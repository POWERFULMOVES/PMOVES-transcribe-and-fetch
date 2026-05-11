# --- START OF REFACTORED Transcribe1.py ---

import os
# Environment variables recommended to be set before importing torch/numpy
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OPENBLAS_NUM_THREADS'] = '1'

import asyncio
import pandas as pd
import math
from faster_whisper import WhisperModel
from pydantic import BaseModel
# Assuming these utils exist and are correctly implemented in '.utils'
# Make sure they use async file I/O (like aiofiles) if needed for save functions
from .general_utils import (
    clean_filename,
    format_as_hyperlink, # Note: This wasn't used in the final markdown format, but kept import
    ensure_directory_exists,
    # download_audio is defined below for clarity, assuming it was in utils
    save_text_to_markdown,
    save_segments_to_csv,
    save_segments_to_excel,
    format_timestamp # Defined below for clarity, assuming it was in utils
)
# Assuming configuration variables are correctly set in '.config' and LLM registry service is available
from .app_config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE, GROQ_API_KEY, WORKSPACE_ROOT, SUBFOLDERS
from .utils.llm_registry_service import get_llm_registry_service # Import the getter function
import logging
import json
import aiohttp # Keep for potential future API integrations
from fastapi import HTTPException # Keep if parts integrate with FastAPI elsewhere
import torch
from typing import Literal, List, Tuple, Dict, Any, Optional # Added Optional
import yt_dlp
# from pydub import AudioSegment # Commented out - only used in removed chunking function
# import tempfile # Commented out - only used in removed chunking function
import math # Keep for potential future calculations
import re
from datetime import datetime, timedelta # Added timedelta
import time # Needed for time.sleep in sync loop and timing

# Rich imports for optional enhanced console output
try:
    from rich.console import Console
    # Removed Progress imports as direct integration with to_thread is complex
    # Rely on queue messages for progress reporting
    console = Console()
    RICH_AVAILABLE = True
    print("Rich console is available.")
except ImportError:
    # Basic fallback if rich is not installed
    class Console:
        def print(self, *args, **kwargs): print(*args)
    console = Console()
    RICH_AVAILABLE = False
    print("Rich console not found, using standard print.")


# --- Logging Setup ---
# Configure logging basic setup (consider moving to a central setup in main app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Get logger instance for this module


# --- Device and Model Configuration ---

def get_optimal_device() -> tuple[Literal["cpu", "cuda"], Literal["int8", "float16", "int8_float16"]]:
    """Determines the best device (CUDA or CPU) and compute type."""
    if torch.cuda.is_available():
        # Check CUDA capability for float16 support if needed, default to float16 for CUDA
        # cap = torch.cuda.get_device_capability(0)
        # compute_type = "float16" if cap[0] >= 7 else "int8_float16" # Example capability check
        return "cuda", "float16" # Defaulting to float16 for simplicity if CUDA found
    # Add MPS check if relevant for target hardware
    # elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
    #     logger.info("MPS device detected.")
    #     return "mps", "float16"
    else:
        return "cpu", "int8" # Default to int8 for CPU for broader compatibility

optimal_device, optimal_compute_type = get_optimal_device()

# Log device info at startup
logger.info(f"--- System Info ---")
logger.info(f"Selected Whisper model size: {WHISPER_MODEL}")
logger.info(f"CUDA available: {torch.cuda.is_available()}")
logger.info(f"Determined optimal device: '{optimal_device}' with compute type: '{optimal_compute_type}'")
if optimal_device == "cuda":
    try:
        logger.info(f"GPU Device Name: {torch.cuda.get_device_name(0)}")
        props = torch.cuda.get_device_properties(0)
        logger.info(f"GPU Memory: {props.total_memory / 1024**3:.2f} GB")
        logger.info(f"CUDA Device Capability: {torch.cuda.get_device_capability(0)}")
        logger.info(f"CUDA Device Count: {torch.cuda.device_count()}")
    except Exception as e:
        logger.error(f"Could not get detailed CUDA device info: {e}")
logger.info(f"--- End System Info ---")


# --- Whisper Model Initialization (Lazy Loading) ---
_whisper_model_instance: Optional[WhisperModel] = None

def get_whisper_model() -> WhisperModel:
    """Gets or initializes the Whisper model instance. Ensures it's loaded only once."""
    global _whisper_model_instance
    if _whisper_model_instance is None:
        # Use the globally determined optimal device and compute type
        device_to_use = optimal_device # e.g., "cuda" or "cpu"
        # Ensure compute_type is appropriate for the device
        compute_to_use = optimal_compute_type if device_to_use == "cuda" else "int8"

        logger.info(f"Initializing Whisper model '{WHISPER_MODEL}' on device='{device_to_use}' with compute_type='{compute_to_use}'...")
        console.print(f"[yellow]Initializing Whisper model '{WHISPER_MODEL}' (this might take a moment)...[/yellow]")
        try:
            # Adjust threads/workers based on your system and use case
            # More cpu_threads can help preprocessing on CPU even if using GPU
            # num_workers often benefits from being > 1 for parallel batch processing if applicable
            _whisper_model_instance = WhisperModel(
                WHISPER_MODEL,
                device=device_to_use,
                compute_type=compute_to_use,
                cpu_threads=os.cpu_count() or 4, # Use more threads if available
                num_workers=1, # Often 1 is fine for single sequential transcription
                # download_root=None, # Default location okay?
                # local_files_only=False # Allow download if needed
            )
            logger.info("Whisper model initialized successfully.")
            console.print("[green]Whisper model loaded.[/green]")
        except Exception as e:
            logger.error(f"FATAL: Failed to initialize Whisper model: {e}", exc_info=True)
            console.print(f"[bold red]Error initializing Whisper model: {e}[/bold red]")
            # This is critical, so raise an exception to stop the process if the model fails
            raise RuntimeError(f"Whisper model initialization failed: {e}")
    return _whisper_model_instance


# --- Pydantic Model ---
class VideoProcessRequest(BaseModel): # Matches definition in main.py or caller
    youtube_video_url: str
    obsidian_dir: str
    output_folder: str
    use_groq: bool = False # Should be determined by transcription_model in caller's logic
    transcription_model: str = "faster-whisper" # Default value
    target_language: Optional[str] = None
    task: Literal["transcribe", "translate"] = "transcribe"


# --- Utility Functions (Copied from provided code for completeness) ---

# Assume these save functions are async and correctly implemented in .utils
# Example placeholder if they were defined here:
# async def save_text_to_markdown(content, path): ...
# async def save_segments_to_csv(df, path): ...
# async def save_segments_to_excel(df, path): ...

async def save_to_both_locations(content: Any, filename: str, output_folder: str, obsidian_dir: str, is_markdown: bool = False):
    """ Saves content to both output_folder and obsidian_dir (as CSV or MD). """
    # Ensure target directories exist before saving
    await ensure_directory_exists(output_folder)
    await ensure_directory_exists(obsidian_dir)

    output_path = os.path.join(output_folder, filename)
    obsidian_path = os.path.join(obsidian_dir, filename)
    logger.info(f"Attempting to save to output path: {output_path}")
    logger.info(f"Attempting to save to obsidian path: {obsidian_path}")

    try:
        if is_markdown:
            # Assumes save_text_to_markdown is async
            await save_text_to_markdown(content, output_path)
            await save_text_to_markdown(content, obsidian_path)
            logger.info(f"Saved Markdown successfully: {filename}")
        else: # Assume CSV/Excel for non-markdown (DataFrame expected)
            df = None
            if isinstance(content, pd.DataFrame):
                df = content
            elif isinstance(content, list) and all(isinstance(item, dict) for item in content):
                 logger.info(f"Converting list of {len(content)} dicts to DataFrame for saving.")
                 df = pd.DataFrame(content)
            else:
                 logger.warning(f"Cannot save content of type {type(content)} as CSV/Excel. Needs DataFrame or list of dicts. Skipping save for '{filename}'.")
                 return None, None # Indicate failure

            # Determine file type and save
            if filename.endswith('.csv'):
                # Assumes save_segments_to_csv is async
                await save_segments_to_csv(df, output_path)
                await save_segments_to_csv(df, obsidian_path)
                logger.info(f"Saved CSV successfully: {filename}")
            elif filename.endswith('.xlsx'):
                # Assumes save_segments_to_excel is async
                await save_segments_to_excel(df, output_path)
                await save_segments_to_excel(df, obsidian_path)
                logger.info(f"Saved Excel successfully: {filename}")
            else:
                logger.warning(f"Unsupported file extension for DataFrame saving: {filename}. Skipping.")
                return None, None

        return output_path, obsidian_path
    except Exception as e:
        logger.error(f"Error saving file '{filename}' to locations '{output_path}' and '{obsidian_path}': {e}", exc_info=True)
        # Optionally send an error status via queue if available in this context
        return None, None # Indicate failure

def get_best_thumbnail(thumbnails: Optional[List[Dict[str, Any]]]) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """ Gets the highest resolution thumbnail URL and dimensions. Handles potential None input. """
    if not thumbnails: return None, None, None
    try:
        # Filter out entries without width/height for sorting
        valid_thumbnails = [t for t in thumbnails if t.get('width') and t.get('height')]
        if not valid_thumbnails:
             # If no dimensions, fallback to the last thumbnail URL (often highest res)
             return thumbnails[-1].get('url'), None, None

        # Sort by area (width * height)
        sorted_thumbnails = sorted(
            valid_thumbnails,
            key=lambda x: x['width'] * x['height'],
            reverse=True
        )
        best = sorted_thumbnails[0]
        return best.get('url'), best.get('width'), best.get('height')
    except Exception as e:
        logger.warning(f"Error processing thumbnails: {e}. Using first available URL as fallback.")
        # Fallback to the very first thumbnail URL if sorting fails
        return thumbnails[0].get('url'), None, None

def format_timestamp(seconds: float) -> str:
    """ Convert seconds to HH:MM:SS format without milliseconds """
    if seconds < 0: seconds = 0 # Handle potential negative start times
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

async def extract_video_info(youtube_video_url: str) -> Dict[str, Any]:
    """ Extracts detailed video information using yt-dlp. """
    logger.info(f"Attempting to extract video info for: {youtube_video_url}")
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True, # We only want metadata
            'extract_flat': False, # Get detailed info, not just URL list
            # Consider adding options for subtitles/chapters if needed later
            # 'writesubtitles': True,
            # 'writeautomaticsub': True, # Auto-generated captions
            # 'listsubtitles': True,
        }
        loop = asyncio.get_running_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Run blocking IO in executor thread
            info = await loop.run_in_executor(
                None, lambda: ydl.extract_info(youtube_video_url, download=False)
            )

        if not info:
            raise ValueError("yt-dlp returned no information for the URL.")

        # --- Process extracted info ---
        video_id = info.get('id', 'N/A')
        logger.info(f"Successfully extracted info for video ID: {video_id}")

        thumbnail_url, thumb_width, thumb_height = get_best_thumbnail(info.get('thumbnails'))
        duration_sec = info.get('duration')
        duration_str = str(timedelta(seconds=int(duration_sec))) if duration_sec else "N/A"
        upload_date_str = info.get('upload_date') # YYYYMMDD format
        formatted_upload_date = f"{upload_date_str[:4]}-{upload_date_str[4:6]}-{upload_date_str[6:]}" if upload_date_str and len(upload_date_str) == 8 else "N/A"

        video_info = {
            'id': video_id,
            'title': info.get('title', 'N/A'),
            'description': info.get('description'),
            'duration': duration_sec, # Raw seconds
            'duration_formatted': duration_str, # HH:MM:SS format
            'view_count': info.get('view_count'),
            'like_count': info.get('like_count'),
            'channel': info.get('channel', info.get('uploader', 'N/A')), # Fallback uploader
            'channel_id': info.get('channel_id'),
            'channel_url': info.get('channel_url'),
            'upload_date': formatted_upload_date, # Formatted YYYY-MM-DD
            'raw_upload_date': upload_date_str, # Original YYYYMMDD
            'best_thumbnail': { 'url': thumbnail_url, 'width': thumb_width, 'height': thumb_height },
            'watch_url': info.get('webpage_url', youtube_video_url), # Use original URL as fallback
            'tags': info.get('tags', []),
            'categories': info.get('categories', []),
            # Add more fields as needed (e.g., chapters, subtitles if extracted)
            # 'chapters': info.get('chapters'),
        }
        return video_info

    except yt_dlp.utils.DownloadError as dle:
         # Handle specific yt-dlp errors (e.g., video unavailable, private)
         logger.error(f"yt-dlp download error for {youtube_video_url}: {dle}", exc_info=True)
         raise ValueError(f"Video not accessible or private: {dle}")
    except Exception as e:
        logger.error(f"Generic error extracting video info for {youtube_video_url}: {e}", exc_info=True)
        # Re-raise a generic error or a specific one if identifiable
        raise ValueError(f"Failed to extract video info: {e}")


async def download_audio(youtube_url: str, output_template: str, progress_callback=None):
    """
    Downloads audio using yt-dlp, preferring 'm4a'.
    Returns the actual path of the downloaded file.
    `output_template` should include '%(ext)s'.
    """
    logger.info(f"Starting audio download for: {youtube_url}")
    output_dir = os.path.dirname(output_template)
    await ensure_directory_exists(output_dir) # Ensure directory exists first

    actual_download_path = None # Variable to store the final path

    try:
        loop = asyncio.get_running_loop()

        # --- Progress Hook Setup ---
        last_progress_sent_local = -10.0 # Track progress for this specific download

        def sync_progress_hook(d):
            nonlocal last_progress_sent_local, actual_download_path # Allow modification
            status = d.get('status')

            if status == 'finished':
                actual_download_path = d.get('filename') # Store the final filename from yt-dlp
                logger.info(f"Download hook: status 'finished'. Final path reported: {actual_download_path}")
                # Ensure 100% is sent on completion if callback exists
                if progress_callback and last_progress_sent_local < 100.0:
                    logger.info(f"Download complete: 100%")
                    # Use run_coroutine_threadsafe as hook might be called from ytdlp's thread
                    asyncio.run_coroutine_threadsafe(progress_callback(100.0), loop)

            elif status == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0 and progress_callback:
                    current_progress = round((downloaded / total) * 100, 1)
                    # Send updates more frequently (e.g., every 2%)
                    if abs(current_progress - last_progress_sent_local) >= 2.0:
                        logger.info(f"Download progress: {current_progress:.1f}% ({downloaded/(1024*1024):.1f}MB/{total/(1024*1024):.1f}MB)")
                        # Use run_coroutine_threadsafe for thread safety
                        asyncio.run_coroutine_threadsafe(progress_callback(current_progress), loop)
                        last_progress_sent_local = current_progress

            elif status == 'error':
                logger.error(f"Download hook: status 'error'. Info: {d}")


        # --- yt-dlp Options ---
        ydl_opts = {
            'format': 'm4a/bestaudio/best', # Prefer M4A, fallback to best audio
            'outtmpl': output_template, # Template like 'path/to/base.%(ext)s'
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a', # Specify desired codec for extraction
                # 'preferredquality': '192', # Optional: set bitrate
            }],
            'progress_hooks': [sync_progress_hook] if progress_callback else [],
            'quiet': True, # Suppress yt-dlp stdout unless error
            'no_warnings': True,
            'noprogress': True if not progress_callback else False, # Only enable internal progress if using hook
            # 'verbose': True, # Enable for deep debugging
        }

        # --- Execute Download ---
        logger.info(f"Using yt-dlp options: {ydl_opts}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await loop.run_in_executor(None, lambda: ydl.download([youtube_url]))

        # --- Verify Download ---
        if actual_download_path and os.path.exists(actual_download_path):
            logger.info(f"Audio download successful. File saved to: {actual_download_path}")
            return actual_download_path
        else:
            # Fallback check if hook didn't capture path or file missing
            logger.warning(f"Download hook did not provide final path or file is missing. Attempting to find file...")
            base_name = os.path.splitext(os.path.basename(output_template))[0]
            found_files = [f for f in os.listdir(output_dir) if f.startswith(base_name) and f.endswith(('.m4a', '.mp3', '.ogg', '.wav'))]
            if found_files:
                actual_download_path = os.path.join(output_dir, found_files[0])
                logger.warning(f"Found matching audio file: {actual_download_path}")
                return actual_download_path
            else:
                error_msg = f"Audio file could not be found in '{output_dir}' after download attempt for base name '{base_name}'."
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

    except Exception as e:
        # Catch potential errors during download or options processing
        error_msg = f"Error during audio download process for {youtube_url}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        # Re-raise the exception to be caught by the calling function (process_video)
        raise Exception(error_msg)


# --- Utility Functions ---

def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from YouTube URL."""
    if not youtube_url:
        return ""

    # Try to match various YouTube URL formats
    patterns = [
        r'(?:v=|\/)([a-zA-Z0-9_-]{11})(?:\?|&|$|\/)',  # Standard YouTube URLs
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',           # Short youtu.be URLs
        r'(?:embed\/)([a-zA-Z0-9_-]{11})',               # Embed URLs
    ]

    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)

    # If no match found, return empty string
    return ""

# --- Transcription Functions ---

def _transcribe_loop_sync(model: WhisperModel, audio_path: str, video_id: str, base_url: str,
                         status_queue_sync: asyncio.Queue, transcription_queue_sync: asyncio.Queue, loop: asyncio.AbstractEventLoop,
                         target_language: Optional[str] = None, task: Literal["transcribe", "translate"] = "transcribe"):
    """
    Synchronous function containing the blocking transcription loop.
    Designed to be run in a separate thread via asyncio.to_thread.
    Communicates progress and results back to the main asyncio loop via queues.
    """
    thread_id = os.getpid() # Get thread/process ID for logging
    logger.info(f"[Thread-{thread_id}] Starting synchronous transcription loop for {audio_path}")
    results_list = [] # Store segment dicts for final return
    full_text_parts = [] # Store markdown formatted text parts for final return

    try:
        # --- Core Blocking Call ---
        segments_gen, info = model.transcribe(
            audio_path,
            language=target_language,
            task=task,
            beam_size=1, # Optimized for speed (higher beam_size might increase accuracy but slow down)
            best_of=1,   # Keep only the single best hypothesis
            temperature=0.0, # Deterministic output
            condition_on_previous_text=False, # Can sometimes speed up, potentially less accurate context
            vad_filter=True, # Use Voice Activity Detection - crucial for filtering silence
            vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=200) # VAD tuning
        )
        logger.info(f"[Thread-{thread_id}] model.transcribe yielded generator. Language: {info.language}, Duration: {info.duration:.2f}s")
        detected_language = info.language
        detected_lang_prob = info.language_probability

        total_segments_processed = 0
        start_loop_time = time.time()

        # --- Process Segments ---
        for idx, segment in enumerate(segments_gen):
            total_segments_processed = idx + 1
            try:
                segment_text = segment.text.strip()
                start_time_secs = segment.start
                end_time_secs = segment.end

                # Formatting for display/storage
                start_time_fmt = format_timestamp(start_time_secs) # HH:MM:SS.ms
                end_time_fmt = format_timestamp(end_time_secs) # HH:MM:SS.ms
                timestamp_seconds_int = int(start_time_secs) # Integer seconds for URL
                watch_url = f"{base_url}&t={timestamp_seconds_int}s" # Add 's' suffix for clarity

                # Create the dictionary for this segment's data
                segment_dict = {
                    'watch_url': watch_url,
                    'video_id': video_id,
                    'id': idx, # Sequential ID
                    'start': start_time_fmt, # Formatted string HH:MM:SS.ms
                    'end': end_time_fmt, # Formatted string HH:MM:SS.ms
                    'text': segment_text,
                    # Include raw float times maybe useful for frontend waveform sync?
                    'start_seconds': start_time_secs,
                    'end_seconds': end_time_secs,
                }
                results_list.append(segment_dict) # Add to list for final return value

                # Prepare data for SSE queues (must be JSON serializable)
                segment_data_for_queue = {
                    "type": "transcription_segment",
                    "content": segment_dict, # Send the structured dict
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"  # Add priority flag for immediate delivery
                }
                status_msg_for_queue = {
                    "type": "status",
                    "content": f"Transcribing segment {idx + 1}...",
                    "timestamp": datetime.now().isoformat()
                }

                # Log the segment being sent to the frontend
                print(f"[Thread-{thread_id}] Sending segment {idx + 1} to frontend: {segment_text[:50]}...")
                logger.info(f"[Thread-{thread_id}] Sending segment {idx + 1} to frontend: {segment_text[:50]}...")
                logger.info(f"[Thread-{thread_id}] Segment data: {json.dumps(segment_data_for_queue)[:200]}...")

                # --- Queue Interaction (Thread-Safe) ---
                if loop.is_running():
                    # Convert to JSON string and log it
                    segment_json = json.dumps(segment_data_for_queue)
                    print(f"[Thread-{thread_id}] JSON string to be sent: {segment_json[:200]}...")
                    logger.info(f"[Thread-{thread_id}] JSON string to be sent: {segment_json[:200]}...")

                    # Always send transcription segments to the transcription queue
                    asyncio.run_coroutine_threadsafe(transcription_queue_sync.put(segment_json), loop)

                    # Only send status updates periodically to avoid overwhelming the frontend
                    # Send status updates for the first few segments and then every 10 segments
                    if idx < 5 or idx % 10 == 0:
                        asyncio.run_coroutine_threadsafe(status_queue_sync.put(json.dumps(status_msg_for_queue)), loop)
                        logger.debug(f"[Thread-{thread_id}] QUEUE PUT: Status update for segment #{idx}")
                else:
                    # If the main loop stops (e.g., application shutdown), stop processing
                    logger.warning(f"[Thread-{thread_id}] Event loop stopped. Halting transcription segment processing at index {idx}.")
                    break # Exit the loop

                # Append to markdown text parts (for final file saving)
                # Format for Markdown table row
                md_link = f"[{start_time_fmt}]({watch_url})" # Clickable timestamp link
                formatted_text_part = f"| {md_link} | {video_id} | {idx} | {start_time_fmt} | {end_time_fmt} | {segment_text.replace('|', ' ')} |\n" # Replace pipes in text
                full_text_parts.append(formatted_text_part)

                # Minimal sleep to potentially yield within the thread, maybe not effective
                # time.sleep(0.001) # Usually not needed / has little effect

            except Exception as segment_error:
                logger.error(f"[Thread-{thread_id}] Error processing segment {idx}: {segment_error}", exc_info=True)
                error_segment_msg = {"type": "error", "content": f"Error processing transcription segment {idx}: {segment_error}"}
                # Try sending error message back to main thread
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(status_queue_sync.put(json.dumps(error_segment_msg)), loop)
                continue # Skip this segment and continue with the next

        # --- Loop Finished ---
        end_loop_time = time.time()
        loop_duration = end_loop_time - start_loop_time
        logger.info(f"[Thread-{thread_id}] Synchronous transcription loop finished. Processed {total_segments_processed} segments in {loop_duration:.2f}s.")
        logger.info(f"[Thread-{thread_id}] Detected language: {detected_language} (Probability: {detected_lang_prob:.2f})")

        # Return the collected results and the detected language info
        return results_list, full_text_parts, {"language": detected_language, "probability": detected_lang_prob}

    except Exception as transcription_error:
        # Catch errors during the model.transcribe call itself or loop setup
        logger.error(f"[Thread-{thread_id}] Core transcription error in sync loop: {transcription_error}", exc_info=True)
        error_general_msg = {"type": "error", "content": f"Core transcription process failed: {transcription_error}"}
        if loop.is_running():
            # Use run_coroutine_threadsafe from the thread
            asyncio.run_coroutine_threadsafe(status_queue_sync.put(json.dumps(error_general_msg)), loop)
        # Return None to indicate failure to the awaiting async function
        return None, None, None


async def transcribe_audio(audio_path: str, status_queue: asyncio.Queue, transcription_queue: asyncio.Queue, youtube_video_url: str, target_language: Optional[str] = None, task: Literal["transcribe", "translate"] = "transcribe"):
    """
    Asynchronously manages the transcription of an audio file using faster-whisper.
    Runs the blocking transcription process in a separate thread.
    Sends real-time updates via asyncio Queues.
    """
    logger.info(f"Preparing for local transcription task: {audio_path}")
    console.print(f"[MIC] Starting transcription for: [cyan]{os.path.basename(audio_path)}[/cyan]")
    results: Optional[List[Dict]] = None
    full_text: Optional[str] = None
    language_info: Optional[Dict] = None

    try:
        # --- Pre-checks ---
        if not os.path.exists(audio_path):
            error_msg = f"Audio file not found at path: {audio_path}"
            logger.error(error_msg)
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
            raise FileNotFoundError(error_msg)

        await status_queue.put(json.dumps({"type": "status", "content": "Loading Whisper model..."}))
        # Get model (initialization happens here if it's the first call)
        model = get_whisper_model() # This might block briefly if first time, but it's acceptable here.

        # --- Extract Info Needed by Thread ---
        # Use regex to robustly find video ID from various URL formats
        video_id_match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})(?:\?|&|\/|$)", youtube_video_url)
        video_id = video_id_match.group(1) if video_id_match else "UNKNOWN_ID"
        base_url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"Extracted Video ID: {video_id} for transcription.")

        # Get the current running event loop to pass to the thread
        loop = asyncio.get_running_loop()

        # --- Dispatch to Thread ---
        await status_queue.put(json.dumps({"type": "status", "content": "Dispatching transcription to background thread..."}))
        logger.info(f"Dispatching transcription task to thread for: {audio_path}")

        # Run the synchronous blocking function in a separate thread
        results, full_text_parts, language_info = await asyncio.to_thread(
            _transcribe_loop_sync, # The function to run
            # Arguments for the function:
            model,
            audio_path,
            video_id,
            base_url,
            status_queue, # Pass the queues
            transcription_queue,
            loop, # Pass the event loop
            target_language,
            task
        )

        logger.info(f"Transcription thread completed for: {audio_path}")

        # --- Process Results ---
        if results is None or full_text_parts is None or language_info is None:
             # The thread function returned None, indicating failure. Error logged within thread.
             logger.error("Transcription thread failed to return valid results.")
             # Error message should have been sent via queue from the thread already
             # No final "transcription_complete" message will be sent.
             return None, None # Indicate failure up to process_video

        logger.info(f"Transcription successful. Segments processed: {len(results)}")
        if language_info:
             logger.info(f"Detected Language: {language_info.get('language', 'N/A')} (Prob: {language_info.get('probability', 0):.2f})")

        # Assemble the final markdown text from parts collected in the thread
        title_md = f"# Transcription for Video: [{video_id}]({base_url})\n\n"
        title_md += f"**Detected Language:** {language_info.get('language', 'N/A')}\n"
        title_md += f"**Task:** {task.capitalize()}\n\n"
        table_header_md = "| Timestamp Link | Video ID | Seg ID | Start | End | Text |\n"
        table_separator_md = "|---|---|---|---|---|---|\n"
        full_text = title_md + table_header_md + table_separator_md + "".join(full_text_parts)

        # Send completion messages *after* thread is done and results processed
        completion_msg = {"type": "transcription_complete", "content": "Transcription process finished."} # Keep content minimal
        await transcription_queue.put(json.dumps(completion_msg))
        logger.info(f"QUEUE PUT (Transcription Complete)")

        status_msg_final = {"type": "status", "content": f"Transcription complete. Segments: {len(results)}. Language: {language_info.get('language', 'N/A')}."}
        await status_queue.put(json.dumps(status_msg_final))
        logger.info(f"QUEUE PUT (Status): Transcription Completed")
        console.print(f"[bold green][OK] Transcription complete for {os.path.basename(audio_path)}.[/bold green]")

        return results, full_text # Return results and assembled text

    except FileNotFoundError as fnf_err:
        # Already handled logging and status queue message, just re-raise
        raise fnf_err
    except RuntimeError as rt_err:
         # Catch model initialization errors from get_whisper_model
         error_msg = f"Whisper model runtime error: {str(rt_err)}"
         logger.critical(error_msg, exc_info=True) # Critical error
         await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
         raise rt_err # Re-raise to stop processing
    except Exception as e:
        # Catch any other unexpected errors in this async wrapper function
        error_msg = f"Unexpected error in transcribe_audio wrapper: {str(e)}"
        logger.error(error_msg, exc_info=True)
        try:
            # Try to send error message via queue
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
        except Exception as status_error:
            logger.error(f"Error sending error status to queue: {str(status_error)}")
        # Re-raise so process_video knows this step failed critically
        raise e

# Groq transcription implementation
async def process_audio_with_groq(audio_path: str, status_queue: asyncio.Queue, transcription_queue: asyncio.Queue, youtube_video_url: str):
    """
    Process audio using the Groq API in chunks to avoid rate limits and provide a better user experience.
    """
    try:
        # Extract video ID from YouTube URL
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            error_msg = f"Could not extract video ID from URL: {youtube_video_url}"
            logger.error(error_msg)
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
            return None, None

        # Create base URL for watch links
        base_url = f"https://www.youtube.com/watch?v={video_id}"

        # Send status update
        await status_queue.put(json.dumps({"type": "status", "content": "Preparing audio for Groq transcription...", "timestamp": datetime.now().isoformat()}))

        # Import required modules for Groq transcription
        try:
            from openai import OpenAI
            import os
            from pydub import AudioSegment
            import tempfile
        except ImportError as e:
            error_msg = f"Missing required modules for Groq transcription: {e}"
            logger.error(error_msg)
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
            return None, None

        # Check if GROQ_API_KEY is set
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            error_msg = "GROQ_API_KEY environment variable not set"
            logger.error(error_msg)
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
            return None, None

        # Initialize Groq client
        client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")

        # Convert audio to MP3 format if needed
        audio_format = audio_path.split('.')[-1].lower()
        if audio_format != 'mp3':
            await status_queue.put(json.dumps({"type": "status", "content": "Converting audio to MP3 format...", "timestamp": datetime.now().isoformat()}))
            try:
                # Create a temporary file for the MP3
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    mp3_path = temp_file.name

                # Convert to MP3
                audio = AudioSegment.from_file(audio_path, format=audio_format)
                audio.export(mp3_path, format="mp3")
                logger.info(f"Converted {audio_path} to MP3 format: {mp3_path}")

                # Use the MP3 file for transcription
                audio_path_for_transcription = mp3_path
            except Exception as e:
                error_msg = f"Error converting audio to MP3: {e}"
                logger.error(error_msg)
                await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
                return None, None
        else:
            audio_path_for_transcription = audio_path

        # Load the audio file
        try:
            audio = AudioSegment.from_file(audio_path_for_transcription)
            total_duration_ms = len(audio)
            total_duration_sec = total_duration_ms / 1000

            # Calculate chunk size (5 minutes per chunk)
            chunk_size_ms = 5 * 60 * 1000  # 5 minutes in milliseconds
            num_chunks = math.ceil(total_duration_ms / chunk_size_ms)

            await status_queue.put(json.dumps({
                "type": "status",
                "content": f"Audio duration: {total_duration_sec:.2f} seconds. Processing in {num_chunks} chunks.",
                "timestamp": datetime.now().isoformat()
            }))

            # Initialize results containers
            results_list = []
            full_text_parts = []
            segment_counter = 0

            # Process audio in chunks
            for chunk_idx in range(num_chunks):
                chunk_start_ms = chunk_idx * chunk_size_ms
                chunk_end_ms = min(chunk_start_ms + chunk_size_ms, total_duration_ms)

                # Extract chunk
                chunk = audio[chunk_start_ms:chunk_end_ms]

                # Create a temporary file for the chunk
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as chunk_file:
                    chunk_path = chunk_file.name

                # Export chunk to temporary file
                chunk.export(chunk_path, format="mp3")

                # Send status update
                await status_queue.put(json.dumps({
                    "type": "status",
                    "content": f"Processing chunk {chunk_idx + 1}/{num_chunks} ({chunk_start_ms/1000:.2f}s to {chunk_end_ms/1000:.2f}s)...",
                    "timestamp": datetime.now().isoformat()
                }))

                # Process chunk with Groq API
                with open(chunk_path, 'rb') as audio_chunk_file:
                    try:
                        # Call Groq API for transcription
                        response = client.audio.transcriptions.create(
                            file=audio_chunk_file,
                            model="whisper-large-v3",
                            response_format="verbose_json",
                            timestamp_granularities=["segment"]
                        )

                        # Process the response
                        if hasattr(response, 'segments') and response.segments:
                            # Send status update
                            await status_queue.put(json.dumps({
                                "type": "status",
                                "content": f"Received {len(response.segments)} segments for chunk {chunk_idx + 1}",
                                "timestamp": datetime.now().isoformat()
                            }))

                            # Process segments
                            for idx, segment in enumerate(response.segments):
                                # Extract segment data
                                segment_text = segment.text.strip()

                                # Adjust timestamps to account for chunk position
                                start_time_secs = segment.start + (chunk_start_ms / 1000)
                                end_time_secs = segment.end + (chunk_start_ms / 1000)

                                # Format timestamps
                                start_time_fmt = format_timestamp(start_time_secs)
                                end_time_fmt = format_timestamp(end_time_secs)
                                timestamp_seconds_int = int(start_time_secs)
                                watch_url = f"{base_url}&t={timestamp_seconds_int}s"

                                # Create segment dictionary
                                segment_dict = {
                                    'watch_url': watch_url,
                                    'video_id': video_id,
                                    'id': segment_counter,
                                    'start': start_time_fmt,
                                    'end': end_time_fmt,
                                    'text': segment_text,
                                    'start_seconds': start_time_secs,
                                    'end_seconds': end_time_secs,
                                }

                                # Add to results list
                                results_list.append(segment_dict)

                                # Format for markdown
                                md_link = f"[{start_time_fmt}]({watch_url})"
                                formatted_text_part = f"| {md_link} | {video_id} | {segment_counter} | {start_time_fmt} | {end_time_fmt} | {segment_text.replace('|', ' ')} |\n"
                                full_text_parts.append(formatted_text_part)

                                # Send segment to frontend
                                segment_data_for_queue = {
                                    "type": "transcription_segment",
                                    "content": segment_dict,
                                    "timestamp": datetime.now().isoformat(),
                                    "priority": "high"  # Add priority flag for immediate delivery
                                }

                                # Log the segment being sent to the frontend
                                console.print(f"[bold green]Sending segment {segment_counter + 1} to frontend:[/bold green] {segment_text[:50]}...")
                                logger.info(f"Sending segment {segment_counter + 1} to frontend: {segment_text[:50]}...")

                                # Send segment to frontend
                                await transcription_queue.put(json.dumps(segment_data_for_queue))

                                # Increment segment counter
                                segment_counter += 1

                                # Send status update less frequently to avoid overwhelming the frontend
                                # Send for the first few segments and then every 20 segments
                                if segment_counter < 5 or segment_counter % 20 == 0:
                                    await status_queue.put(json.dumps({
                                        "type": "status",
                                        "content": f"Processed {segment_counter} segments so far...",
                                        "timestamp": datetime.now().isoformat()
                                    }))
                        else:
                            logger.warning(f"No segments found in chunk {chunk_idx + 1}")
                    except Exception as e:
                        logger.error(f"Error processing chunk {chunk_idx + 1}: {e}")
                        await status_queue.put(json.dumps({
                            "type": "status",
                            "content": f"Error processing chunk {chunk_idx + 1}: {e}",
                            "timestamp": datetime.now().isoformat()
                        }))

                # Clean up temporary chunk file
                try:
                    os.unlink(chunk_path)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary chunk file: {e}")

                # Add a small delay between chunks to avoid rate limits
                await asyncio.sleep(1)

            # Send completion status
            await status_queue.put(json.dumps({
                "type": "status",
                "content": f"Completed processing {segment_counter} segments from {num_chunks} chunks",
                "timestamp": datetime.now().isoformat()
            }))

            # Send transcription_complete message
            await transcription_queue.put(json.dumps({
                "type": "transcription_complete",
                "content": {
                    "segments": segment_counter,
                    "chunks": num_chunks
                },
                "timestamp": datetime.now().isoformat()
            }))
            logger.info(f"Sent transcription_complete message for Groq transcription")

            # Join full text parts
            full_text = ''.join(full_text_parts)

            # Clean up temporary file if created
            if audio_format != 'mp3':
                try:
                    os.unlink(mp3_path)
                    logger.info(f"Removed temporary MP3 file: {mp3_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary MP3 file: {e}")

            return results_list, full_text
        except Exception as e:
            error_msg = f"Error processing audio: {e}"
            logger.error(error_msg)
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
            return None, None
    except Exception as e:
        error_msg = f"Unexpected error in Groq transcription: {e}"
        logger.error(error_msg)
        await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
        return None, None


# --- Main Video Processing Orchestrator ---
async def process_video(
    youtube_video_url: str,
    obsidian_dir: str,
    status_queue: asyncio.Queue,
    transcription_queue: asyncio.Queue,
    output_folder: str = None, # Optional output folder override
    model_config: dict = None # Configuration dict
) -> Dict[str, Any]:
    """
    Orchestrates the video download, transcription, and saving process.
    Sends status updates and results via provided asyncio Queues.
    Returns a dictionary summarizing the outcome.
    """
    process_start_time = time.time()
    logger.info(f"--- Starting Video Processing ---")
    logger.info(f"Received request for URL: {youtube_video_url}")
    console.print(f"\n[bold blue]>>> Starting processing for:[/bold blue] {youtube_video_url}")

    # Use defaults if not provided
    # Obtain the LLM registry service instance
    registry_service = get_llm_registry_service()

    if not output_folder:
        output_folder = os.path.join(WORKSPACE_ROOT, SUBFOLDERS['transcriptions']['markdown'])
    if not model_config:
        model_config = {"model": "faster-whisper", "use_groq": False}

    use_groq = model_config.get("use_groq", False)
    transcription_engine = "Groq" if use_groq else "Local Faster-Whisper"
    logger.info(f"Output Folder: {output_folder}")
    logger.info(f"Obsidian Folder: {obsidian_dir}")
    logger.info(f"Transcription Engine: {transcription_engine}")

    video_id = "UNKNOWN" # Default value
    video_title = "Untitled Video" # Default value
    base_filename = "transcription" # Default value
    actual_audio_path = None # To store path of downloaded audio

    try:
        # --- 1. Extract Video Info ---
        await status_queue.put(json.dumps({"type": "status", "content": "Extracting video information..."}))
        logger.info("Step 1: Extracting video info...")
        try:
            video_info = await extract_video_info(youtube_video_url)
            video_id = video_info.get('id', 'N/A')
            video_title = video_info.get('title', 'Untitled Video')
            clean_title = clean_filename(video_title) # Sanitize title for filenames
            logger.info(f"Video Info Extracted: ID={video_id}, Title='{video_title}'")

            # Send detailed metadata via SSE queue
            metadata_content = {
                "title": video_title,
                "id": video_id,
                "thumbnail": video_info.get('best_thumbnail', {}).get('url'),
                "channel": video_info.get('channel'),
                "duration": video_info.get('duration_formatted'),
                "upload_date": video_info.get('upload_date')
                # Add more fields from video_info if needed by frontend
            }
            metadata_msg = {"type": "video_metadata", "content": metadata_content}
            await status_queue.put(json.dumps(metadata_msg))
            logger.info(f"QUEUE PUT (Metadata): '{video_title}'")
            console.print(f"[VIDEO] Video Info: [green]'{video_title}'[/green] (ID: {video_id})")

            # Set base filename using extracted info and engine type
            model_prefix = "groq" if use_groq else "local"
            base_filename = f"{model_prefix}_{clean_title}_{video_id}"
            logger.info(f"Base filename set to: {base_filename}")

        except Exception as info_err:
            # Handle failure to get video info (critical step)
            error_msg = f"Failed to extract video info: {info_err}"
            logger.error(error_msg, exc_info=True)
            console.print(f"[bold red]Error: {error_msg}[/bold red]")
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
            # Return failure dict immediately
            return {"status": "error", "message": error_msg, "step": "extract_info"}

        # --- 2. Prepare Directories ---
        logger.info("Step 2: Preparing output directories...")
        # Output Folder Structure
        audio_dir = os.path.join(WORKSPACE_ROOT, 'transcriptions', SUBFOLDERS['transcriptions']['audio'])
        csv_dir = os.path.join(WORKSPACE_ROOT, 'transcriptions', 'csv')
        excel_dir = os.path.join(WORKSPACE_ROOT, 'transcriptions', 'excel')
        md_dir = os.path.join(WORKSPACE_ROOT, 'transcriptions', SUBFOLDERS['transcriptions']['markdown'])
        # pdf_dir = os.path.join(output_folder, OUTPUT_SUBFOLDERS["pdf"]) # PDF saving not implemented
        # Obsidian Folder Structure (mirrored)
        obsidian_md_dir = os.path.join(obsidian_dir, SUBFOLDERS['transcriptions']['markdown'])
        obsidian_csv_dir = os.path.join(obsidian_dir, 'csv')
        obsidian_excel_dir = os.path.join(obsidian_dir, 'excel')
        # obsidian_pdf_dir = os.path.join(obsidian_dir, OUTPUT_SUBFOLDERS["pdf"]) # PDF saving not implemented
        # Create all needed directories, use ensure_directory_exists from utils
        dirs_to_create = [audio_dir, csv_dir, excel_dir, md_dir, obsidian_md_dir, obsidian_csv_dir, obsidian_excel_dir]
        for directory in dirs_to_create:
            try:
                await ensure_directory_exists(directory)
                logger.debug(f"Ensured directory exists: {directory}")
            except Exception as dir_err:
                logger.warning(f"Could not create or access directory {directory}: {dir_err}")
        logger.info(f"Output directories prepared in '{output_folder}' and '{obsidian_dir}'")
        # Place downloaded audio in the 'audio' subdirectory
        audio_output_template = os.path.join(audio_dir, f"{base_filename}.%(ext)s")

        # --- 3. Download Audio ---
        await status_queue.put(json.dumps({"type": "status", "content": "Starting audio download..."}))
        logger.info("Step 3: Downloading audio...")
        console.print(f"[DOWN] Downloading audio...")
        # Use m4a as preferred format, let yt-dlp determine final extension in template
        # Place downloaded audio in the 'audio' subdirectory

        # Define the async progress callback for download_audio
        async def download_progress_callback(progress_percent: float):
            """ Sends download progress updates to the status queue. """
            progress_msg = { "type": "status", "content": f"Downloading audio: {progress_percent:.1f}%" }
            await status_queue.put(json.dumps(progress_msg))
            # Optionally print to console too, but sparingly
            # if int(progress_percent) % 10 == 0: console.print(f"   Download progress: {progress_percent:.1f}%")

        try:
            actual_audio_path = await download_audio(
                youtube_video_url,
                audio_output_template,
                progress_callback=download_progress_callback # Pass the callback
            )
            if not actual_audio_path or not os.path.exists(actual_audio_path):
                 # This case should ideally be caught within download_audio, but double-check
                 raise FileNotFoundError("Audio file path not returned or file does not exist after download.")
            logger.info(f"Audio downloaded successfully to: {actual_audio_path}")
            await status_queue.put(json.dumps({"type": "status", "content": "Audio download complete."}))
            logger.info(f"QUEUE PUT (Status): Download complete.")
            console.print(f"[green]   Download complete:[/green] {os.path.basename(actual_audio_path)}")
        except Exception as download_err:
            error_msg = f"Audio download failed: {str(download_err)}"
            logger.error(error_msg, exc_info=True)
            console.print(f"[bold red]Error: {error_msg}[/bold red]")
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
            # Return failure dict immediately
            return {"status": "error", "message": error_msg, "step": "download_audio"}

        # --- 4. Perform Transcription ---
        await status_queue.put(json.dumps({"type": "status", "content": f"Starting transcription ({transcription_engine})..."}))
        logger.info(f"Step 4: Starting transcription using {transcription_engine}...")
        segments: Optional[List[Dict[str, Any]]] = None
        full_text: Optional[str] = None
        transcription_start_time = time.time()

        try:
            transcription_model_id = model_config.get("model", "faster-whisper") # Get model_id from config

            if use_groq or (transcription_model_id and not transcription_model_id == "faster-whisper"):
                logger.info(f"Using LLM Registry for transcription with model_id: {transcription_model_id}")
                # Read audio data
                with open(actual_audio_path, "rb") as audio_file:
                    audio_data_bytes = audio_file.read()
                
                # Call the registry service
                # The transcribe_audio_from_registry should return a dict like:
                # {"text": "full transcript", "segments": [{"start": S, "end": E, "text": T, "speaker": S}...]}
                # or None on failure.
                registry_response = await registry_service.transcribe_audio( # Call the method on the instance
                    model_id=transcription_model_id,
                    audio_data=audio_data_bytes,
                    # Potentially pass other kwargs like language if supported by LiteLLM endpoint
                    # For diarization, the registry function or LiteLLM should handle it if model supports
                )

                if registry_response and "segments" in registry_response and "text" in registry_response:
                    # Process segments from registry_response
                    segments = []
                    full_text_parts_temp = []
                    video_id_for_md = extract_video_id(youtube_video_url) or "UNKNOWN_ID"
                    base_url_for_md = f"https://www.youtube.com/watch?v={video_id_for_md}"

                    for idx, seg_data in enumerate(registry_response.get("segments", [])):
                        start_secs = seg_data.get("start", 0.0)
                        end_secs = seg_data.get("end", 0.0)
                        text = seg_data.get("text", "").strip()
                        speaker = seg_data.get("speaker") # Optional speaker info

                        start_fmt = format_timestamp(start_secs)
                        end_fmt = format_timestamp(end_secs)
                        watch_url_ts = f"{base_url_for_md}&t={int(start_secs)}s"
                        
                        segment_dict = {
                            'watch_url': watch_url_ts,
                            'video_id': video_id_for_md,
                            'id': idx,
                            'start': start_fmt,
                            'end': end_fmt,
                            'text': text,
                            'start_seconds': start_secs,
                            'end_seconds': end_secs,
                        }
                        if speaker:
                            segment_dict['speaker'] = speaker
                        segments.append(segment_dict)

                        md_link = f"[{start_fmt}]({watch_url_ts})"
                        speaker_md = f" (Speaker {speaker})" if speaker else ""
                        formatted_text_part = f"| {md_link} | {video_id_for_md} | {idx} | {start_fmt} | {end_fmt} | {text.replace('|', ' ')}{speaker_md} |\n"
                        full_text_parts_temp.append(formatted_text_part)
                    
                    # Assemble full_text for markdown
                    title_md_header = f"# Transcription for Video: [{video_id_for_md}]({base_url_for_md})\n\n"
                    table_header_md_content = "| Timestamp Link | Video ID | Seg ID | Start | End | Text |\n"
                    table_separator_md_content = "|---|---|---|---|---|---|\n"
                    full_text = title_md_header + table_header_md_content + table_separator_md_content + "".join(full_text_parts_temp)
                    
                    logger.info(f"Transcription via registry successful. Segments: {len(segments)}")
                    # Send segments to queue
                    for seg_dict_for_q in segments:
                        seg_q_msg = {
                            "type": "transcription_segment", 
                            "content": seg_dict_for_q, 
                            "timestamp": datetime.now().isoformat(),
                            "priority": "high"
                        }
                        await transcription_queue.put(json.dumps(seg_q_msg))

                else:
                    logger.error(f"Transcription via registry for model {transcription_model_id} failed or returned invalid data.")
                    segments = None # Indicate failure
                    full_text = None
            else: # Local Faster Whisper
                segments, full_text = await transcribe_audio( # This is the original local transcribe_audio
                    actual_audio_path, status_queue, transcription_queue, youtube_video_url
                )

            transcription_duration = time.time() - transcription_start_time
            logger.info(f"Transcription step finished in {transcription_duration:.2f}s.")

            # Check if transcription step failed (returned None)
            if segments is None or full_text is None:
                # Error message should have been sent from the transcription function via queue
                logger.error(f"Transcription using {transcription_engine} failed.")
                console.print(f"[bold red]Error: Transcription process failed.[/bold red]")
                # Return failure dict - step already logged error internally
                return {"status": "failed", "message": f"{transcription_engine} transcription failed.", "step": "transcribe"}

        except Exception as transcribe_err:
             # Catch unexpected errors during the transcription call itself
             error_msg = f"Error during {transcription_engine} transcription call: {str(transcribe_err)}"
             logger.error(error_msg, exc_info=True)
             console.print(f"[bold red]Error: {error_msg}[/bold red]")
             await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
             return {"status": "error", "message": error_msg, "step": "transcribe"}


        # --- 5. Save Results ---
        await status_queue.put(json.dumps({"type": "status", "content": "Saving transcription files..."}))
        logger.info("Step 5: Saving transcription results...")
        console.print(f"[SAVE] Saving transcription files...")
        files_saved = {} # Dictionary to store paths of successfully saved files

        try:
            # Create DataFrame from segments (which should be a list of dicts)
            if isinstance(segments, list):
                 df = pd.DataFrame(segments)
                 logger.info(f"Created DataFrame with {len(df)} segments.")
            else:
                 # This shouldn't happen if transcription succeeded, but handle defensively
                 logger.error("Transcription segments were not in the expected list format. Cannot create DataFrame.")
                 df = pd.DataFrame() # Create empty DF to avoid errors below, but saving will likely fail or be empty

            # Save CSV
            csv_filename = f"{base_filename}_transcription.csv"
            csv_output_path, csv_obsidian_path = await save_to_both_locations(df, csv_filename, csv_dir, obsidian_csv_dir)
            if csv_output_path: files_saved['csv'] = csv_filename
            await status_queue.put(json.dumps({"type": "status", "content": "CSV files saved."}))
            logger.info(f"QUEUE PUT (Status): CSV saved")
            console.print(f"[green]   CSV saved:[/green] {csv_filename}")

            # Save Markdown
            md_filename = f"{base_filename}_transcription.md"
            md_output_path, md_obsidian_path = await save_to_both_locations(full_text, md_filename, md_dir, obsidian_md_dir, is_markdown=True)
            if md_output_path: files_saved['markdown'] = md_filename
            await status_queue.put(json.dumps({"type": "status", "content": "Markdown files saved."}))
            logger.info(f"QUEUE PUT (Status): MD saved")
            console.print(f"[green]   Markdown saved:[/green] {md_filename}")

            # Save Excel
            excel_filename = f"{base_filename}_transcription.xlsx"
            excel_output_path, excel_obsidian_path = await save_to_both_locations(df, excel_filename, excel_dir, obsidian_excel_dir)
            if excel_output_path: files_saved['excel'] = excel_filename
            await status_queue.put(json.dumps({"type": "status", "content": "Excel files saved."}))
            logger.info(f"QUEUE PUT (Status): Excel saved")
            console.print(f"[green]   Excel saved:[/green] {excel_filename}")

        except Exception as save_err:
             # Log saving errors but maybe don't fail the whole process if some files saved?
             error_msg = f"Error occurred during file saving: {str(save_err)}"
             logger.error(error_msg, exc_info=True)
             console.print(f"[bold orange]Warning: {error_msg}[/bold orange]")
             # Send a non-fatal error/warning to the queue
             await status_queue.put(json.dumps({"type": "warning", "content": error_msg}))
             # Continue to final status message, but results might be incomplete

        # --- 6. Final Completion Status ---
        process_end_time = time.time()
        total_duration = process_end_time - process_start_time
        logger.info(f"--- Video Processing Completed ---")
        logger.info(f"Total processing time: {total_duration:.2f} seconds.")
        final_status_content = f"Processing complete for '{video_title}' ({total_duration:.2f}s)."
        final_status_msg = {"type": "status", "content": final_status_content}
        await status_queue.put(json.dumps(final_status_msg))
        logger.info(f"QUEUE PUT (Status): Processing complete")
        console.print(f"\n🎉 [bold green]Processing complete for '{video_title}' in {total_duration:.2f}s.[/bold green]")

        # --- ADDED: Send safe_to_disconnect AFTER completion message ---
        await asyncio.sleep(0.5) # Small delay to ensure message gets processed
        await status_queue.put(json.dumps({
            "type": "connection_status",
            "content": "safe_to_disconnect",
            "timestamp": datetime.now().isoformat()
        }))
        logger.info("Sent final safe_to_disconnect signal (success path)")
        # --- END ADDED ---

        # Return success details
        return {
            "status": "completed",
            "message": final_status_content,
            "files": files_saved, # Dict of successfully saved filenames by type
            "paths": { # Base directories where files were saved
                "output_folder": output_folder,
                "obsidian_folder": obsidian_dir,
                "audio_file": os.path.basename(actual_audio_path) if actual_audio_path else None
            },
            "duration_seconds": total_duration
        }

    except Exception as e:
        # --- Global Exception Handler for process_video ---
        process_end_time = time.time()
        total_duration = process_end_time - process_start_time
        error_msg = f"Unhandled error during video processing ({total_duration:.2f}s elapsed): {str(e)}"
        logger.critical(error_msg, exc_info=True) # Use CRITICAL for unexpected top-level errors
        console.print(f"[bold red]CRITICAL ERROR: {error_msg}[/bold red]")
        try:
            # Try to send a final error status via SSE queue
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
            logger.info(f"QUEUE PUT (Critical Error): {error_msg}")

            # --- ADDED: Send safe_to_disconnect AFTER error message ---
            await asyncio.sleep(0.5) # Small delay
            await status_queue.put(json.dumps({
                "type": "connection_status",
                "content": "safe_to_disconnect",
                "timestamp": datetime.now().isoformat()
            }))
            logger.info("Sent final safe_to_disconnect signal (error path)")
            # --- END ADDED ---

        except Exception as status_error:
            # Log if sending the error message itself fails
            logger.error(f"Failed to send final critical error status/disconnect signal to queue: {str(status_error)}")

        # Return error details
        return {
            "status": "error",
            "message": error_msg,
            "step": "unknown", # Indicate the error was caught at the top level
            "duration_seconds": total_duration
        }

# --- Commented out: Unused Audio Chunking Function (Appears OpenAI related) ---
"""
async def process_audio_in_chunks(audio_file_path: str, chunk_duration_ms: int = 300000) -> str:
    # This function seems designed for chunking audio and sending to an API (like OpenAI Whisper API),
    # potentially with pydub for manipulation. It is not currently called by the main process_video flow
    # and requires an API key (e.g., openai_api_key) and proper endpoint logic.
    # Keeping it commented out for reference if needed later.
    logger.warning(f"Function 'process_audio_in_chunks' is defined but not used in the current workflow.")
    # ... (Implementation using AudioSegment, tempfile, aiohttp to call an API) ...
    pass
"""

# --- Optional: Add functions like download_video_clip, download_chapter if needed ---
# async def download_video_clip(...): ...
# async def download_chapter(...): ...


# --- Example Usage (if running this script directly) ---
if __name__ == '__main__':
    # This block allows testing the functions directly if needed.
    # Requires setting up dummy queues and potentially hardcoding values.
    print("Script running in main execution block.")

    async def run_test():
        # Example: Test video info extraction
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Example URL
        print(f"Testing video info extraction for: {test_url}")
        try:
            info = await extract_video_info(test_url)
            print("Video Info:")
            # print(json.dumps(info, indent=2)) # Pretty print full info
            print(f"  Title: {info.get('title')}")
            print(f"  ID: {info.get('id')}")
            print(f"  Duration: {info.get('duration_formatted')}")
            print(f"  Channel: {info.get('channel')}")
            print(f"  Thumbnail: {info.get('best_thumbnail', {}).get('url')}")
        except Exception as e:
            print(f"Error during info extraction test: {e}")

        # Example: Set up dummy queues for process_video test
        status_q = asyncio.Queue()
        transcription_q = asyncio.Queue()

        async def queue_reader(q: asyncio.Queue, name: str):
            """Helper to read messages from a queue for testing."""
            while True:
                msg_json = await q.get()
                try:
                    msg = json.loads(msg_json)
                    print(f"<- QUEUE [{name}]: Type='{msg.get('type')}', Content='{str(msg.get('content'))[:100]}...'")
                except json.JSONDecodeError:
                     print(f"<- QUEUE [{name}]: Received non-JSON message: {msg_json}")
                q.task_done() # Mark message as processed

        # Start reader tasks (run in background)
        status_reader_task = asyncio.create_task(queue_reader(status_q, "Status"))
        transcription_reader_task = asyncio.create_task(queue_reader(transcription_q, "Transcription"))

        # --- Configure and run process_video test ---
        test_output = os.path.join(os.getcwd(), "test_output")
        test_obsidian = os.path.join(os.getcwd(), "test_obsidian")
        print(f"\nTesting process_video (will download & transcribe)...")
        print(f"Output will go to: {test_output}")
        print(f"Obsidian output to: {test_obsidian}")

        # Ensure test directories exist
        os.makedirs(test_output, exist_ok=True)
        os.makedirs(test_obsidian, exist_ok=True)

        test_config = {
            "model": "faster-whisper", # Use local model for test
            "use_groq": False
        }

        try:
            result = await process_video(
                youtube_video_url=test_url,
                obsidian_dir=test_obsidian,
                status_queue=status_q,
                transcription_queue=transcription_q,
                output_folder=test_output,
                model_config=test_config
            )
            print("\n--- process_video Test Result ---")
            print(json.dumps(result, indent=2))
            print("--- End process_video Test ---")

        except Exception as e:
            print(f"Error during process_video test: {e}")
        finally:
             # Wait briefly for queues to process final messages (adjust time if needed)
             await asyncio.sleep(2)
             # Cancel reader tasks
             status_reader_task.cancel()
             transcription_reader_task.cancel()
             try:
                 await asyncio.gather(status_reader_task, transcription_reader_task, return_exceptions=True)
             except asyncio.CancelledError:
                 print("Queue reader tasks cancelled.")

    # Run the async test function
    asyncio.run(run_test())

# --- END OF REFACTORED Transcribe1.py ---
