"""
TranscribeAgent - Specialized agent for audio/video transcription

This agent provides:
- Multi-provider transcription (Groq, OpenAI Whisper, Deepgram)
- Real-time audio processing
- Video audio extraction
- Speaker diarization
- Secure file handling with validation
- Integration with PMOVES backend services
- Production-ready security features
"""

import os
import asyncio
import json
import logging
import tempfile
import shutil
import time
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
import httpx
import aiofiles
from pydantic import BaseModel, Field
import subprocess
import mimetypes
import re

# Audio processing imports
try:
    import whisper

    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("Whisper not available")

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscribeConfig(BaseModel):
    """Configuration for Transcribe agent"""

    default_provider: str = Field(
        default="groq", description="Default transcription provider"
    )
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    deepgram_api_key: Optional[str] = Field(
        default=None, description="Deepgram API key"
    )
    whisper_model: str = Field(default="base", description="Whisper model size")
    max_file_size: int = Field(
        default=100 * 1024 * 1024, description="Max file size in bytes"
    )
    temp_dir: str = Field(default="/tmp/transcribe", description="Temporary directory")
    enable_diarization: bool = Field(
        default=True, description="Enable speaker diarization"
    )
    chunk_duration: int = Field(
        default=30, description="Audio chunk duration in seconds"
    )
    backend_url: str = Field(
        default="http://pmoves-backend:8000", description="Backend service URL"
    )
    rate_limit_requests: int = Field(default=50, description="Requests per minute")
    max_concurrent_jobs: int = Field(
        default=5, description="Max concurrent transcription jobs"
    )

    # Model configurations
    groq_transcription_model: str = Field(default="whisper-large-v3", description="Groq model for transcription")
    openai_transcription_model: str = Field(default="whisper-1", description="OpenAI model for transcription")
    deepgram_transcription_model: str = Field(default="nova-2", description="Deepgram model for transcription")


class TranscriptionRequest(BaseModel):
    """Transcription request model"""

    audio_url: Optional[str] = Field(
        default=None, description="URL to audio/video file"
    )
    audio_data: Optional[bytes] = Field(default=None, description="Raw audio data")
    provider: Optional[str] = Field(default=None, description="Transcription provider")
    language: Optional[str] = Field(default="auto", description="Audio language")
    enable_diarization: bool = Field(
        default=True, description="Enable speaker diarization"
    )
    output_format: str = Field(
        default="segments", description="Output format: segments, full, both"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )


class TranscriptionResult(BaseModel):
    """Transcription result model"""

    success: bool
    provider: str
    language: Optional[str] = None
    duration: Optional[float] = None
    segments: Optional[List[Dict[str, Any]]] = None
    full_text: Optional[str] = None
    speakers: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TranscribeAgent:
    """Transcription agent with multi-provider support and security features"""

    def __init__(self, config: TranscribeConfig):
        self.config = config
        self.status = "initializing"
        self.temp_dir = Path(config.temp_dir)
        self.whisper_model = None

        # Ensure temp directory exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Provider availability
        self.providers = {
            "groq": bool(config.groq_api_key),
            "openai": bool(config.openai_api_key),
            "deepgram": bool(config.deepgram_api_key),
            "whisper": WHISPER_AVAILABLE,
        }

        # Security and rate limiting
        self.request_counts = {}
        self.last_cleanup = time.time()
        self.active_jobs = 0

        # Supported file formats
        self.supported_audio_formats = {
            ".mp3",
            ".wav",
            ".flac",
            ".m4a",
            ".aac",
            ".ogg",
            ".wma",
        }
        self.supported_video_formats = {
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
            ".webm",
            ".flv",
            ".wmv",
        }

    async def initialize(self) -> bool:
        """Initialize the transcription agent"""
        try:
            # Load Whisper model if available and configured
            if WHISPER_AVAILABLE and self.providers["whisper"]:
                try:
                    self.whisper_model = whisper.load_model(self.config.whisper_model)
                    logger.info(
                        f"Whisper model '{self.config.whisper_model}' loaded successfully"
                    )
                except Exception as e:
                    logger.warning(f"Failed to load Whisper model: {e}")
                    self.providers["whisper"] = False

            # Verify at least one provider is available
            if not any(self.providers.values()):
                logger.error("No transcription providers available")
                self.status = "error"
                return False

            self.status = "ready"
            logger.info(
                f"TranscribeAgent initialized with providers: {[k for k, v in self.providers.items() if v]}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize TranscribeAgent: {e}")
            self.status = "error"
            return False

    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        current_time = time.time()

        # Cleanup old entries every 5 minutes
        if current_time - self.last_cleanup > 300:
            self._cleanup_rate_limit_data()
            self.last_cleanup = current_time

        # Get current minute window
        minute_window = int(current_time // 60)

        if client_id not in self.request_counts:
            self.request_counts[client_id] = {}

        # Count requests in current minute
        current_requests = self.request_counts[client_id].get(minute_window, 0)

        if current_requests >= self.config.rate_limit_requests:
            return False

        # Increment counter
        self.request_counts[client_id][minute_window] = current_requests + 1
        return True

    def _cleanup_rate_limit_data(self):
        """Remove old rate limit data"""
        current_time = time.time()
        current_minute = int(current_time // 60)

        for client_id in list(self.request_counts.keys()):
            # Remove entries older than 2 minutes
            self.request_counts[client_id] = {
                minute: count
                for minute, count in self.request_counts[client_id].items()
                if minute >= current_minute - 2
            }

            # Remove empty client entries
            if not self.request_counts[client_id]:
                del self.request_counts[client_id]

    def _validate_file_security(self, file_path: Path) -> bool:
        """Validate file for security concerns"""
        try:
            # Check file size
            if file_path.stat().st_size > self.config.max_file_size:
                logger.warning(f"File too large: {file_path.stat().st_size} bytes")
                return False

            # Check file extension
            file_ext = file_path.suffix.lower()
            if file_ext not in (
                self.supported_audio_formats | self.supported_video_formats
            ):
                logger.warning(f"Unsupported file format: {file_ext}")
                return False

            # Check MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type:
                if not (
                    mime_type.startswith("audio/") or mime_type.startswith("video/")
                ):
                    logger.warning(f"Invalid MIME type: {mime_type}")
                    return False

            # Basic file header validation
            with open(file_path, "rb") as f:
                header = f.read(16)

            # Check for common audio/video file signatures
            valid_signatures = [
                b"\xff\xfb",  # MP3
                b"\xff\xf3",  # MP3
                b"\xff\xf2",  # MP3
                b"RIFF",  # WAV
                b"fLaC",  # FLAC
                b"\x00\x00\x00\x20ftypmp4",  # MP4 (partial)
                b"\x00\x00\x00\x18ftypmp4",  # MP4 (partial)
                b"OggS",  # OGG
            ]

            if not any(header.startswith(sig) for sig in valid_signatures):
                # For MP4 and other container formats, check ftyp box
                if b"ftyp" not in header[:20]:
                    logger.warning(f"Invalid file signature for {file_path}")
                    return False

            return True

        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False

    async def transcribe(
        self, request: TranscriptionRequest, client_id: str = "anonymous"
    ) -> TranscriptionResult:
        """Main transcription method with security checks"""
        try:
            # Rate limiting check
            if not self._check_rate_limit(client_id):
                return TranscriptionResult(
                    success=False,
                    provider="none",
                    error="Rate limit exceeded. Please try again later.",
                )

            # Check concurrent job limit
            if self.active_jobs >= self.config.max_concurrent_jobs:
                return TranscriptionResult(
                    success=False,
                    provider="none",
                    error="Maximum concurrent jobs reached. Please try again later.",
                )

            self.active_jobs += 1

            try:
                # Determine provider with fallback
                provider = await self._select_provider(request.provider)
                if not provider:
                    return TranscriptionResult(
                        success=False,
                        provider="none",
                        error="No transcription providers available",
                    )

                # Get audio file path
                audio_path = await self._prepare_audio_file(request)
                if not audio_path:
                    return TranscriptionResult(
                        success=False,
                        provider=provider,
                        error="Failed to prepare audio file",
                    )

                # Validate file security
                if not self._validate_file_security(audio_path):
                    await self._cleanup_temp_file(audio_path)
                    return TranscriptionResult(
                        success=False,
                        provider=provider,
                        error="File validation failed",
                    )

                try:
                    # Perform transcription based on provider
                    if provider == "groq":
                        result = await self._transcribe_groq(audio_path, request)
                    elif provider == "openai":
                        result = await self._transcribe_openai(audio_path, request)
                    elif provider == "deepgram":
                        result = await self._transcribe_deepgram(audio_path, request)
                    elif provider == "whisper":
                        result = await self._transcribe_whisper(audio_path, request)
                    else:
                        result = TranscriptionResult(
                            success=False,
                            provider=provider,
                            error=f"Unsupported provider: {provider}",
                        )

                    # Store transcription if successful
                    if result.success:
                        await self._store_transcription(result, request)

                    return result

                finally:
                    # Always cleanup temp file
                    await self._cleanup_temp_file(audio_path)

            finally:
                self.active_jobs -= 1

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return TranscriptionResult(
                success=False,
                provider="unknown",
                error="Internal transcription error",
            )

    async def _select_provider(
        self, requested_provider: Optional[str]
    ) -> Optional[str]:
        """Select best available provider with fallback logic"""
        # If specific provider requested and available, use it
        if requested_provider and self.providers.get(requested_provider, False):
            return requested_provider

        # Use default provider if available
        if self.providers.get(self.config.default_provider, False):
            return self.config.default_provider

        # Fallback to first available provider
        available_providers = [k for k, v in self.providers.items() if v]
        if available_providers:
            selected = available_providers[0]
            logger.info(f"Using fallback provider: {selected}")
            return selected

        return None

    async def _prepare_audio_file(
        self, request: TranscriptionRequest
    ) -> Optional[Path]:
        """Prepare audio file for transcription with security validation"""
        try:
            if request.audio_data:
                # Handle raw audio data
                file_hash = hashlib.md5(request.audio_data).hexdigest()
                temp_file = self.temp_dir / f"audio_{file_hash}.wav"

                async with aiofiles.open(temp_file, "wb") as f:
                    await f.write(request.audio_data)

                return temp_file

            elif request.audio_url:
                # Download from URL
                return await self._download_audio(request.audio_url)

            return None

        except Exception as e:
            logger.error(f"Failed to prepare audio file: {e}")
            return None

    async def _download_audio(self, url: str) -> Optional[Path]:
        """Download audio/video file with security validation"""
        try:
            # Validate URL format
            if not re.match(r"^https?://", url):
                logger.warning(f"Invalid URL format: {url}")
                return None

            # Check for suspicious URLs
            suspicious_patterns = [
                r"localhost",
                r"127\.0\.0\.1",
                r"192\.168\.",
                r"10\.",
                r"172\.(1[6-9]|2[0-9]|3[01])\.",
                r"file://",
                r"ftp://",
            ]

            if any(
                re.search(pattern, url, re.IGNORECASE)
                for pattern in suspicious_patterns
            ):
                logger.warning(f"Suspicious URL blocked: {url}")
                return None

            # Try video download first (handles both video and audio)
            video_path = await self._download_video_audio(url)
            if video_path:
                return video_path

            # Fallback to direct audio download
            return await self._download_direct_audio(url)

        except Exception as e:
            logger.error(f"Audio download failed: {e}")
            return None

    async def _download_video_audio(self, url: str) -> Optional[Path]:
        """Download video and extract audio using yt-dlp with security measures"""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            output_path = self.temp_dir / f"video_audio_{url_hash}.%(ext)s"

            # yt-dlp command with security options
            cmd = [
                "yt-dlp",
                "--extract-audio",
                "--audio-format",
                "wav",
                "--audio-quality",
                "0",
                "--no-playlist",
                "--max-filesize",
                f"{self.config.max_file_size}",
                "--socket-timeout",
                "30",
                "--retries",
                "3",
                "--no-check-certificate",  # Only if necessary
                "--user-agent",
                "Mozilla/5.0 (compatible; PMOVES-TranscribeAgent)",
                "-o",
                str(output_path),
                url,
            ]

            # Run with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=300,  # 5 minute timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logger.error(f"yt-dlp timeout for URL: {url}")
                return None

            if process.returncode == 0:
                # Find the downloaded file
                pattern = f"video_audio_{url_hash}.*"
                for file_path in self.temp_dir.glob(pattern):
                    if file_path.is_file():
                        logger.info(f"Successfully downloaded audio from: {url}")
                        return file_path

            logger.warning(f"yt-dlp failed for URL: {url}, stderr: {stderr.decode()}")
            return None

        except Exception as e:
            logger.error(f"Video audio download failed: {e}")
            return None

    async def _download_direct_audio(self, url: str) -> Optional[Path]:
        """Download audio file directly with security validation"""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            temp_file = self.temp_dir / f"direct_audio_{url_hash}"

            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_connections=5),
                follow_redirects=True,
            ) as client:
                # Head request to check content type and size
                head_response = await client.head(url)

                content_type = head_response.headers.get("content-type", "")
                if not (
                    content_type.startswith("audio/")
                    or content_type.startswith("video/")
                ):
                    logger.warning(f"Invalid content type: {content_type}")
                    return None

                content_length = head_response.headers.get("content-length")
                if content_length and int(content_length) > self.config.max_file_size:
                    logger.warning(f"File too large: {content_length} bytes")
                    return None

                # Download the file
                async with client.stream("GET", url) as response:
                    response.raise_for_status()

                    downloaded_size = 0
                    async with aiofiles.open(temp_file, "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            downloaded_size += len(chunk)
                            if downloaded_size > self.config.max_file_size:
                                logger.warning("File size exceeded during download")
                                await f.close()
                                temp_file.unlink(missing_ok=True)
                                return None
                            await f.write(chunk)

            # Determine file extension from content type
            if content_type.startswith("audio/"):
                if "mp3" in content_type:
                    final_path = temp_file.with_suffix(".mp3")
                elif "wav" in content_type:
                    final_path = temp_file.with_suffix(".wav")
                elif "flac" in content_type:
                    final_path = temp_file.with_suffix(".flac")
                else:
                    final_path = temp_file.with_suffix(".audio")
            else:
                final_path = temp_file.with_suffix(".video")

            temp_file.rename(final_path)
            logger.info(f"Successfully downloaded: {url}")
            return final_path

        except Exception as e:
            logger.error(f"Direct audio download failed: {e}")
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
            return None

    async def _transcribe_groq(
        self, audio_path: Path, request: TranscriptionRequest
    ) -> TranscriptionResult:
        """Transcribe using Groq API with enhanced error handling"""
        try:
            if not self.config.groq_api_key:
                return TranscriptionResult(
                    success=False,
                    provider="groq",
                    error="Groq API key not configured",
                )

            # Import Groq client
            try:
                from groq import AsyncGroq
            except ImportError:
                return TranscriptionResult(
                    success=False,
                    provider="groq",
                    error="Groq client not available",
                )

            client = AsyncGroq(api_key=self.config.groq_api_key)

            # Read audio file
            async with aiofiles.open(audio_path, "rb") as audio_file:
                audio_data = await audio_file.read()

            # Prepare transcription parameters
            transcription_params = {
                "file": (audio_path.name, audio_data, "audio/wav"),
                "model": self.config.groq_transcription_model,
                "response_format": "verbose_json",
                "timestamp_granularities": ["segment"],
            }

            if request.language and request.language != "auto":
                transcription_params["language"] = request.language

            # Perform transcription with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await client.audio.transcriptions.create(
                        **transcription_params
                    )
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        continue
                    raise e

            # Process response
            segments = []
            if hasattr(response, "segments") and response.segments:
                for segment in response.segments:
                    segments.append(
                        {
                            "start": segment.start,
                            "end": segment.end,
                            "text": segment.text.strip(),
                            "confidence": getattr(segment, "avg_logprob", 0.0),
                        }
                    )

            full_text = response.text if hasattr(response, "text") else ""
            language = (
                response.language if hasattr(response, "language") else request.language
            )
            duration = response.duration if hasattr(response, "duration") else None

            return TranscriptionResult(
                success=True,
                provider="groq",
                language=language,
                duration=duration,
                segments=segments,
                full_text=full_text,
                metadata={
                    "model": self.config.groq_transcription_model,
                    "file_size": len(audio_data),
                    "file_name": audio_path.name,
                },
            )

        except Exception as e:
            logger.error(f"Groq transcription failed: {e}")
            return TranscriptionResult(
                success=False,
                provider="groq",
                error=f"Groq transcription failed: {str(e)}",
            )

    async def _transcribe_openai(
        self, audio_path: Path, request: TranscriptionRequest
    ) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper API with enhanced error handling"""
        try:
            if not self.config.openai_api_key:
                return TranscriptionResult(
                    success=False,
                    provider="openai",
                    error="OpenAI API key not configured",
                )

            # Import OpenAI client
            try:
                from openai import AsyncOpenAI
            except ImportError:
                return TranscriptionResult(
                    success=False,
                    provider="openai",
                    error="OpenAI client not available",
                )

            client = AsyncOpenAI(api_key=self.config.openai_api_key)

            # Read audio file
            async with aiofiles.open(audio_path, "rb") as audio_file:
                audio_data = await audio_file.read()

            # Prepare transcription parameters
            transcription_params = {
                "file": (audio_path.name, audio_data, "audio/wav"),
                "model": self.config.openai_transcription_model,
                "response_format": "verbose_json",
                "timestamp_granularities": ["segment"],
            }

            if request.language and request.language != "auto":
                transcription_params["language"] = request.language

            # Perform transcription with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await client.audio.transcriptions.create(
                        **transcription_params
                    )
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        continue
                    raise e

            # Process response
            segments = []
            if hasattr(response, "segments") and response.segments:
                for segment in response.segments:
                    segments.append(
                        {
                            "start": segment.start,
                            "end": segment.end,
                            "text": segment.text.strip(),
                            "confidence": getattr(segment, "avg_logprob", 0.0),
                        }
                    )

            full_text = response.text if hasattr(response, "text") else ""
            language = (
                response.language if hasattr(response, "language") else request.language
            )
            duration = response.duration if hasattr(response, "duration") else None

            return TranscriptionResult(
                success=True,
                provider="openai",
                language=language,
                duration=duration,
                segments=segments,
                full_text=full_text,
                metadata={
                    "model": self.config.openai_transcription_model,
                    "file_size": len(audio_data),
                    "file_name": audio_path.name,
                },
            )

        except Exception as e:
            logger.error(f"OpenAI transcription failed: {e}")
            return TranscriptionResult(
                success=False,
                provider="openai",
                error=f"OpenAI transcription failed: {str(e)}",
            )

    async def _transcribe_deepgram(
        self, audio_path: Path, request: TranscriptionRequest
    ) -> TranscriptionResult:
        """Transcribe using Deepgram API with enhanced error handling"""
        try:
            if not self.config.deepgram_api_key:
                return TranscriptionResult(
                    success=False,
                    provider="deepgram",
                    error="Deepgram API key not configured",
                )

            # Read audio file
            async with aiofiles.open(audio_path, "rb") as audio_file:
                audio_data = await audio_file.read()

            # Prepare request
            url = "https://api.deepgram.com/v1/listen"
            headers = {
                "Authorization": f"Token {self.config.deepgram_api_key}",
                "Content-Type": "audio/wav",
            }

            params = {
                "model": self.config.deepgram_transcription_model,
                "smart_format": "true",
                "punctuate": "true",
                "diarize": "true" if request.enable_diarization else "false",
                "utterances": "true",
                "paragraphs": "true",
            }

            if request.language and request.language != "auto":
                params["language"] = request.language

            # Perform transcription with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient(timeout=300.0) as client:
                        response = await client.post(
                            url,
                            headers=headers,
                            params=params,
                            content=audio_data,
                        )
                        response.raise_for_status()
                        break
                except Exception as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        continue
                    raise e

            result_data = response.json()

            # Process response
            segments = []
            speakers = []
            full_text = ""

            if "results" in result_data and "channels" in result_data["results"]:
                channel = result_data["results"]["channels"][0]

                if "alternatives" in channel and channel["alternatives"]:
                    alternative = channel["alternatives"][0]
                    full_text = alternative.get("transcript", "")

                    # Process paragraphs/utterances for segments
                    if (
                        "paragraphs" in alternative
                        and "paragraphs" in alternative["paragraphs"]
                    ):
                        for paragraph in alternative["paragraphs"]["paragraphs"]:
                            for sentence in paragraph.get("sentences", []):
                                segments.append(
                                    {
                                        "start": sentence.get("start", 0),
                                        "end": sentence.get("end", 0),
                                        "text": sentence.get("text", "").strip(),
                                        "confidence": sentence.get("confidence", 0.0),
                                        "speaker": sentence.get("speaker", 0),
                                    }
                                )

                    # Extract speaker information
                    if "words" in alternative:
                        speaker_set = set()
                        for word in alternative["words"]:
                            if "speaker" in word:
                                speaker_set.add(f"Speaker {word['speaker']}")
                        speakers = list(speaker_set)

            metadata = result_data.get("metadata", {})
            duration = metadata.get("duration")
            language = metadata.get("detected_language", request.language)

            return TranscriptionResult(
                success=True,
                provider="deepgram",
                language=language,
                duration=duration,
                segments=segments,
                full_text=full_text,
                speakers=speakers,
                metadata={
                    "model": self.config.deepgram_transcription_model,
                    "file_size": len(audio_data),
                    "file_name": audio_path.name,
                    "deepgram_metadata": metadata,
                },
            )

        except Exception as e:
            logger.error(f"Deepgram transcription failed: {e}")
            return TranscriptionResult(
                success=False,
                provider="deepgram",
                error=f"Deepgram transcription failed: {str(e)}",
            )

    async def _transcribe_whisper(
        self, audio_path: Path, request: TranscriptionRequest
    ) -> TranscriptionResult:
        """Transcribe using local Whisper model"""
        try:
            if not self.whisper_model:
                return TranscriptionResult(
                    success=False,
                    provider="whisper",
                    error="Whisper model not loaded",
                )

            # Run Whisper in thread pool to avoid blocking
            def run_whisper():
                try:
                    result = self.whisper_model.transcribe(
                        str(audio_path),
                        language=request.language
                        if request.language != "auto"
                        else None,
                        task="transcribe",
                        verbose=False,
                    )
                    return result
                except Exception as e:
                    logger.error(f"Whisper transcription error: {e}")
                    return None

            # Execute with timeout
            result = await asyncio.get_event_loop().run_in_executor(None, run_whisper)

            if not result:
                return TranscriptionResult(
                    success=False,
                    provider="whisper",
                    error="Whisper transcription failed",
                )

            # Process segments
            segments = []
            for segment in result.get("segments", []):
                segments.append(
                    {
                        "start": segment.get("start", 0),
                        "end": segment.get("end", 0),
                        "text": segment.get("text", "").strip(),
                        "confidence": segment.get("avg_logprob", 0.0),
                    }
                )

            return TranscriptionResult(
                success=True,
                provider="whisper",
                language=result.get("language"),
                segments=segments,
                full_text=result.get("text", ""),
                metadata={
                    "model": self.config.whisper_model,
                    "file_name": audio_path.name,
                },
            )

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return TranscriptionResult(
                success=False,
                provider="whisper",
                error=f"Whisper transcription failed: {str(e)}",
            )

    async def _store_transcription(
        self, result: TranscriptionResult, request: TranscriptionRequest
    ):
        """Store transcription result in backend with error handling"""
        try:
            # Prepare data for storage
            storage_data = {
                "provider": result.provider,
                "language": result.language,
                "duration": result.duration,
                "full_text": result.full_text,
                "segments": result.segments,
                "speakers": result.speakers,
                "metadata": result.metadata,
                "created_at": datetime.utcnow().isoformat(),
            }

            # Add request metadata if available
            if request.metadata:
                storage_data["request_metadata"] = request.metadata

            # Send to backend
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.config.backend_url}/api/transcriptions",
                    json=storage_data,
                )

                if response.status_code == 200:
                    logger.info(f"Transcription stored successfully")
                else:
                    logger.warning(
                        f"Failed to store transcription: {response.status_code}"
                    )

        except Exception as e:
            logger.error(f"Failed to store transcription: {e}")

    async def _cleanup_temp_file(self, file_path: Path):
        """Safely cleanup temporary files"""
        try:
            if file_path and file_path.exists():
                file_path.unlink()
                logger.debug(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup temp file {file_path}: {e}")

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive agent health status"""
        try:
            return {
                "status": self.status,
                "providers": self.providers,
                "active_jobs": self.active_jobs,
                "max_concurrent_jobs": self.config.max_concurrent_jobs,
                "rate_limit_config": {
                    "requests_per_minute": self.config.rate_limit_requests,
                    "max_file_size": self.config.max_file_size,
                },
                "active_clients": len(self.request_counts),
                "supported_formats": {
                    "audio": list(self.supported_audio_formats),
                    "video": list(self.supported_video_formats),
                },
                "whisper_model": self.config.whisper_model
                if self.whisper_model
                else None,
                "temp_dir": str(self.temp_dir),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def cleanup(self):
        """Cleanup resources and temporary files"""
        try:
            # Wait for active jobs to complete (with timeout)
            timeout = 30  # 30 seconds
            start_time = time.time()

            while self.active_jobs > 0 and (time.time() - start_time) < timeout:
                await asyncio.sleep(1)

            # Cleanup temp directory
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)

            self.status = "stopped"
            logger.info("TranscribeAgent cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Factory function for creating TranscribeAgent
def create_transcribe_agent(config_dict: Dict[str, Any]) -> TranscribeAgent:
    """Create a TranscribeAgent instance from configuration"""
    config = TranscribeConfig(**config_dict)
    return TranscribeAgent(config)
