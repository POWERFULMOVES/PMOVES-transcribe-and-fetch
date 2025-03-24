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

# Log CUDA device information for diagnostics
logger.info(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    logger.info(f"CUDA device count: {torch.cuda.device_count()}")
    logger.info(f"CUDA device name: {torch.cuda.get_device_name(0)}")
    logger.info(f"CUDA device capability: {torch.cuda.get_device_capability(0)}")

# Remove global model initialization
# Instead, create a function to get or initialize the model when needed
def get_whisper_model():
    """Get or initialize the Whisper model only when needed"""
    logger.info(f"Initializing Whisper model: {WHISPER_MODEL}")
    return WhisperModel(
        WHISPER_MODEL,
        device="cuda" if torch.cuda.is_available() else "cpu",  # Use CUDA if available
        compute_type="float16" if torch.cuda.is_available() else "int8",  # Use appropriate precision
        cpu_threads=8,           # Increase CPU threads
        num_workers=4,           # Increase workers for parallel processing
        download_root=None,
        local_files_only=False
    )

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
async def process_video(
    youtube_video_url: str,
    obsidian_dir: str,
    status_queue: asyncio.Queue,
    transcription_queue: asyncio.Queue,
    output_folder: str = None,
    model_config: dict = None
):
    """
    Process a video with configurable transcription options.
    
    Args:
        youtube_video_url: URL of the YouTube video
        obsidian_dir: Directory for Obsidian notes
        status_queue: Queue for status updates
        transcription_queue: Queue for transcription updates
        output_folder: Directory for output files
        model_config: Dictionary containing model configuration:
            - model: str, model name (faster-whisper, llama-3.3-70b, mixtral)
            - use_groq: bool, whether to use Groq API
            - api_key: str, optional Groq API key
            - model_name: str, optional full model name for Groq
    """
    try:
        if not model_config:
            model_config = {
                "model": "faster-whisper",
                "use_groq": False
            }

        # Ensure output folder exists
        if not output_folder:
            output_folder = os.path.join(os.getcwd(), "output")
        os.makedirs(output_folder, exist_ok=True)

        # Extract video info
        video_info = await extract_video_info(youtube_video_url)
        video_id = video_info['id']
        
        # Create a clean filename base
        clean_title = clean_filename(video_info['title'])
        base_filename = f"{clean_title}_{video_id}"
        
        # Download audio
        audio_path = os.path.join(output_folder, f"{base_filename}.mp3")
        audio_path = await download_audio(youtube_video_url, audio_path)

        # Process with appropriate model
        if model_config["use_groq"]:
            # For cloud processing, check for OpenAI API key
            if not os.getenv("OPENAI_API_KEY"):
                error_msg = "OpenAI API key is required for cloud transcription (OPENAI_API_KEY environment variable)"
                logger.error(error_msg)
                await status_queue.put(json.dumps({
                    "type": "error",
                    "content": error_msg
                }))
                raise ValueError(error_msg)
                
            await status_queue.put(json.dumps({
                "type": "status", 
                "content": "Using Groq API for transcription (cloud-based)"
            }))
            transcription = await process_audio_with_groq(
                audio_path,
                status_queue,
                transcription_queue,
                model_name="distil-whisper-large-v3"  # Use Whisper model on Groq
            )
        else:
            # Use local Whisper
            await status_queue.put(json.dumps({
                "type": "status",
                "content": "Using local Whisper model on GPU"
            }))
            transcription = await transcribe_audio(
                audio_path,
                status_queue,
                transcription_queue,
                youtube_video_url
            )

        # Rest of the processing remains the same...
        # ... existing code ...

    except Exception as e:
        error_msg = f"Error processing video: {str(e)}"
        logger.error(error_msg)
        await status_queue.put({
            "type": "error",
            "content": error_msg
        })
        raise

# Function to transcribe audio
async def transcribe_audio(audio_path: str, status_queue: asyncio.Queue, transcription_queue: asyncio.Queue, youtube_video_url: str):
    """
    Transcribe audio file with real-time updates and proper formatting
    
    Args:
        audio_path: Path to audio file
        status_queue: Queue for status messages
        transcription_queue: Queue for transcription segments
        youtube_video_url: Original YouTube URL for timestamps
    """
    try:
        # Verify file exists
        if not os.path.exists(audio_path):
            error_msg = f"Audio file not found: {audio_path}"
            logger.error(error_msg)
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
            raise FileNotFoundError(error_msg)
            
        # Send initial status
        await status_queue.put(json.dumps({
            "type": "status",
            "content": "Starting transcription..."
        }))

        # Initialize Whisper model only when needed
        await status_queue.put(json.dumps({
            "type": "status",
            "content": "Loading Whisper model on GPU..."
        }))
        model = get_whisper_model()
        logger.info("Whisper model loaded successfully")

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
            await transcription_queue.put(json.dumps({
                "type": "transcription_segment",
                "content": segment_text
            }))
            logger.info(f"Sent transcription segment: {segment_text}")
            
            # Send status updates periodically
            if idx % 5 == 0:
                await status_queue.put(json.dumps({
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
        await transcription_queue.put(json.dumps({
            "type": "transcription_complete",
            "content": full_text
        }))

        await status_queue.put(json.dumps({
            "type": "status",
            "content": f"Transcription completed. Total segments: {len(result)}"
        }))

        return result, full_text

    except Exception as e:
        error_msg = f"Error in transcribe_audio: {str(e)}"
        logger.error(error_msg)
        await status_queue.put(json.dumps({
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
    Returns the actual file path after potential format conversion
    """
    try:
        loop = asyncio.get_event_loop()
        output_dir = os.path.dirname(output_path)
        filename_base, _ = os.path.splitext(os.path.basename(output_path))
        
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
            
            # Check for the actual file - it might have been converted to .m4a
            m4a_path = f"{output_path}.m4a"
            actual_path = m4a_path if os.path.exists(m4a_path) else output_path
            
            logger.info(f"Audio downloaded successfully to: {actual_path}")
            return actual_path

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

async def process_audio_with_groq(
    audio_file_path: str,
    status_queue: asyncio.Queue,
    transcription_queue: asyncio.Queue,
    chunk_duration_ms: int = 60000,
    model_name: str = "distil-whisper-large-v3"
) -> str:
    """
    Process audio using OpenAI's Whisper API since Groq doesn't directly support audio transcription
    
    Args:
        audio_file_path: Path to the audio file
        status_queue: Queue for status updates
        transcription_queue: Queue for transcription updates
        chunk_duration_ms: Duration of each audio chunk in milliseconds
        model_name: Name of the Whisper model to use
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        error_msg = "OPENAI_API_KEY environment variable is not set. Cloud transcription requires an OpenAI API key."
        logger.error(error_msg)
        await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
        raise ValueError(error_msg)
        
    try:
        # Verify file exists
        if not os.path.exists(audio_file_path):
            error_msg = f"Audio file not found: {audio_file_path}"
            logger.error(error_msg)
            await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
            raise FileNotFoundError(error_msg)
            
        # Load audio file
        audio = AudioSegment.from_file(audio_file_path)
        total_chunks = math.ceil(len(audio) / chunk_duration_ms)
        transcription = []
         
        await status_queue.put(json.dumps({
            "type": "status",
            "content": f"Starting cloud transcription with Whisper model: {model_name}"
        }))
        
        async with aiohttp.ClientSession() as session:
            for i in range(total_chunks):
                chunk_num = i + 1
                await status_queue.put(json.dumps({
                    "type": "status",
                    "content": f"Processing chunk {chunk_num}/{total_chunks} using cloud API"
                }))
                
                start_ms = i * chunk_duration_ms
                end_ms = min((i + 1) * chunk_duration_ms, len(audio))
                chunk = audio[start_ms:end_ms]
                
                # Save chunk to temporary file
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    chunk_path = temp_file.name
                    chunk.export(chunk_path, format='mp3')

                try:
                    # Prepare form data
                    form = aiohttp.FormData()
                    form.add_field(
                        'file',
                        open(chunk_path, 'rb'),
                        filename='chunk.mp3',
                        content_type='audio/mp3'
                    )
                    form.add_field('model', 'whisper-1')  # OpenAI's Whisper model
                    form.add_field('response_format', 'verbose_json')
                    form.add_field('language', 'en')

                    # Make API request to OpenAI instead of Groq
                    headers = {"Authorization": f"Bearer {openai_api_key}"}
                    async with session.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        data=form,
                        headers=headers
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            error_msg = f"Error in cloud transcription chunk {chunk_num}: {error_text}"
                            logger.error(error_msg)
                            await status_queue.put(json.dumps({
                                "type": "error",
                                "content": error_msg
                            }))
                            continue
                        
                        result = await response.json()
                        segment_text = result.get('text', '')
                        if segment_text:
                            # Add to overall transcription
                            transcription.append(segment_text)
                            
                            # Also send update for real-time display
                            await transcription_queue.put(json.dumps({
                                "type": "transcription_segment",
                                "content": segment_text
                            }))
                            
                            logger.info(f"Successfully transcribed chunk {chunk_num}/{total_chunks}")
                except Exception as e:
                    error_msg = f"Error processing chunk {chunk_num}: {str(e)}"
                    logger.error(error_msg)
                    await status_queue.put(json.dumps({
                        "type": "error", 
                        "content": error_msg
                    }))
                    continue
                
                # Clean up chunk file
                try:
                    os.remove(chunk_path)
                except Exception as e:
                    logger.warning(f"Failed to remove temp file: {e}")

                # Add a small delay between chunks to avoid rate limits
                await asyncio.sleep(1)

        # Combine all transcriptions
        if not transcription:
            error_msg = "No chunks were successfully transcribed"
            logger.error(error_msg)
            await status_queue.put(json.dumps({
                "type": "error",
                "content": error_msg
            }))
            raise Exception(error_msg)
            
        full_transcription = ' '.join(transcription)
        
        # Send final complete message
        await status_queue.put(json.dumps({
            "type": "status",
            "content": "Cloud transcription completed successfully"
        }))
        
        logger.info("Successfully combined all transcription chunks")
        return full_transcription

    except Exception as e:
        error_msg = f"Error in cloud transcription: {str(e)}"
        logger.error(error_msg)
        await status_queue.put(json.dumps({"type": "error", "content": error_msg}))
        raise

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