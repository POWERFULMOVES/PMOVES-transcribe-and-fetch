# -*- coding: utf-8 -*-
"""
transcribe1.py - Module for Video Transcription Processing

Handles audio download (yt-dlp), transcription using local faster-whisper
or cloud APIs (Groq Whisper endpoint), result formatting, and file saving.
Includes real-time updates via queues (for SSE) and styled terminal output.
"""

import os
# Set environment variables if needed BEFORE importing torch/numpy/etc.
# os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE' # For macOS
# os.environ['OPENBLAS_NUM_THREADS'] = '1'

import asyncio
import pandas as pd
from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Any, Optional, Tuple
import logging
import json
import aiohttp
from fastapi import HTTPException # For raising errors in FastAPI context
import torch
import yt_dlp
from pydub import AudioSegment
import tempfile
import math
import re
from datetime import datetime, timedelta
from pathlib import Path
import time
import argparse # For CLI execution
import sys

# Rich imports for terminal output
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt # For CLI interaction

# --- Logging and Console Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
# Use Rich console for enhanced terminal output
console = Console(force_terminal=True, color_system="auto")

# --- Local Imports ---
try:
    from .utils import (
        clean_filename,
        format_as_hyperlink,
        save_text_to_markdown,
        save_segments_to_csv,
        save_segments_to_excel,
    )
    from .config import (
        WHISPER_MODEL, GROQ_API_KEY, OPENAI_API_KEY # OPENAI key kept as potential alternative
    )
    UTILS_CONFIG_LOADED = True
except ImportError as e:
    logger.error(f"Failed to import local utils/config: {e}", exc_info=True)
    UTILS_CONFIG_LOADED = False
    WHISPER_MODEL = "base"; GROQ_API_KEY = os.getenv("GROQ_API_KEY"); OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    async def save_text_to_markdown(c, p): logger.error(f"Save MD failed: {p}")
    async def save_segments_to_csv(df, p): logger.error(f"Save CSV failed: {p}")
    async def save_segments_to_excel(df, p): logger.error(f"Save Excel failed: {p}")
    def clean_filename(s): return re.sub(r'[\\/*?:"<>|]', '_', s)
    def format_as_hyperlink(url): return url # Fallback

# --- Optional Whisper Import ---
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_LOADED = True
except ImportError:
    WhisperModel = None
    FASTER_WHISPER_LOADED = False
    logger.warning("faster_whisper not found. Local transcription unavailable.")

# --- Device Detection ---
def get_optimal_device() -> Tuple[Literal["cpu", "cuda", "mps"], str]:
    """Detects best device and compute type for faster-whisper."""
    if torch.cuda.is_available():
        capability = torch.cuda.get_device_capability(0)
        compute_type = "float16" if capability >= (7, 0) else "int8"
        return "cuda", compute_type
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        try:
             torch.ones(1, device="mps") # Test MPS
             logger.info("MPS device available and working.")
             return "mps", "float16"
        except Exception as mps_err:
             logger.warning(f"MPS device detected but failed init: {mps_err}. Falling back to CPU.")
             return "cpu", "int8" # Fallback to CPU if MPS fails
    else:
        return "cpu", "int8"

optimal_device, optimal_compute_type = get_optimal_device()
logger.info(f"Optimal device: {optimal_device} | Compute type: {optimal_compute_type}")
if optimal_device == "cuda":
    try: logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)} | Cap: {torch.cuda.get_device_capability(0)}")
    except Exception as e: logger.warning(f"Could not get CUDA info: {e}")

# --- Whisper Model Loader ---
_whisper_model_instance = None
def get_whisper_model():
    """Initializes and returns the faster-whisper model instance (Singleton)."""
    global _whisper_model_instance
    if not FASTER_WHISPER_LOADED: return None
    if _whisper_model_instance is None:
        try:
            logger.info(f"Initializing Whisper: {WHISPER_MODEL} on {optimal_device}({optimal_compute_type})")
            cpu_threads = 0 if optimal_device != "cpu" else os.cpu_count() or 4
            num_workers = 1
            _whisper_model_instance = WhisperModel(
                WHISPER_MODEL, device=optimal_device, compute_type=optimal_compute_type,
                cpu_threads=cpu_threads, num_workers=num_workers,
            )
            logger.info("Whisper model loaded.")
        except Exception as e: logger.error(f"Whisper init failed: {e}", exc_info=True); _whisper_model_instance = None
    return _whisper_model_instance

# --- Pydantic Model ---
class VideoProcessRequest(BaseModel):
    """Request model matching main.py"""
    youtube_video_url: str
    obsidian_dir: str
    output_folder: str
    use_groq: bool = Field(False, description="Use Groq endpoint for transcription")
    transcription_model: str = Field("faster-whisper", description="Model identifier")

# --- Helper Functions ---
def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS.mmm format"""
    if not isinstance(seconds, (int, float)) or seconds < 0: return "00:00:00.000"
    try:
        # Handle potential very small negative numbers from floating point issues
        td = timedelta(seconds=abs(seconds))
        total_seconds = int(td.total_seconds())
        hours, rem = divmod(total_seconds, 3600); minutes, secs = divmod(rem, 60)
        ms = td.microseconds // 1000
        # Return format like 0:00:12.345 or 1:23:45.678
        return f"{hours}:{minutes:02d}:{secs:02d}.{ms:03d}"
    except Exception: return "00:00:00.000"

async def save_to_both_locations(content: Any, filename: str, output_dir: Path, obsidian_dir: Path):
    """Saves content to both output and obsidian dirs based on filename extension."""
    output_path = output_dir / filename; obsidian_path = obsidian_dir / filename
    try: output_dir.mkdir(parents=True, exist_ok=True); obsidian_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e: logger.error(f"Mkdir fail for '{filename}': {e}"); return None, None
    logger.info(f"Saving: {output_path} & {obsidian_path}")
    ext = output_path.suffix.lower(); saved_output = False; saved_obsidian = False
    try:
        if ext == ".csv": df = content if isinstance(content, pd.DataFrame) else pd.DataFrame(content); await save_segments_to_csv(df, str(output_path)); saved_output=True; await save_segments_to_csv(df, str(obsidian_path)); saved_obsidian=True
        elif ext == ".xlsx": df = content if isinstance(content, pd.DataFrame) else pd.DataFrame(content); await save_segments_to_excel(df, str(output_path)); saved_output=True; await save_segments_to_excel(df, str(obsidian_path)); saved_obsidian=True
        elif ext == ".md": md = content if isinstance(content, str) else pd.DataFrame(content).to_markdown(index=False); await save_text_to_markdown(md, str(output_path)); saved_output=True; await save_text_to_markdown(md, str(obsidian_path)); saved_obsidian=True
        else: logger.warning(f"Unsupported save ext: {ext}"); return None, None
        logger.info(f"Saved {filename} OK."); return str(output_path), str(obsidian_path)
    except Exception as e: logger.error(f"Save fail '{filename}': {e}", exc_info=True); return (str(output_path) if saved_output else None), (str(obsidian_path) if saved_obsidian else None)

async def download_audio_utility(youtube_url: str, output_path_template: str, progress_callback=None) -> Optional[str]:
    """Downloads audio using yt-dlp. Returns actual path or None."""
    if not yt_dlp:
        logger.error("yt-dlp library is not installed or imported.")
        return None

    logger.info(f"Downloading audio: {youtube_url} -> {output_path_template}")
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If called from a context without a running loop (less common for FastAPI background tasks)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    output_dir = Path(output_path_template).parent
    filename_base = Path(output_path_template).stem

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create output directory {output_dir}: {e}")
        return None

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(output_dir / f'{filename_base}.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a', # Good quality, widely compatible
            'preferredquality': '192', # Bitrate
        }],
        'quiet': True,
        'no_warnings': True,
        'noprogress': True, # Rely on hooks
        'progress_hooks': []
    }
    last_sent_progress = -10.0 # Initialize to ensure first update (0%) sends

    if progress_callback:
        def sync_hook(d):
            nonlocal last_sent_progress
            if d['status'] == 'downloading':
                try:
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    if total > 0:
                        current_progress = round((downloaded / total) * 100, 1)
                        # Send update at start, end, and roughly every 10%
                        if current_progress == 0 or current_progress >= 100 or abs(current_progress - last_sent_progress) >= 10.0:
                             # Ensure progress_callback is awaitable or handle appropriately
                            if asyncio.iscoroutinefunction(progress_callback):
                                asyncio.run_coroutine_threadsafe(progress_callback(current_progress), loop)
                            else:
                                # If callback is not async, schedule it in loop or run directly (careful!)
                                loop.call_soon_threadsafe(progress_callback, current_progress) # Example for sync callback
                            last_sent_progress = current_progress
                except Exception as e:
                    # Log error without breaking download if hook fails
                    logger.error(f"Error in download progress hook: {e}", exc_info=False)
            elif d['status'] == 'finished':
                # Ensure 100% is sent upon completion
                if asyncio.iscoroutinefunction(progress_callback):
                     asyncio.run_coroutine_threadsafe(progress_callback(100.0), loop)
                else:
                     loop.call_soon_threadsafe(progress_callback, 100.0)

        ydl_opts['progress_hooks'].append(sync_hook)

    # Main download execution block
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Run the blocking download call in a separate thread
            await loop.run_in_executor(None, lambda: ydl.download([youtube_url]))

        # Postprocessor should have created the .m4a file
        actual_path = output_dir / f"{filename_base}.m4a"
        if not actual_path.is_file():
            logger.error(f"Expected audio file not found after download: {actual_path}")
            # You might want to check for other possible extensions if ffmpeg failed, but m4a is expected
            return None

        logger.info(f"Audio downloaded successfully to: {actual_path}")
        return str(actual_path)

    # Add the except block at the same level as the try
    except Exception as e:
        logger.error(f"Error during yt-dlp download or processing: {e}", exc_info=True)
        return None

def format_sse_message(type: str, content: Any, metadata: Optional[dict] = None) -> str:
     """Helper to format messages for Server-Sent Events"""
     message = {"type": type, "content": content, "timestamp": datetime.now().isoformat()}
     if metadata: message["metadata"] = metadata
     try: json_str = json.dumps(message); return f"data: {json_str}\n\n"
     except TypeError as e: logger.error(f"SSE JSON Error ({type}): {e}. Content: {str(content)[:100]}", exc_info=False); return f"data: {json.dumps({'type': 'error', 'content': 'Serialization fail', 'timestamp': datetime.now().isoformat()})}\n\n"

# --- Status Update Helper ---
async def send_and_print_status(queue: asyncio.Queue, message: str, level: str = "info"):
    """Sends status to queue (for frontend) AND prints styled message to console."""
    await queue.put(format_sse_message("status", message))
    prefix_map = {"info": "[cyan]STATUS[/cyan]: ", "error": "[bold red]ERROR[/bold red]: ", "warn": "[yellow]WARN[/yellow]: ", "complete": "[bold green]COMPLETE[/bold green]: "}
    prefix = prefix_map.get(level, "[grey50]STATUS[/grey50]: ")
    if 'console' in globals(): console.print(f"{prefix}{message}")
    else: print(f"[{level.upper()}] {message}")

# --- Main Processing Function ---
async def process_video(
    youtube_video_url: str,
    obsidian_dir: str,
    status_queue: asyncio.Queue,
    transcription_queue: asyncio.Queue,
    output_folder: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None
):
    """Orchestrates video processing: download, transcribe, save. Includes console output."""
    start_time_process = time.time(); video_id = "unknown"; obsidian_dir_path = Path(obsidian_dir).resolve(); output_folder_path = Path(output_folder or Path.cwd()/"output").resolve()
    try:
        if not UTILS_CONFIG_LOADED: raise RuntimeError("Utils/config missing.")
        if not model_config: model_config = {"use_groq": False, "transcription_model": "faster-whisper"}
        use_groq_api = model_config.get("use_groq", False)
        model_identifier = model_config.get("transcription_model", "faster-whisper")

        await send_and_print_status(status_queue, f"Processing request for {youtube_video_url}...")
        await send_and_print_status(status_queue, "Extracting video information...")
        video_info = await extract_video_info(youtube_video_url)
        video_id = video_info.get('id', 'unknown_id'); clean_title = clean_filename(video_info.get('title', 'untitled'))
        logger.info(f"Processing Video: {video_info.get('title', 'N/A')} (ID: {video_id})")

        model_prefix = "groq" if use_groq_api else "local"
        specific_model_name = clean_filename(model_identifier) if model_identifier != "faster-whisper" else None
        if specific_model_name: model_prefix += f"_{specific_model_name}"
        base_filename = f"{model_prefix}_{clean_title}_{video_id}"

        subdirs={"audio":"audio","csv":"csv","excel":"excel","md":"md"}; output_paths={k: output_folder_path/v for k,v in subdirs.items()}; obsidian_paths={k: obsidian_dir_path/v for k,v in subdirs.items()}
        for path in list(output_paths.values()) + list(obsidian_paths.values()): path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output dirs ensured: {output_folder_path} & {obsidian_dir_path}")

        audio_filename_base = f"{base_filename}_audio"; audio_output_path_template = str(output_paths["audio"] / audio_filename_base)
        async def dl_prog(p):
            status_msg = "Downloading audio..." if p<100 else "Audio download complete."
            await status_queue.put(format_sse_message("progress", {"status": status_msg, "percentage": p}))
            if p == 0 or p >= 100: await send_and_print_status(status_queue, status_msg)
        actual_audio_path = await download_audio_utility(youtube_video_url, audio_output_path_template, dl_prog)
        if not actual_audio_path: raise FileNotFoundError("Audio download failed.")

        segments: List[Dict[str, Any]] = []; full_text_md: str = ""
        if use_groq_api:
            if not GROQ_API_KEY: raise ValueError("GROQ_API_KEY needed.")
            groq_model = specific_model_name or "distil-whisper-large-v3-en"
            segments, full_text_md = await process_audio_with_groq(actual_audio_path, status_queue, transcription_queue, youtube_video_url, model_name=groq_model)
        else:
            if not FASTER_WHISPER_LOADED: raise RuntimeError("faster_whisper not installed.")
            # Pass model_identifier if needed for local model selection logic in transcribe_audio/get_whisper_model
            segments, full_text_md = await transcribe_audio(actual_audio_path, status_queue, transcription_queue, youtube_video_url)

        if not segments: raise ValueError("Transcription returned no segments.")

        await send_and_print_status(status_queue, "Saving transcription files...")
        df = pd.DataFrame(segments)
        save_tasks = [ save_to_both_locations(df, f"{base_filename}_transcript.csv", output_paths["csv"], obsidian_paths["csv"]),
                       save_to_both_locations(df, f"{base_filename}_transcript.xlsx", output_paths["excel"], obsidian_paths["excel"]),
                       save_to_both_locations(full_text_md, f"{base_filename}_transcript.md", output_paths["md"], obsidian_paths["md"]), ]
        save_results = await asyncio.gather(*save_tasks)
        saved_log = {ft:{"out":str(p[0] or 'FAIL'),"obs":str(p[1] or 'FAIL')} for ft, p in zip(["csv","excel","md"], save_results)}; logger.info(f"Save results: {saved_log}")

        total_duration = time.time()-start_time_process; completion_msg = f"'{clean_title}' ({model_prefix}) processed in {total_duration:.2f}s."
        await send_and_print_status(status_queue, completion_msg, level="complete")
        await status_queue.put(format_sse_message("complete", {"message":completion_msg,"video_id":video_id,"title":clean_title,"files":{"audio":Path(actual_audio_path).name,"csv":f"{base_filename}_transcript.csv","excel":f"{base_filename}_transcript.xlsx","markdown":f"{base_filename}_transcript.md"}, "output_base":str(output_folder_path),"obsidian_base":str(obsidian_dir_path)}))
        return {"status": "completed", "files": saved_log}

    except Exception as e:
        error_msg = f"Failed processing '{video_id}': {e}"; logger.error(error_msg, exc_info=True)
        await send_and_print_status(status_queue, error_msg, level="error")
        raise HTTPException(status_code=500, detail=error_msg) from e

# --- Local Transcription (faster-whisper) ---
async def transcribe_audio(
    audio_path: str, status_queue: asyncio.Queue, transcription_queue: asyncio.Queue,
    youtube_video_url: str
):
    """Transcribes audio locally, queues results, and prints styled output."""
    if not os.path.exists(audio_path): raise FileNotFoundError(f"Audio file not found: {audio_path}")
    await send_and_print_status(status_queue, "Loading local Whisper model...")
    model = get_whisper_model();
    if model is None: raise RuntimeError("Failed to load local Whisper model.")
    await send_and_print_status(status_queue, f"Starting local transcription ({WHISPER_MODEL})...")

    result_segments: List[Dict[str, Any]] = []; full_text_md_lines: List[str] = []
    video_id = youtube_video_url.split('v=')[1].split('&')[0] if 'v=' in youtube_video_url else 'unknown_id'
    try: audio_duration_s = AudioSegment.from_file(audio_path).duration_seconds
    except Exception as dur_err: logger.warning(f"Could not get audio duration: {dur_err}"); audio_duration_s = 3600.0
    estimated_total = int(audio_duration_s)

    # --- Run blocking transcription in thread ---
    segments_gen, info = await asyncio.to_thread(model.transcribe, audio_path, beam_size=5, vad_filter=True, word_timestamps=False)
    logger.info(f"Local transcription info: Lang={info.language} Prob={info.language_probability:.2f}")

    with Progress(SpinnerColumn(), TextColumn("[blue]{task.description}"), BarColumn(bar_width=None), TextColumn("[green]{task.percentage:>3.0f}%"), TimeElapsedColumn(), console=console, transient=True) as progress:
        task_id = progress.add_task("[cyan]Transcribing...", total=estimated_total)
        processed_time_s = 0.0; segment_index = 0

        for segment in segments_gen:
            segment_index += 1; processed_time_s = segment.end
            progress.update(task_id, completed=min(int(processed_time_s), estimated_total), description=f"Processing {format_timestamp(processed_time_s)}")

            segment_text = segment.text.strip(); start_time = format_timestamp(segment.start); end_time = format_timestamp(segment.end)
            timestamp_seconds = int(segment.start); watch_url = f"https://www.youtube.com/watch?v={video_id}&t={timestamp_seconds}s" # CORRECTED

            segment_dict = {'watch_url': format_as_hyperlink(watch_url) if UTILS_CONFIG_LOADED else watch_url, 'video_id': video_id, 'id': segment_index, 'start': start_time, 'end': end_time, 'text': segment_text }
            result_segments.append(segment_dict)
            md_line = f"| [{start_time}]({watch_url}) | {video_id} | {segment_index} | {start_time} | {end_time} | {segment_text.replace('|', '\|')} |"; full_text_md_lines.append(md_line)

            await transcription_queue.put(format_sse_message("transcription_segment", segment_dict)) # Send to queue
            if segment_index % 20 == 0: await status_queue.put(format_sse_message("status", f"Processed segment {segment_index} up to {start_time}"))

            # --- ALWAYS Print Styled Output to Console ---
            confidence_str = ""; prob=0.0
            if hasattr(segment, 'avg_logprob'): prob = math.exp(segment.avg_logprob); color="green" if prob>0.7 else "yellow" if prob>0.4 else "red"; confidence_str=f"[grey50]Conf:[/{color}] {prob:.2f}[/{color}][/grey50]"
            panel = Panel(f"{segment_text}", title=f"[bold green]💻 Seg {segment_index}[/bold green] {confidence_str}", subtitle=f"[yellow]{start_time} -> {end_time}[/yellow] [blue][link={watch_url}]Watch[/link][/blue]", border_style="dim green", padding=(0,1))
            console.print(panel)

            await asyncio.sleep(0) # Yield control

        progress.update(task_id, completed=estimated_total, description="Finalizing...")

    title = f"# Transcription: [{clean_filename(video_id)}]({youtube_video_url})\n\n"; table_header = "| Watch URL | Video ID | Seg ID | Start | End | Text |\n|---|---|---|---|---|---|\n"
    full_text_md = title + table_header + "\n".join(full_text_md_lines)
    await transcription_queue.put(format_sse_message("transcription_complete", {"text": full_text_md}))
    await send_and_print_status(status_queue, f"Local transcription complete. Segments: {len(result_segments)}", level="complete") # Use helper
    return result_segments, full_text_md


# --- Cloud Transcription (Groq) ---
async def process_audio_with_groq(
    audio_file_path: str, status_queue: asyncio.Queue, transcription_queue: asyncio.Queue,
    youtube_video_url: str, chunk_duration_ms: int = 600*1000, model_name: str = "distil-whisper-large-v3-en"
) -> tuple[List[Dict[str, Any]], str]:
    """Processes audio via Groq Whisper API, queues results, prints styled output."""
    if not GROQ_API_KEY: raise ValueError("GROQ_API_KEY not configured.")
    if not os.path.exists(audio_file_path): raise FileNotFoundError(f"Audio not found: {audio_file_path}")

    await send_and_print_status(status_queue, f"Starting Groq cloud transcription ({model_name})...") # Use helper
    audio = AudioSegment.from_file(audio_file_path); total_duration_ms = len(audio); total_chunks = math.ceil(total_duration_ms/chunk_duration_ms)
    segments: List[Dict[str, Any]] = []; full_text_md_lines: List[str] = []
    video_id = youtube_video_url.split('v=')[1].split('&')[0] if 'v=' in youtube_video_url else 'unknown_id'
    temp_files = []

    try:
        async with aiohttp.ClientSession() as session:
            for i in range(total_chunks):
                chunk_num = i + 1; start_ms = i * chunk_duration_ms; end_ms = min((i + 1) * chunk_duration_ms, total_duration_ms)
                await send_and_print_status(status_queue, f"Preparing chunk {chunk_num}/{total_chunks} for Groq...") # Use helper
                chunk = audio[start_ms:end_ms]
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    chunk_path = temp_file.name; temp_files.append(chunk_path)
                    try: chunk.export(chunk_path, format='mp3', bitrate="128k"); logger.debug(f"Exported chunk {chunk_num}: {chunk_path}")
                    except Exception as ex_err: logger.error(f"Export chunk {chunk_num} fail: {ex_err}"); await send_and_print_status(status_queue, f"Export chunk {chunk_num} fail", "error"); continue
                if os.path.getsize(chunk_path)/(1024*1024) > 24.5: logger.warning(f"Chunk {chunk_num}>24.5MB. Skip."); await send_and_print_status(status_queue, f"Chunk {chunk_num} too large, skip.", "warn"); continue

                try:
                    await send_and_print_status(status_queue, f"Uploading chunk {chunk_num}/{total_chunks} to Groq...") # Use helper
                    form = aiohttp.FormData()
                    with open(chunk_path, 'rb') as f_rb: # Ensure file is closed
                        form.add_field('file', f_rb, filename='chunk.mp3', content_type='audio/mp3')
                        form.add_field('model', model_name); form.add_field('response_format', 'verbose_json'); form.add_field('language', 'en')
                        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}; groq_url = "https://api.groq.com/openai/v1/audio/transcriptions"
                        logger.info(f"Sending chunk {chunk_num} to Groq API...")
                        async with session.post(groq_url, data=form, headers=headers, timeout=aiohttp.ClientTimeout(total=600)) as response:
                            if response.status != 200: error_text = await response.text(); raise Exception(f"Groq API Error {response.status}: {error_text}")
                            result = await response.json(); logger.info(f"Groq response chunk {chunk_num} OK.")

                    current_chunk_segments = [] # Collect for console print
                    if 'segments' in result:
                        for segment_data in result['segments']:
                            segment_index = len(segments) + 1; segment_start = segment_data['start']+(start_ms/1000.0); segment_end = segment_data['end']+(start_ms/1000.0)
                            segment_text = segment_data['text'].strip(); timestamp_seconds = int(segment_start); watch_url = f"https://www.youtube.com/watch?v={video_id}&t={timestamp_seconds}s" # CORRECTED
                            segment_dict = {'watch_url': format_as_hyperlink(watch_url) if UTILS_CONFIG_LOADED else watch_url, 'video_id': video_id, 'id': segment_index, 'start': format_timestamp(segment_start), 'end': format_timestamp(segment_end), 'text': segment_text}
                            segments.append(segment_dict); current_chunk_segments.append(segment_dict)
                            md_line = f"| [{segment_dict['start']}]({watch_url}) | {video_id} | {segment_index} | {segment_dict['start']} | {segment_dict['end']} | {segment_text.replace('|','\|')} |"; full_text_md_lines.append(md_line)
                            await transcription_queue.put(format_sse_message("transcription_segment", segment_dict)) # Send to queue
                    else: # Fallback
                         full_chunk_text = result.get('text','').strip(); start_time_s=start_ms/1000.0; end_time_s=end_ms/1000.0
                         if full_chunk_text:
                              segment_index=len(segments)+1; timestamp_seconds=int(start_time_s); watch_url=f"https://www.youtube.com/watch?v={video_id}&t={timestamp_seconds}s" # CORRECTED
                              segment_dict = {'watch_url': format_as_hyperlink(watch_url) if UTILS_CONFIG_LOADED else watch_url, 'video_id': video_id, 'id': segment_index, 'start': format_timestamp(start_time_s), 'end': format_timestamp(end_time_s), 'text': full_chunk_text }
                              segments.append(segment_dict); current_chunk_segments.append(segment_dict)
                              md_line = f"| [{segment_dict['start']}]({watch_url}) | {video_id} | {segment_index} | {segment_dict['start']} | {segment_dict['end']} | {full_chunk_text.replace('|','\|')} |"; full_text_md_lines.append(md_line)
                              await transcription_queue.put(format_sse_message("transcription_segment", segment_dict)) # Send to queue
                         logger.warning(f"Groq chunk {chunk_num} lacked segments.")

                    # --- ALWAYS Print Console Output for this Chunk ---
                    if current_chunk_segments:
                        console.print(f"--- Groq Chunk {chunk_num}/{total_chunks} Results ---", style="dim blue") # Header for clarity
                        for seg_dict in current_chunk_segments:
                            panel = Panel(f"{seg_dict['text']}", title=f"[bold blue]☁️ Seg {seg_dict['id']}[/bold blue]", subtitle=f"[yellow]{seg_dict['start']} -> {seg_dict['end']}[/yellow] [blue][link={seg_dict['watch_url']}]Watch[/link][/blue]", border_style="dim blue", padding=(0,1))
                            console.print(panel) # Print EVERY segment panel

                except Exception as api_err:
                    error_msg = f"Groq API error chunk {chunk_num}: {api_err}"
                    logger.error(error_msg, exc_info=True)
                    await send_and_print_status(status_queue, error_msg, level="error") # Use helper
                    raise # Fail fast

                await asyncio.sleep(0.5) # Optional delay

        # --- Final Assembly ---
        if not segments: raise ValueError("Groq transcription failed (no segments).")
        title = f"# Transcription: [{clean_filename(video_id)}]({youtube_video_url})\n\n"; table_header = "| Watch URL | Video ID | Seg ID | Start | End | Text |\n|---|---|---|---|---|---|\n"
        full_text_md = title + table_header + "\n".join(full_text_md_lines)
        await transcription_queue.put(format_sse_message("transcription_complete", {"text": full_text_md}))
        await send_and_print_status(status_queue, "Groq transcription completed.", level="complete") # Use helper
        return segments, full_text_md

    finally: # Cleanup temp files
        logger.debug(f"Cleaning up {len(temp_files)} temp files...");
        for f_path in temp_files:
            try: os.remove(f_path)
            except Exception as e: logger.warning(f"Failed cleanup {f_path}: {e}")

# --- yt-dlp Info Extraction ---
async def extract_video_info(youtube_video_url: str) -> Dict[str, Any]:
    """Extracts detailed video metadata using yt-dlp."""
    if not yt_dlp: raise RuntimeError("yt-dlp is not installed.")
    logger.info(f"Extracting info for {youtube_video_url}")
    # Avoid extracting subtitle data here if it slows things down; can be done during download if needed.
    ydl_opts={'quiet':True,'no_warnings':True,'skip_download':True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(youtube_video_url, download=False))
        if not info: raise ValueError("yt-dlp failed to extract info.")
        info['webpage_url'] = info.get('webpage_url', youtube_video_url); return info
    except Exception as e: logger.error(f"Info extraction error: {e}", exc_info=True); raise ValueError(f"Info extraction fail: {e}") from e

# --- CLI Execution Block ---
async def run_transcription_cli(args):
    """Runs the transcription process with console output when script is run directly."""
    # Use a distinct download dir for CLI to avoid conflicts with server downloads
    DOWNLOAD_DIR = "downloads_cli"; Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
    video_id, safe_title = None, None
    try:
        console.print(f"Fetching info for: [link={args.video_url}]{args.video_url}[/link]")
        with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
            info = ydl.extract_info(args.video_url, download=False)
            video_id = info.get('id', 'unknown_id'); safe_title = clean_filename(info.get('title', 'untitled'))
            console.print(f"Processing: [bold]{safe_title}[/] (ID: {video_id})")
    except Exception as e: console.print(f"[bold red]Info Error:[/bold red] {e}"); return

    audio_filename_base = Path(DOWNLOAD_DIR) / f"{safe_title}_{video_id}"
    output_file = Path(f"{args.output or safe_title}.{args.format}")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Dummy queues are sufficient as functions now print directly to console
    dummy_q = asyncio.Queue()

    console.print("Downloading audio...")
    actual_audio_path = await download_audio_utility(args.video_url, str(audio_filename_base))
    if not actual_audio_path: console.print("[bold red]Audio download failed.[/bold red]"); return
    # Audio download success status is printed inside the utility or the main process now

    console.print("-" * console.width); results = None; info = None; start_time = time.time()

    # Call transcription function (it will print panels internally now)
    try:
        if args.use_groq:
            groq_model_cli = args.model or "distil-whisper-large-v3-en"
            if not GROQ_API_KEY: console.print("[bold red]GROQ_API_KEY missing![/bold red]"); return
            # Status is printed inside the function
            results, info = await process_audio_with_groq(actual_audio_path, dummy_q, dummy_q, args.video_url, model_name=groq_model_cli)
        else:
            local_model_cli = args.model or WHISPER_MODEL
            if not FASTER_WHISPER_LOADED: console.print("[bold red]faster_whisper missing![/bold red]"); return
            # Status is printed inside the function
            # TODO: Adapt get_whisper_model if CLI needs to specify size dynamically based on args.model
            results, info = await transcribe_audio(actual_audio_path, dummy_q, dummy_q, args.video_url)
    except Exception as cli_transcribe_err:
         console.print(f"[bold red]Transcription Execution Error:[/bold red] {cli_transcribe_err}")
         logger.error("Transcription failed in CLI mode.", exc_info=True)
         results = None # Ensure results is None on error


    end_time = time.time(); console.print("-" * console.width) # Separator after transcription finishes

    if results:
        # Final status is printed by the transcription functions now
        console.print(f"Total transcription duration: {end_time - start_time:.2f}s.")
        # Basic saving for CLI demonstration
        try:
            with open(str(output_file), 'w', encoding='utf-8') as f:
                if args.format == 'json': json.dump(results, f, indent=2, ensure_ascii=False)
                else: # Basic TXT format
                    f.write(f"# Transcription: {safe_title} ({video_id})\n\n")
                    f.write("\n".join([f"[{res['start']} -> {res['end']}] {res['text']}" for res in results]))
            console.print(f"Basic transcript saved to '{output_file}' (format: {args.format})")
        except Exception as e: console.print(f"[red]Error saving transcript: {e}[/red]")
    else:
        console.print("[bold red]Transcription failed (no results generated).[/bold red]")

    # Cleanup (Optional)
    # try: os.remove(actual_audio_path) except OSError as e: console.print(f"[yellow]Cleanup Error: {e}[/yellow]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe YT audio via local Whisper or Groq API.")
    parser.add_argument("video_url", help="URL of the YouTube video.")
    parser.add_argument("-o", "--output", help="Output file name (without ext). Defaults to video title.")
    parser.add_argument("-f", "--format", choices=['txt', 'json'], default='txt', help="Output format (basic save). Default: txt")
    parser.add_argument("--use-groq", action="store_true", help="Use Groq API instead of local Whisper.")
    parser.add_argument("-m", "--model", help="Specify model (e.g., 'base' for local, 'distil-whisper-large-v3-en' for Groq). Overrides default.")

    args = parser.parse_args()
    try: asyncio.run(run_transcription_cli(args))
    except KeyboardInterrupt: console.print("\n[yellow]Operation cancelled.[/yellow]")
    except Exception as main_err: console.print(f"\n[bold red]Error:[/bold red] {main_err}"); logger.error("CLI failed.", exc_info=True); sys.exit(1)