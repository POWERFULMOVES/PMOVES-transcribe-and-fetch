import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from faster_whisper import WhisperModel
import torch
import aiohttp
from pydantic import BaseModel

from .audio_processor import AudioProcessor
from .error_handlers import TranscriptionErrorHandler, RecoveryStrategy
from .monitoring.logger import CustomLogger, PerformanceMonitor, async_timer
from .monitoring.metrics import MetricsCollector
from .utils import (
    clean_filename,
    format_timestamp,
    save_text_to_markdown,
    convert_markdown_to_pdf
)
from .config import WHISPER_MODEL, GROQ_API_KEY

# Initialize logging and monitoring
logger = logging.getLogger(__name__)
custom_logger = CustomLogger('transcription')
performance_monitor = PerformanceMonitor(custom_logger)
metrics_collector = MetricsCollector()

# Initialize AudioProcessor
audio_processor = AudioProcessor()

# Initialize Whisper model
logger.info(f"Loading Whisper model: {WHISPER_MODEL}")
model = WhisperModel(
    WHISPER_MODEL,
    device="cuda" if torch.cuda.is_available() else "cpu",
    compute_type="float16" if torch.cuda.is_available() else "int8",
    cpu_threads=8,
    num_workers=4
)

class VideoProcessRequest(BaseModel):
    youtube_video_url: str
    obsidian_dir: str
    output_folder: str
    use_groq: bool = False
    transcription_model: str = "faster-whisper"

@async_timer(custom_logger)
async def process_video(youtube_video_url: str, obsidian_dir: str, 
                       status_updates: asyncio.Queue, transcription_updates: asyncio.Queue,
                       output_folder: str = None, use_groq: bool = False, 
                       transcription_model: str = "faster-whisper") -> Optional[Dict[str, Any]]:
    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            performance_monitor.start_timer('video_processing')

            # Extract video info
            try:
                video_info = await extract_video_info(youtube_video_url)
            except Exception as e:
                error_details = TranscriptionErrorHandler.handle_error(
                    "INVALID_VIDEO_URL",
                    e,
                    url=youtube_video_url
                )
                await status_updates.put(json.dumps({
                    "type": "error",
                    "content": error_details
                }))
                return None

            # Process audio
            try:
                audio_path = await download_audio(youtube_video_url, output_folder)
                prepared_audio = audio_processor.prepare_audio(audio_path)
            except Exception as e:
                error_details = TranscriptionErrorHandler.handle_error(
                    "AUDIO_PROCESSING",
                    e,
                    video_id=video_info['id']
                )
                if await RecoveryStrategy.handle_audio_processing_error(error_details, audio_processor):
                    retry_count += 1
                    continue
                await status_updates.put(json.dumps({
                    "type": "error",
                    "content": error_details
                }))
                return None

            # Transcribe
            try:
                if use_groq:
                    result = await process_audio_with_groq(
                        prepared_audio,
                        status_updates,
                        transcription_updates
                    )
                else:
                    result = await transcribe_audio(
                        prepared_audio,
                        status_updates,
                        transcription_updates,
                        youtube_video_url
                    )

                duration = performance_monitor.stop_timer('video_processing')
                metrics_collector.add_metric('transcription_duration', duration)

                return result

            except Exception as e:
                error_code = "API_CONNECTION" if "connection" in str(e).lower() else "INVALID_RESPONSE"
                error_details = TranscriptionErrorHandler.handle_error(
                    error_code,
                    e,
                    video_id=video_info['id']
                )
                
                if error_code == "API_CONNECTION" and await RecoveryStrategy.handle_api_connection_error(error_details, retry_count):
                    retry_count += 1
                    continue
                
                await status_updates.put(json.dumps({
                    "type": "error",
                    "content": error_details
                }))
                return None

        except Exception as e:
            error_details = TranscriptionErrorHandler.handle_error(
                "UNKNOWN_ERROR",
                e,
                retry_count=retry_count
            )
            await status_updates.put(json.dumps({
                "type": "error",
                "content": error_details
            }))
            return None

    error_details = TranscriptionErrorHandler.handle_error(
        "UNKNOWN_ERROR",
        message="Maximum retry attempts exceeded"
    )
    await status_updates.put(json.dumps({
        "type": "error",
        "content": error_details
    }))
    return None

# Rest of the file remains largely the same, but with added monitoring and error handling...