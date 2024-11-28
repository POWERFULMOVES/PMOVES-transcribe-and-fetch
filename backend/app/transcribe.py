import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import asyncio
import pandas as pd
from faster_whisper import WhisperModel
from pydantic import BaseModel
from .utils import (
    clean_filename,
    format_as_hyperlink,
    ensure_directory_exists,
    download_audio,
    save_text_to_markdown,
    convert_markdown_to_pdf,
    save_segments_to_csv,
    save_segments_to_excel,
    format_timestamp
)
from .config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE, GROQ_API_KEY
import logging
import json
import aiohttp
from fastapi import HTTPException
import torch
from typing import Literal
import yt_dlp
from pydub import AudioSegment
import tempfile
import math
import re

logger = logging.getLogger(__name__)

# First get device info
def get_optimal_device() -> tuple[Literal["cpu", "cuda", "mps"], Literal["int8", "float16", "int8_float16"]]:
    if torch.cuda.is_available():
        return "cuda", "float16"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps", "float16"
    else:
        return "cpu", "int8"

# Then use it
optimal_device, optimal_compute_type = get_optimal_device()

# Now log the information
logger.info(f"Loading Whisper model: {WHISPER_MODEL}")
logger.info(f"CUDA available: {torch.cuda.is_available()}")
logger.info(f"Using device: {optimal_device} with compute type: {optimal_compute_type}")
if torch.cuda.is_available():
    logger.info(f"GPU Device: {torch.cuda.get_device_name(0)}")
    logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

# Initialize the model
model = WhisperModel(
    WHISPER_MODEL,
    device="cuda",  # Force CUDA for GPU
    compute_type="float16",  # Use float16 for faster GPU processing
    cpu_threads=8,           # Increase CPU threads
    num_workers=4,           # Increase workers for parallel processing
    download_root=None,
    local_files_only=False
)
logger.info("Whisper model loaded successfully")

class VideoProcessRequest(BaseModel):
    youtube_video_url: str
    obsidian_dir: str
    output_folder: str
    use_groq: bool = False
    transcription_model: str = "faster-whisper"

# Add this function at the module level (outside any other function)
async def save_to_both_locations(content, filename, output_folder, obsidian_dir, is_markdown=False):
    """
    Save content to both output_folder and obsidian_dir
    Returns tuple of (output_path, obsidian_path)
    """
    # Create full paths
    output_path = os.path.join(output_folder, filename)
    obsidian_path = os.path.join(obsidian_dir, filename)
    
    logger.info(f"Saving to output path: {output_path}")
    logger.info(f"Saving to obsidian path: {obsidian_path}")
    
    if is_markdown:
        if isinstance(content, pd.DataFrame):
            # Convert DataFrame to markdown table string
            markdown_content = content.to_markdown(index=False)
            await save_text_to_markdown(markdown_content, output_path)
            await save_text_to_markdown(markdown_content, obsidian_path)
        else:
            # Regular text content
            await save_text_to_markdown(content, output_path)
            await save_text_to_markdown(content, obsidian_path)
    else:
        # If content is a DataFrame, save directly
        if isinstance(content, pd.DataFrame):
            await save_segments_to_csv(content, output_path)
            await save_segments_to_csv(content, obsidian_path)
        else:
            # If content is a list, convert to DataFrame first
            df = pd.DataFrame(content)
            await save_segments_to_csv(df, output_path)
            await save_segments_to_csv(df, obsidian_path)
    
    return output_path, obsidian_path

# Function to process a video
async def process_video(youtube_video_url, obsidian_dir, status_updates, transcription_updates,
                       output_folder=None, use_groq=False, transcription_model="faster-whisper"):
    try:
        # Log the transcription settings
        logger.info(f"Starting process_video with model: {transcription_model}, use_groq: {use_groq}")
        
        # Update the logic to determine if we should use Groq
        use_groq = transcription_model.lower() == "groq"
        
        if use_groq and not GROQ_API_KEY:
            error_msg = "Groq API key not configured. Please set GROQ_API_KEY in your environment variables."
            logger.error(error_msg)
            await status_updates.put(json.dumps({
                "type": "status",
                "content": error_msg
            }))
            raise Exception(error_msg)

        # Extract video info first to get the title
        video_info = await extract_video_info(youtube_video_url)
        video_title = clean_filename(video_info['title'])
        
        await status_updates.put(json.dumps({
            "type": "status",
            "content": f"Starting transcription with {transcription_model}"
        }))

        # Extract video info with proper error handling
        logger.info("Extracting video info...")
        try:
            video_info = await extract_video_info(youtube_video_url)
            video_id = video_info['id']
            watch_url = video_info['watch_url']
            title = video_info['title']
            clean_title = clean_filename(title)
            
            logger.info(f"Video info extracted: {video_id} - {clean_title}")
            await status_updates.put(json.dumps({
                "type": "status",
                "content": f"Processing video: {clean_title}"
            }))
        except Exception as e:
            error_msg = f"Error extracting video info: {str(e)}"
            logger.error(error_msg)
            await status_updates.put(json.dumps({
                "type": "status",
                "content": error_msg
            }))
            raise

        # Create necessary directories in both output_folder and obsidian_dir
        mp4_dir = os.path.join(output_folder, 'mp4')
        csv_dir = os.path.join(output_folder, 'csv')
        excel_dir = os.path.join(output_folder, 'excel')
        md_dir = os.path.join(output_folder, 'md')
        pdf_dir = os.path.join(output_folder, 'pdf')

        # Create directories in output_folder
        for directory in [mp4_dir, csv_dir, excel_dir, md_dir, pdf_dir]:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory in output_folder: {directory}")

        # Create directories in obsidian_dir
        obsidian_md_dir = os.path.join(obsidian_dir, 'md')
        obsidian_csv_dir = os.path.join(obsidian_dir, 'csv')
        obsidian_excel_dir = os.path.join(obsidian_dir, 'excel')
        obsidian_pdf_dir = os.path.join(obsidian_dir, 'pdf')

        for directory in [obsidian_md_dir, obsidian_csv_dir, obsidian_excel_dir, obsidian_pdf_dir]:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory in obsidian_dir: {directory}")

        # Download audio with progress updates
        audio_output_path = os.path.join(mp4_dir, f"{clean_title}.m4a")
        await status_updates.put(json.dumps({"type": "status", "content": "Starting audio download..."}))
        logger.info(f"Downloading audio to: {audio_output_path}")
        
        # Add download progress updates
        async def progress_callback(progress):
            await status_updates.put(json.dumps({
                "type": "status",
                "content": f"Downloading audio: {progress}%"
            }))
            logger.info(f"Download progress: {progress}%")

        audio_output_path = await download_audio(youtube_video_url, audio_output_path, progress_callback)
        
        if not os.path.exists(audio_output_path):
            error_msg = f"Audio file not found at: {audio_output_path}"
            logger.error(error_msg)
            raise Exception(error_msg)

        logger.info(f"Audio downloaded successfully to: {audio_output_path}")
        
        # The audio file from yt-dlp is already in m4a format, we can use it directly
        audio_file_path = audio_output_path  # Use the downloaded m4a file directly

        # Process with either Groq or local model
        if use_groq:
            logger.info("Using Groq API for transcription")
            await status_updates.put(json.dumps({
                "type": "status",
                "content": "Starting Groq transcription..."
            }))
            
            try:
                # Use audio_output_path consistently
                transcription = await process_audio_with_groq(audio_output_path, status_updates, transcription_updates)
                logger.info("Groq transcription completed successfully")
                
                # Get video ID from URL
                video_id = youtube_video_url.split('v=')[1].split('&')[0]
                base_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Split transcription into sentences for better segmentation
                sentences = re.split(r'(?<=[.!?])\s+', transcription)
                
                # Create segments with estimated timestamps
                words_per_second = 2.5  # 150 words / 60 seconds
                current_time = 0
                segments = []
                
                for idx, sentence in enumerate(sentences):
                    # Calculate estimated duration based on word count
                    word_count = len(sentence.split())
                    duration = word_count / words_per_second
                    
                    # Create timestamp for YouTube URL
                    watch_url = f"{base_url}&t={int(current_time)}s"
                    
                    # Create segment with same format as Whisper
                    segment_dict = {
                        'watch_url': f'[Link](=HYPERLINK("{watch_url}", "{watch_url}"))',
                        'video_id': video_id,
                        'id': idx,
                        'start': format_timestamp(current_time),
                        'end': format_timestamp(current_time + duration),
                        'text': sentence.strip()
                    }
                    segments.append(segment_dict)
                    current_time += duration
                
                # Convert to DataFrame
                df_export = pd.DataFrame(segments)
                
                # Create table markdown content
                title = f"# Transcription for Video: [{video_id}](https://www.youtube.com/watch?v={video_id})\n\n"
                table_header = "| watch_url | video_id | id | start | end | text |\n"
                table_separator = "|---|---|---|---|---|\n"
                
                # Add note about estimated timestamps
                note_row = f"| | | -1 | | | Note: Timestamps are estimated for Groq API transcription |\n"
                
                # Create table content
                table_rows = df_export.apply(lambda row: 
                    f"| {row['watch_url']} | {row['video_id']} | {row['id']} | "
                    f"{row['start']} | {row['end']} | {row['text']} |\n", axis=1)
                
                table_content = title + table_header + table_separator + note_row + ''.join(table_rows)
                
                # Add "groq" to filenames
                groq_clean_title = f"{clean_title}_groq"
                
                # Save CSV and Excel with full format
                csv_path = os.path.join(csv_dir, f"{groq_clean_title}.csv")
                obsidian_csv_path = os.path.join(obsidian_csv_dir, f"{groq_clean_title}.csv")
                await save_segments_to_csv(df_export, csv_path)
                await save_segments_to_csv(df_export, obsidian_csv_path)
                logger.info(f"Saved Groq CSV files to: {csv_path} and {obsidian_csv_path}")
                
                # Save Excel with full format
                excel_path = os.path.join(excel_dir, f"{groq_clean_title}.xlsx")
                obsidian_excel_path = os.path.join(obsidian_excel_dir, f"{groq_clean_title}.xlsx")
                await save_segments_to_excel(df_export, excel_path)
                await save_segments_to_excel(df_export, obsidian_excel_path)
                logger.info(f"Saved Groq Excel files to: {excel_path} and {obsidian_excel_path}")
                
                # Save plain text markdown
                md_path = os.path.join(md_dir, f"{groq_clean_title}.md")
                obsidian_md_path = os.path.join(obsidian_md_dir, f"{groq_clean_title}.md")
                await save_text_to_markdown(transcription, md_path)
                await save_text_to_markdown(transcription, obsidian_md_path)
                logger.info(f"Saved Groq markdown files to: {md_path} and {obsidian_md_path}")
                
                # Save table markdown
                table_md_path = os.path.join(md_dir, f"{groq_clean_title}_table.md")
                obsidian_table_md_path = os.path.join(obsidian_md_dir, f"{groq_clean_title}_table.md")
                await save_text_to_markdown(table_content, table_md_path)
                await save_text_to_markdown(table_content, obsidian_table_md_path)
                logger.info(f"Saved Groq table markdown files to: {table_md_path} and {obsidian_table_md_path}")
                
                # Extract plain text for PDF (without table formatting)
                plain_text = "\n".join(sentence.strip() for sentence in sentences)

                # Save PDF with just the transcription text
                pdf_path = os.path.join(pdf_dir, f"{groq_clean_title}.pdf")
                obsidian_pdf_path = os.path.join(obsidian_pdf_dir, f"{groq_clean_title}.pdf")
                try:
                    await convert_markdown_to_pdf(md_path, pdf_path)
                    await convert_markdown_to_pdf(md_path, obsidian_pdf_path)
                    logger.info(f"Saved Groq PDF files to: {pdf_path} and {obsidian_pdf_path}")
                except Exception as pdf_error:
                    logger.error(f"Error creating Groq PDF: {str(pdf_error)}", exc_info=True)
                    await status_updates.put(json.dumps({
                        "type": "status",
                        "content": f"Warning: Could not create PDF: {str(pdf_error)}"
                    }))

                return {
                    "message": "Video processed successfully",
                    "csv_path": csv_path,
                    "excel_path": excel_path,
                    "markdown_path": md_path,
                    "table_markdown_path": table_md_path,
                    "pdf_path": pdf_path,
                    "obsidian_paths": {
                        "csv": obsidian_csv_path,
                        "excel": obsidian_excel_path,
                        "markdown": obsidian_md_path,
                        "table_markdown": obsidian_table_md_path,
                        "pdf": obsidian_pdf_path
                    },
                    "full_text": transcription
                }
            except Exception as e:
                logger.error(f"Error processing audio file with Groq API: {str(e)}", exc_info=True)
                await status_updates.put(json.dumps({
                    "type": "status",
                    "content": f"Error processing audio file with Groq API: {str(e)}"
                }))
                raise
        else:
            logger.info("Using Faster Whisper for transcription")
            await status_updates.put(json.dumps({
                "type": "status",
                "content": "Starting Faster Whisper transcription..."
            }))

            # Use local model for transcription
            segments, full_text = await transcribe_audio(
                audio_output_path, 
                status_updates, 
                transcription_updates,
                youtube_video_url
            )
            
            # Convert segments to DataFrame
            df_export = pd.DataFrame(segments)
            
            # Save CSV files with logging
            csv_path = os.path.join(csv_dir, f"{clean_title}.csv")
            obsidian_csv_path = os.path.join(obsidian_csv_dir, f"{clean_title}.csv")
            await save_segments_to_csv(df_export, csv_path)
            await save_segments_to_csv(df_export, obsidian_csv_path)
            logger.info(f"Saved CSV files to: {csv_path} and {obsidian_csv_path}")
            
            # Save Excel with full format
            excel_path = os.path.join(excel_dir, f"{clean_title}.xlsx")
            obsidian_excel_path = os.path.join(obsidian_excel_dir, f"{clean_title}.xlsx")
            await save_segments_to_excel(df_export, excel_path)
            await save_segments_to_excel(df_export, obsidian_excel_path)
            logger.info(f"Saved Excel files to: {excel_path} and {obsidian_excel_path}")
            
            # Save plain text markdown (just the transcription text)
            plain_text = "\n".join(segment['text'] for segment in segments)
            md_path = os.path.join(md_dir, f"{clean_title}.md")
            obsidian_md_path = os.path.join(obsidian_md_dir, f"{clean_title}.md")
            await save_text_to_markdown(plain_text, md_path)
            await save_text_to_markdown(plain_text, obsidian_md_path)
            logger.info(f"Saved plain text markdown files to: {md_path} and {obsidian_md_path}")
            
            # Save table markdown (with full format)
            table_md_path = os.path.join(md_dir, f"{clean_title}_table.md")
            obsidian_table_md_path = os.path.join(obsidian_md_dir, f"{clean_title}_table.md")
            table_content = df_export.to_markdown(index=False)
            await save_text_to_markdown(table_content, table_md_path)
            await save_text_to_markdown(table_content, obsidian_table_md_path)
            logger.info(f"Saved table markdown files to: {table_md_path} and {obsidian_table_md_path}")
            
            # Save PDF
            pdf_path = os.path.join(pdf_dir, f"{clean_title}.pdf")
            obsidian_pdf_path = os.path.join(obsidian_pdf_dir, f"{clean_title}.pdf")
            try:
                await convert_markdown_to_pdf(md_path, pdf_path)
                await convert_markdown_to_pdf(md_path, obsidian_pdf_path)
                logger.info(f"Saved PDF files to: {pdf_path} and {obsidian_pdf_path}")
            except Exception as pdf_error:
                logger.error(f"Error creating PDF: {str(pdf_error)}", exc_info=True)

            return {
                "message": "Video processed successfully",
                "csv_path": csv_path,
                "excel_path": excel_path,
                "markdown_path": md_path,
                "table_markdown_path": table_md_path,
                "pdf_path": pdf_path,
                "obsidian_paths": {
                    "csv": obsidian_csv_path,
                    "excel": obsidian_excel_path,
                    "markdown": obsidian_md_path,
                    "table_markdown": obsidian_table_md_path,
                    "pdf": obsidian_pdf_path
                },
                "full_text": full_text
            }

    except Exception as e:
        error_msg = f"Error in process_video: {str(e)}"
        logger.error(error_msg, exc_info=True)
        await status_updates.put(json.dumps({
            "type": "status",
            "content": error_msg
        }))
        raise

# Function to transcribe audio
async def transcribe_audio(audio_path: str, status_updates: asyncio.Queue, transcription_updates: asyncio.Queue, youtube_video_url: str):
    """
    Transcribe audio file with real-time updates and proper formatting
    
    Args:
        audio_path: Path to audio file
        status_updates: Queue for status messages
        transcription_updates: Queue for transcription segments
        youtube_video_url: Original YouTube URL for timestamps
    """
    try:
        # Send initial status
        await status_updates.put(json.dumps({
            "type": "status",
            "content": "Starting transcription..."
        }))

        # Initialize result containers
        result = []  # For structured data
        full_text = ""  # For formatted text output

        # Optimized transcription parameters for GPU
        segments_gen, info = model.transcribe(
            audio_path,
            beam_size=1,           # Reduced for speed
            best_of=1,             # Only keep best result
            temperature=0.0,        # Reduce randomness
            condition_on_previous_text=False,  # Disable for speed
            vad_filter=True,       # Keep VAD for accuracy
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=100
            )
        )
        
        # Process segments with minimal delay
        for idx, segment in enumerate(segments_gen):
            # Clean and format segment text
            segment_text = segment.text.strip()
            
            # Send transcription segment immediately for real-time updates
            await transcription_updates.put(json.dumps({
                "type": "transcription_segment",
                "content": segment_text
            }))
            logger.info(f"Sent transcription segment: {segment_text}")
            
            # Send status updates periodically
            if idx % 5 == 0:
                await status_updates.put(json.dumps({
                    "type": "status",
                    "content": f"Transcribing segment {idx + 1}"
                }))
            
            # Create timestamped YouTube URL
            video_id = youtube_video_url.split('v=')[1].split('&')[0]
            timestamp_seconds = int(segment.start)
            watch_url = f"https://www.youtube.com/watch?v={video_id}&t={timestamp_seconds}"
            
            # Format segment data for structured output
            segment_dict = {
                'watch_url': f'[Link](=HYPERLINK("{watch_url}", "{watch_url}"))',
                'video_id': video_id,
                'id': idx,
                'start': format_timestamp(segment.start),
                'end': format_timestamp(segment.end),
                'text': segment_text
            }
            result.append(segment_dict)
            
            # Format text for markdown table
            formatted_text = (
                f"| {segment_dict['watch_url']} | {segment_dict['video_id']} | "
                f"{idx} | {segment_dict['start']} | {segment_dict['end']} | "
                f"{segment_dict['text']} |\n"
            )
            full_text += formatted_text
            
            # Prevent blocking
            await asyncio.sleep(0)

        # Create final markdown document
        title = f"# Transcription for Video: [{video_id}](https://www.youtube.com/watch?v={video_id})\n\n"
        table_header = "| watch_url | video_id | id | start | end | text |\n"
        table_separator = "|---|---|---|---|---|\n"
        full_text = title + table_header + table_separator + full_text

        # Send completion messages
        await transcription_updates.put(json.dumps({
            "type": "transcription_complete",
            "content": full_text
        }))

        await status_updates.put(json.dumps({
            "type": "status",
            "content": f"Transcription completed. Total segments: {len(result)}"
        }))

        return result, full_text

    except Exception as e:
        error_msg = f"Error in transcribe_audio: {str(e)}"
        logger.error(error_msg)
        await status_updates.put(json.dumps({
            "type": "error",
            "content": error_msg
        }))
        raise

def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS.MS format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = seconds % 1
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{int(ms * 100):02d}"
    return f"{minutes:02d}:{secs:02d}.{int(ms * 100):02d}"

# Add near the top of the file after torch import
logger.info(f"CUDA available: {torch.cuda.is_available()}")
logger.info(f"CUDA device count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    logger.info(f"CUDA device name: {torch.cuda.get_device_name(0)}")
    logger.info(f"CUDA device capability: {torch.cuda.get_device_capability(0)}")

# Add this helper function near the top of the file
def should_send_progress_update(last_progress: float, current_progress: float, threshold: float = 5.0) -> bool:
    """
    Determine if a progress update should be sent based on the difference from the last update
    Args:
        last_progress: Last progress percentage that was sent
        current_progress: Current progress percentage
        threshold: Minimum percentage change required to send update (default 5%)
    Returns:
        bool: Whether update should be sent
    """
    return abs(current_progress - last_progress) >= threshold

# Modify the download_audio function
async def download_audio(youtube_url: str, output_path: str, progress_callback=None):
    """
    Download audio from YouTube URL with minimal progress updates
    """
    try:
        loop = asyncio.get_event_loop()
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
            'progress_hooks': [],
        }

        if progress_callback:
            def sync_progress_hook(d):
                if d['status'] == 'downloading':
                    try:
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        downloaded = d.get('downloaded_bytes', 0)
                        if total > 0:
                            current_progress = round((downloaded / total) * 100, 1)
                            
                            # Only send update at start and completion
                            if current_progress == 0 or current_progress >= 100:
                                loop.create_task(progress_callback(current_progress))
                                
                    except Exception as e:
                        logger.error(f"Error in progress hook: {str(e)}")
                        
            ydl_opts['progress_hooks'].append(sync_progress_hook)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading audio from: {youtube_url}")
            await loop.run_in_executor(None, lambda: ydl.download([youtube_url]))
            logger.info(f"Audio downloaded successfully to: {output_path}")
            return output_path

    except Exception as e:
        error_msg = f"Error downloading audio: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

# Add this function to handle audio chunking
async def process_audio_in_chunks(audio_file_path: str, chunk_duration_ms: int = 300000) -> str:
    """
    Process audio file in smaller chunks with compression
    Returns combined transcription text
    """
    logger.info(f"Processing audio file in chunks: {audio_file_path}")
    audio = AudioSegment.from_file(audio_file_path)
    total_duration = len(audio)
    chunks = []
    transcriptions = []

    # Split audio into smaller chunks and compress
    for i in range(0, total_duration, chunk_duration_ms):
        chunk = audio[i:i + chunk_duration_ms]
        
        # Compress audio to reduce file size
        chunk = chunk.set_frame_rate(16000)  # Reduce sample rate
        chunk = chunk.set_channels(1)        # Convert to mono
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            # Export with compression
            chunk.export(
                temp_file.name,
                format='wav',
                parameters=[
                    "-ac", "1",          # mono
                    "-ar", "16000",      # 16kHz sample rate
                    "-b:a", "64k"        # 64kbps bitrate
                ]
            )
            chunks.append(temp_file.name)
            chunk_size = os.path.getsize(temp_file.name) / (1024 * 1024)  # Size in MB
            logger.info(f"Created chunk {len(chunks)}: {temp_file.name} (Size: {chunk_size:.2f}MB)")

    try:
        # Process each chunk
        async with aiohttp.ClientSession() as session:
            for i, chunk_path in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                # Check file size before sending
                file_size = os.path.getsize(chunk_path) / (1024 * 1024)  # Size in MB
                if file_size > 25:  # Groq's limit is around 25MB
                    logger.warning(f"Chunk {i+1} is too large ({file_size:.2f}MB), skipping")
                    continue
                
                form = aiohttp.FormData()
                form.add_field('file', 
                             open(chunk_path, 'rb'),
                             filename=f'chunk_{i+1}.wav',
                             content_type='audio/wav')
                form.add_field('model', 'distil-whisper-large-v3-en')  # Corrected model name
                form.add_field('response_format', 'json')
                form.add_field('language', 'en')

                headers = {
                    'Authorization': f'Bearer {GROQ_API_KEY}',
                    'Accept': 'application/json'
                }

                try:
                    async with session.post(
                        'https://api.groq.com/openai/v1/audio/transcriptions',
                        data=form,
                        headers=headers
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"Error on chunk {i+1}: {error_text}")
                            continue
                        
                        result = await response.json()
                        transcription = result.get('text', '')
                        if transcription:
                            transcriptions.append(transcription)
                            logger.info(f"Successfully transcribed chunk {i+1}")
                except Exception as e:
                    logger.error(f"Error processing chunk {i+1}: {str(e)}")
                    continue

                # Add a small delay between chunks to avoid rate limits
                await asyncio.sleep(1)

        # Combine all transcriptions
        if not transcriptions:
            raise Exception("No chunks were successfully transcribed")
            
        full_transcription = ' '.join(transcriptions)
        logger.info("Successfully combined all transcriptions")
        return full_transcription

    finally:
        # Cleanup temporary files
        for chunk_path in chunks:
            try:
                os.remove(chunk_path)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {chunk_path}: {e}")

async def process_audio_with_groq(audio_file_path: str, status_updates: asyncio.Queue, transcription_updates: asyncio.Queue, chunk_duration_ms: int = 60000) -> str:
    """
    Process audio file using Groq API in chunks with progress updates
    """
    logger.info(f"Processing audio file with Groq: {audio_file_path}")
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured in environment")
    
    if GROQ_API_KEY == "your_groq_api_key_here":
        raise ValueError("Please update GROQ_API_KEY in your .env file with a valid API key")

    # Verify API key format
    if not GROQ_API_KEY.startswith("gsk_"):
        raise ValueError("Invalid GROQ_API_KEY format - should start with 'gsk_'")

    audio = AudioSegment.from_file(audio_file_path)
    
    # Convert to mono and set to 16kHz as per Groq requirements
    audio = audio.set_channels(1).set_frame_rate(16000)
    
    total_duration = len(audio)
    chunks = []
    transcriptions = []

    # Send initial status
    await status_updates.put(json.dumps({
        "type": "status",
        "content": "Starting Groq transcription processing..."
    }))

    try:
        # Split audio into chunks
        chunk_count = (total_duration + chunk_duration_ms - 1) // chunk_duration_ms
        for i in range(chunk_count):
            start_time = i * chunk_duration_ms
            end_time = min((i + 1) * chunk_duration_ms, total_duration)
            chunk = audio[start_time:end_time]
            
            # Send chunk processing status
            await status_updates.put(json.dumps({
                "type": "status",
                "content": f"Processing chunk {i+1} of {chunk_count}"
            }))

            # Create temporary file for chunk
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                chunk_path = temp_file.name
                chunks.append(chunk_path)
                
                # Export according to Groq requirements:
                # - 16-bit PCM WAV
                # - 16kHz sample rate
                # - Mono channel
                chunk.export(
                    chunk_path,
                    format='wav',
                    parameters=[
                        "-ac", "1",          # mono
                        "-ar", "16000",      # 16kHz sample rate
                        "-acodec", "pcm_s16le"  # 16-bit PCM
                    ]
                )
                
                chunk_size = os.path.getsize(chunk_path) / (1024 * 1024)  # Size in MB
                logger.info(f"Created chunk {i+1}: {chunk_path} (Size: {chunk_size:.2f}MB)")

                try:
                    # Process chunk with Groq API
                    headers = {
                        'Authorization': f'Bearer {GROQ_API_KEY}',
                        'Accept': 'application/json'
                    }

                    logger.info(f"Sending request to Groq API for chunk {i+1}")
                    logger.info("Using Groq API key from environment")
                    
                    async with aiohttp.ClientSession() as session:
                        logger.info(f"Sending request to Groq API for chunk {i+1}")
                        
                        # Prepare the multipart form data
                        form = aiohttp.FormData()
                        form.add_field(
                            'file',
                            open(chunk_path, 'rb'),
                            filename=f'chunk_{i+1}.wav',
                            content_type='audio/wav'
                        )
                        # Using the correct Groq model
                        form.add_field('model', 'distil-whisper-large-v3-en')
                        form.add_field('response_format', 'verbose_json')
                        form.add_field('language', 'en')
                        form.add_field('temperature', '0')
                        form.add_field('prompt', 'This is a transcription of spoken content.')
                        
                        async with session.post(
                            'https://api.groq.com/openai/v1/audio/transcriptions',
                            data=form,
                            headers=headers
                        ) as response:
                            response_text = await response.text()
                            logger.info(f"Groq API Response Status: {response.status}")
                            logger.info(f"Groq API Response: {response_text}")
                            
                            if response.status != 200:
                                logger.error(f"Groq API error on chunk {i+1}: {response_text}")
                                continue
                            
                            try:
                                result = json.loads(response_text)
                                # Handle verbose_json response format
                                transcription = result.get('text', '')
                                if not transcription and isinstance(result, dict):
                                    segments = result.get('segments', [])
                                    transcription = ' '.join(seg.get('text', '') for seg in segments)
                                
                                if transcription:
                                    transcriptions.append(transcription)
                                    # Send transcription segment update
                                    await transcription_updates.put(json.dumps({
                                        "type": "transcription_segment",
                                        "content": transcription
                                    }))
                                    logger.info(f"Successfully transcribed chunk {i+1}")

                            except Exception as e:
                                logger.error(f"Error processing chunk {i+1}: {str(e)}")
                                continue

                except Exception as e:
                    logger.error(f"Error processing chunk {i+1}: {str(e)}")
                    continue

                # Add a small delay between chunks to avoid rate limits
                await asyncio.sleep(1)

        # Check if we got any transcriptions
        if not transcriptions:
            raise Exception("No chunks were successfully transcribed")
            
        # Combine transcriptions
        full_transcription = ' '.join(transcriptions)
        
        # Send completion status
        await status_updates.put(json.dumps({
            "type": "status",
            "content": f"Groq transcription completed successfully. Total chunks processed: {len(transcriptions)}"
        }))

        # Send final transcription
        await transcription_updates.put(json.dumps({
            "type": "transcription_complete",
            "content": full_transcription
        }))

        logger.info("Successfully combined all transcriptions")
        return full_transcription

    finally:
        # Cleanup temporary files
        for chunk_path in chunks:
            try:
                os.remove(chunk_path)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {chunk_path}: {e}")

def get_best_thumbnail(thumbnails):
    """
    Get the highest resolution thumbnail from the list of thumbnails.
    Returns tuple of (url, width, height)
    """
    if not thumbnails:
        return None, None, None
        
    # Sort thumbnails by resolution (width * height) in descending order
    sorted_thumbnails = sorted(
        [t for t in thumbnails if t.get('width') and t.get('height')],
        key=lambda x: (x.get('width', 0) * x.get('height', 0)),
        reverse=True
    )
    
    if sorted_thumbnails:
        best = sorted_thumbnails[0]
        return best.get('url'), best.get('width'), best.get('height')
    
    # Fallback to first thumbnail if no resolution info
    return thumbnails[0].get('url'), None, None

async def extract_video_info(youtube_video_url: str):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writesubtitles': True,  # Enable subtitle extraction
            'writeautomaticsub': True,  # Enable automatic subtitle extraction
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ydl.extract_info(youtube_video_url, download=False)
            )
            
            # Get best thumbnail
            thumbnail_url, thumb_width, thumb_height = get_best_thumbnail(info.get('thumbnails', []))
            
            # Extract additional metadata
            video_info = {
                'id': info.get('id'),
                'title': info.get('title'),
                'description': info.get('description'),
                'duration': info.get('duration'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'channel': info.get('channel'),
                'channel_id': info.get('channel_id'),
                'channel_url': info.get('channel_url'),
                'channel_follower_count': info.get('channel_follower_count'),
                'upload_date': info.get('upload_date'),
                'categories': info.get('categories', []),
                'tags': info.get('tags', []),
                'thumbnails': info.get('thumbnails', []),
                'best_thumbnail': {
                    'url': thumbnail_url,
                    'width': thumb_width,
                    'height': thumb_height
                },
                'chapters': info.get('chapters', []),  # Video chapters/timestamps
                'subtitles': info.get('subtitles', {}),  # Available subtitles
                'automatic_captions': info.get('automatic_captions', {}),  # Auto-generated captions
                'live_status': info.get('live_status'),
                'watch_url': info.get('webpage_url') or youtube_video_url,
                'age_limit': info.get('age_limit'),
                'availability': info.get('availability'),
                'comment_count': info.get('comment_count'),
                'format': info.get('format'),  # Current video format
                'formats': info.get('formats', []),  # All available formats
                'language': info.get('language'),
                'is_live': info.get('is_live'),
                'was_live': info.get('was_live'),
                'playable_in_embed': info.get('playable_in_embed'),
                'release_timestamp': info.get('release_timestamp'),
                'release_date': info.get('release_date'),
            }
            
            # Extract chapter information in a more usable format
            if video_info['chapters']:
                video_info['formatted_chapters'] = [{
                    'title': chapter.get('title'),
                    'start_time': chapter.get('start_time'),
                    'end_time': chapter.get('end_time'),
                    'url': f"{video_info['watch_url']}&t={int(chapter.get('start_time'))}s"
                } for chapter in video_info['chapters']]
            
            return video_info
            
    except Exception as e:
        logger.error(f"Error extracting video info: {str(e)}")
        raise

async def download_video_clip(youtube_url: str, start_time: int, end_time: int, output_path: str):
    """
    Download a specific clip from a video using timestamps
    start_time and end_time should be in seconds
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',  # You can modify this to get specific quality
            'download_ranges': lambda info: [[start_time, end_time]],
            'force_keyframes_at_cuts': True,  # For more precise cuts
            'outtmpl': output_path,
            'postprocessor_args': [
                'ffmpeg', '-ss', str(start_time),
                '-t', str(end_time - start_time)
            ],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: ydl.download([youtube_url])
            )
            
        return output_path
    except Exception as e:
        logger.error(f"Error downloading clip: {str(e)}")
        raise

async def download_chapter(youtube_url: str, chapter_index: int, output_dir: str):
    """
    Download a specific chapter from a video
    """
    try:
        # First get video info to get chapter data
        video_info = await extract_video_info(youtube_url)
        
        if not video_info.get('chapters'):
            raise ValueError("No chapters found in this video")
            
        if chapter_index >= len(video_info['chapters']):
            raise ValueError(f"Chapter index {chapter_index} out of range")
            
        chapter = video_info['chapters'][chapter_index]
        start_time = chapter['start_time']
        end_time = chapter['end_time']
        chapter_title = chapter['title']
        
        # Create sanitized filename
        safe_title = clean_filename(chapter_title)
        output_path = os.path.join(output_dir, f"{safe_title}.mp4")
        
        return await download_video_clip(youtube_url, start_time, end_time, output_path)
        
    except Exception as e:
        logger.error(f"Error downloading chapter: {str(e)}")
        raise