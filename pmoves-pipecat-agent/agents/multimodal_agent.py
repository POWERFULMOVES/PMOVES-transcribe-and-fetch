"""
MultimodalAgent - Specialized agent for multimodal AI interactions

This agent provides:
- Vision and image analysis
- Image generation
- Audio processing and synthesis
- Real-time multimodal communication
- Screen sharing and analysis
- Secure file handling with validation
- Integration with multiple AI providers
- Production-ready security features
"""

import os
import asyncio
import json
import logging
import tempfile
import base64
import time
import hashlib
import re
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from pathlib import Path
import httpx
import aiofiles
from pydantic import BaseModel, Field
from PIL import Image, ImageDraw, ImageFont
import io
import mimetypes

# Vision and image processing imports
try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV not available")

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultimodalConfig(BaseModel):
    """Configuration for Multimodal agent"""

    default_vision_provider: str = Field(
        default="openai", description="Default vision provider"
    )
    default_image_gen_provider: str = Field(
        default="openai", description="Default image generation provider"
    )
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic API key"
    )
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    max_image_size: int = Field(
        default=10 * 1024 * 1024, description="Max image size in bytes"
    )
    max_video_size: int = Field(
        default=100 * 1024 * 1024, description="Max video size in bytes"
    )
    temp_dir: str = Field(default="/tmp/multimodal", description="Temporary directory")
    enable_screen_capture: bool = Field(
        default=True, description="Enable screen capture"
    )
    backend_url: str = Field(
        default="http://pmoves-backend:8000", description="Backend service URL"
    )
    litellm_url: str = Field(
        default="http://litellm-proxy:4000", description="LiteLLM proxy URL"
    )
    rate_limit_requests: int = Field(default=30, description="Requests per minute")
    max_concurrent_jobs: int = Field(default=3, description="Max concurrent jobs")

    # Model configurations
    openai_vision_model: str = Field(default="gpt-4o", description="OpenAI model for vision analysis")
    anthropic_vision_model: str = Field(default="claude-3-5-sonnet-20240620", description="Anthropic model for vision analysis")
    openai_image_gen_model: str = Field(default="dall-e-3", description="OpenAI model for image generation")
    stability_image_gen_model: str = Field(default="stable-diffusion-xl-base-1.0", description="Stability AI model for image generation")
    whisper_model_transcription: str = Field(default="whisper-1", description="Whisper model for audio transcription by multimodal agent")
    emotion_classification_model: str = Field(default="gpt-3.5-turbo", description="Model for emotion/classification tasks")


class VisionRequest(BaseModel):
    """Vision analysis request model"""

    image_url: Optional[str] = Field(default=None, description="URL to image")
    image_data: Optional[bytes] = Field(default=None, description="Raw image data")
    image_base64: Optional[str] = Field(
        default=None, description="Base64 encoded image"
    )
    prompt: str = Field(..., description="Analysis prompt")
    provider: Optional[str] = Field(default=None, description="Vision provider")
    max_tokens: int = Field(default=1000, description="Maximum response tokens")
    detail: str = Field(
        default="auto", description="Image detail level: low, high, auto"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )


class ImageGenerationRequest(BaseModel):
    """Image generation request model"""

    prompt: str = Field(..., description="Generation prompt")
    negative_prompt: Optional[str] = Field(default=None, description="Negative prompt")
    provider: Optional[str] = Field(default=None, description="Generation provider")
    size: str = Field(default="1024x1024", description="Image size")
    quality: str = Field(default="standard", description="Image quality")
    style: Optional[str] = Field(default=None, description="Image style")
    n: int = Field(default=1, description="Number of images")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )


class AudioAnalysisRequest(BaseModel):
    """Audio analysis request model"""

    audio_url: Optional[str] = Field(default=None, description="URL to audio file")
    audio_data: Optional[bytes] = Field(default=None, description="Raw audio data")
    analysis_type: str = Field(default="transcription", description="Analysis type")
    provider: Optional[str] = Field(default=None, description="Analysis provider")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )


class MultimodalResult(BaseModel):
    """Multimodal operation result model"""

    success: bool
    operation: str
    provider: str
    result_data: Optional[Dict[str, Any]] = None
    generated_content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MultimodalAgent:
    """Multimodal agent with comprehensive AI capabilities and security"""

    def __init__(self, config: MultimodalConfig):
        self.config = config
        self.status = "initializing"
        self.temp_dir = Path(config.temp_dir)

        # Ensure temp directory exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Provider availability
        self.vision_providers = {
            "openai": bool(config.openai_api_key),
            "anthropic": bool(config.anthropic_api_key),
            "google": bool(config.google_api_key),
        }

        self.image_gen_providers = {
            "openai": bool(config.openai_api_key),
            "stability": bool(config.openai_api_key),  # Uses LiteLLM proxy
            "midjourney": False,  # Would need Midjourney integration
        }

        # Supported image formats
        self.supported_image_formats = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".tiff",
        }
        self.supported_video_formats = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

        # Security and rate limiting
        self.request_counts = {}
        self.last_cleanup = time.time()
        self.active_jobs = 0

    async def initialize(self) -> bool:
        """Initialize the multimodal agent"""
        try:
            # Verify at least one provider is available
            if not any(self.vision_providers.values()) and not any(
                self.image_gen_providers.values()
            ):
                logger.error("No multimodal providers available")
                self.status = "error"
                return False

            self.status = "ready"
            logger.info(
                f"MultimodalAgent initialized with vision providers: {[k for k, v in self.vision_providers.items() if v]}"
            )
            logger.info(
                f"Image generation providers: {[k for k, v in self.image_gen_providers.items() if v]}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize MultimodalAgent: {e}")
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

    def _validate_image_security(self, image_data: bytes) -> bool:
        """Validate image for security concerns"""
        try:
            # Check file size
            if len(image_data) > self.config.max_image_size:
                logger.warning(f"Image too large: {len(image_data)} bytes")
                return False

            # Check image header signatures
            valid_signatures = [
                b"\xff\xd8\xff",  # JPEG
                b"\x89PNG\r\n\x1a\n",  # PNG
                b"GIF87a",  # GIF87a
                b"GIF89a",  # GIF89a
                b"BM",  # BMP
                b"RIFF",  # WebP (starts with RIFF)
                b"II*\x00",  # TIFF (little endian)
                b"MM\x00*",  # TIFF (big endian)
            ]

            if not any(image_data.startswith(sig) for sig in valid_signatures):
                logger.warning("Invalid image signature")
                return False

            # Try to open with PIL for additional validation
            try:
                with Image.open(io.BytesIO(image_data)) as img:
                    # Check image dimensions (prevent extremely large images)
                    if img.width > 8192 or img.height > 8192:
                        logger.warning(
                            f"Image dimensions too large: {img.width}x{img.height}"
                        )
                        return False

                    # Check for valid format
                    if img.format not in ["JPEG", "PNG", "GIF", "BMP", "WEBP", "TIFF"]:
                        logger.warning(f"Unsupported image format: {img.format}")
                        return False

            except Exception as e:
                logger.warning(f"PIL validation failed: {e}")
                return False

            return True

        except Exception as e:
            logger.error(f"Image validation error: {e}")
            return False

    def _validate_url_security(self, url: str) -> bool:
        """Validate URL for security concerns"""
        try:
            # Validate URL format
            if not re.match(r"^https?://", url):
                logger.warning(f"Invalid URL format: {url}")
                return False

            # Check for suspicious URLs
            suspicious_patterns = [
                r"localhost",
                r"127\.0\.0\.1",
                r"192\.168\.",
                r"10\.",
                r"172\.(1[6-9]|2[0-9]|3[01])\.",
                r"file://",
                r"ftp://",
                r"data:",
            ]

            if any(
                re.search(pattern, url, re.IGNORECASE)
                for pattern in suspicious_patterns
            ):
                logger.warning(f"Suspicious URL blocked: {url}")
                return False

            return True

        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False

    async def analyze_vision(
        self, request: VisionRequest, client_id: str = "anonymous"
    ) -> MultimodalResult:
        """Analyze image with vision AI with security checks"""
        try:
            # Rate limiting check
            if not self._check_rate_limit(client_id):
                return MultimodalResult(
                    success=False,
                    operation="vision_analysis",
                    provider="none",
                    error="Rate limit exceeded. Please try again later.",
                )

            # Check concurrent job limit
            if self.active_jobs >= self.config.max_concurrent_jobs:
                return MultimodalResult(
                    success=False,
                    operation="vision_analysis",
                    provider="none",
                    error="Maximum concurrent jobs reached. Please try again later.",
                )

            self.active_jobs += 1

            try:
                # Validate prompt
                if len(request.prompt) > 2000:  # Limit prompt length
                    return MultimodalResult(
                        success=False,
                        operation="vision_analysis",
                        provider="none",
                        error="Prompt too long. Maximum 2000 characters.",
                    )

                # Determine provider
                provider = await self._select_vision_provider(request.provider)
                if not provider:
                    return MultimodalResult(
                        success=False,
                        operation="vision_analysis",
                        provider="none",
                        error="No vision providers available",
                    )

                # Prepare image data
                image_data = await self._prepare_image_data(request)
                if not image_data:
                    return MultimodalResult(
                        success=False,
                        operation="vision_analysis",
                        provider=provider,
                        error="Failed to prepare image data",
                    )

                # Perform analysis based on provider
                if provider == "openai":
                    result = await self._analyze_vision_openai(image_data, request)
                elif provider == "anthropic":
                    result = await self._analyze_vision_anthropic(image_data, request)
                elif provider == "google":
                    result = await self._analyze_vision_google(image_data, request)
                else:
                    result = MultimodalResult(
                        success=False,
                        operation="vision_analysis",
                        provider=provider,
                        error=f"Unsupported provider: {provider}",
                    )

                # Store result if successful
                if result.success:
                    await self._store_multimodal_result(result, request.metadata)

                return result

            finally:
                self.active_jobs -= 1

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return MultimodalResult(
                success=False,
                operation="vision_analysis",
                provider="unknown",
                error="Internal vision analysis error",
            )

    async def _select_vision_provider(
        self, requested_provider: Optional[str]
    ) -> Optional[str]:
        """Select best available vision provider with fallback logic"""
        # If specific provider requested and available, use it
        if requested_provider and self.vision_providers.get(requested_provider, False):
            return requested_provider

        # Use default provider if available
        if self.vision_providers.get(self.config.default_vision_provider, False):
            return self.config.default_vision_provider

        # Fallback to first available provider
        available_providers = [k for k, v in self.vision_providers.items() if v]
        if available_providers:
            selected = available_providers[0]
            logger.info(f"Using fallback vision provider: {selected}")
            return selected

        return None

    async def generate_image(
        self, request: ImageGenerationRequest, client_id: str = "anonymous"
    ) -> MultimodalResult:
        """Generate image with AI with security checks"""
        try:
            # Rate limiting check
            if not self._check_rate_limit(client_id):
                return MultimodalResult(
                    success=False,
                    operation="image_generation",
                    provider="none",
                    error="Rate limit exceeded. Please try again later.",
                )

            # Check concurrent job limit
            if self.active_jobs >= self.config.max_concurrent_jobs:
                return MultimodalResult(
                    success=False,
                    operation="image_generation",
                    provider="none",
                    error="Maximum concurrent jobs reached. Please try again later.",
                )

            self.active_jobs += 1

            try:
                # Validate prompt
                if len(request.prompt) > 1000:  # Limit prompt length
                    return MultimodalResult(
                        success=False,
                        operation="image_generation",
                        provider="none",
                        error="Prompt too long. Maximum 1000 characters.",
                    )

                # Check for inappropriate content patterns
                inappropriate_patterns = [
                    r"\b(nude|naked|nsfw|explicit|sexual)\b",
                    r"\b(violence|gore|blood|death)\b",
                    r"\b(hate|racist|nazi|terrorist)\b",
                ]

                prompt_text = f"{request.prompt} {request.negative_prompt or ''}"
                if any(
                    re.search(pattern, prompt_text, re.IGNORECASE)
                    for pattern in inappropriate_patterns
                ):
                    return MultimodalResult(
                        success=False,
                        operation="image_generation",
                        provider="none",
                        error="Inappropriate content detected in prompt",
                    )

                # Determine provider
                provider = await self._select_image_gen_provider(request.provider)
                if not provider:
                    return MultimodalResult(
                        success=False,
                        operation="image_generation",
                        provider="none",
                        error="No image generation providers available",
                    )

                # Perform generation based on provider
                if provider == "openai":
                    result = await self._generate_image_openai(request)
                elif provider == "stability":
                    result = await self._generate_image_stability(request)
                else:
                    result = MultimodalResult(
                        success=False,
                        operation="image_generation",
                        provider=provider,
                        error=f"Unsupported provider: {provider}",
                    )

                # Store result if successful
                if result.success:
                    await self._store_multimodal_result(result, request.metadata)

                return result

            finally:
                self.active_jobs -= 1

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return MultimodalResult(
                success=False,
                operation="image_generation",
                provider="unknown",
                error="Internal image generation error",
            )

    async def _select_image_gen_provider(
        self, requested_provider: Optional[str]
    ) -> Optional[str]:
        """Select best available image generation provider with fallback logic"""
        # If specific provider requested and available, use it
        if requested_provider and self.image_gen_providers.get(
            requested_provider, False
        ):
            return requested_provider

        # Use default provider if available
        if self.image_gen_providers.get(self.config.default_image_gen_provider, False):
            return self.config.default_image_gen_provider

        # Fallback to first available provider
        available_providers = [k for k, v in self.image_gen_providers.items() if v]
        if available_providers:
            selected = available_providers[0]
            logger.info(f"Using fallback image generation provider: {selected}")
            return selected

        return None

    async def analyze_audio(
        self, request: AudioAnalysisRequest, client_id: str = "anonymous"
    ) -> MultimodalResult:
        """Analyze audio with AI with security checks"""
        try:
            # Rate limiting check
            if not self._check_rate_limit(client_id):
                return MultimodalResult(
                    success=False,
                    operation="audio_analysis",
                    provider="none",
                    error="Rate limit exceeded. Please try again later.",
                )

            # Check concurrent job limit
            if self.active_jobs >= self.config.max_concurrent_jobs:
                return MultimodalResult(
                    success=False,
                    operation="audio_analysis",
                    provider="none",
                    error="Maximum concurrent jobs reached. Please try again later.",
                )

            self.active_jobs += 1

            try:
                # Prepare audio file
                audio_path = await self._prepare_audio_file(request)
                if not audio_path:
                    return MultimodalResult(
                        success=False,
                        operation="audio_analysis",
                        provider="none",
                        error="Failed to prepare audio file",
                    )

                try:
                    # Route to appropriate analysis method
                    if request.analysis_type == "transcription":
                        result = await self._transcribe_audio(audio_path, request)
                    elif request.analysis_type == "emotion":
                        result = await self._analyze_audio_emotion(audio_path, request)
                    elif request.analysis_type == "classification":
                        result = await self._classify_audio(audio_path, request)
                    else:
                        result = MultimodalResult(
                            success=False,
                            operation="audio_analysis",
                            provider="none",
                            error=f"Unsupported analysis type: {request.analysis_type}",
                        )

                    return result

                finally:
                    # Always cleanup temp file
                    await self._cleanup_temp_file(audio_path)

            finally:
                self.active_jobs -= 1

        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return MultimodalResult(
                success=False,
                operation="audio_analysis",
                provider="unknown",
                error="Internal audio analysis error",
            )

    async def capture_screen(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        client_id: str = "anonymous",
    ) -> MultimodalResult:
        """Capture screen with security checks"""
        try:
            # Rate limiting check
            if not self._check_rate_limit(client_id):
                return MultimodalResult(
                    success=False,
                    operation="screen_capture",
                    provider="system",
                    error="Rate limit exceeded. Please try again later.",
                )

            if not self.config.enable_screen_capture:
                return MultimodalResult(
                    success=False,
                    operation="screen_capture",
                    provider="system",
                    error="Screen capture is disabled",
                )

            # Capture screenshot
            screenshot_path = await self._capture_screenshot(region)
            if not screenshot_path:
                return MultimodalResult(
                    success=False,
                    operation="screen_capture",
                    provider="system",
                    error="Failed to capture screenshot",
                )

            return MultimodalResult(
                success=True,
                operation="screen_capture",
                provider="system",
                file_path=str(screenshot_path),
                metadata={
                    "region": region,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return MultimodalResult(
                success=False,
                operation="screen_capture",
                provider="system",
                error="Internal screen capture error",
            )

    async def _prepare_image_data(self, request: VisionRequest) -> Optional[str]:
        """Prepare image data for analysis with security validation"""
        try:
            if request.image_base64:
                # Validate base64 image
                try:
                    image_data = base64.b64decode(request.image_base64)
                    if not self._validate_image_security(image_data):
                        return None
                    return request.image_base64
                except Exception as e:
                    logger.error(f"Invalid base64 image: {e}")
                    return None

            elif request.image_data:
                # Validate raw image data
                if not self._validate_image_security(request.image_data):
                    return None
                return base64.b64encode(request.image_data).decode()

            elif request.image_url:
                # Download and validate image from URL
                if not self._validate_url_security(request.image_url):
                    return None

                image_data = await self._download_image(request.image_url)
                if not image_data:
                    return None

                if not self._validate_image_security(image_data):
                    return None

                return base64.b64encode(image_data).decode()

            return None

        except Exception as e:
            logger.error(f"Failed to prepare image data: {e}")
            return None

    async def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL with security validation"""
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_connections=5),
                follow_redirects=True,
            ) as client:
                # Head request to check content type and size
                head_response = await client.head(url)

                content_type = head_response.headers.get("content-type", "")
                if not content_type.startswith("image/"):
                    logger.warning(f"Invalid content type: {content_type}")
                    return None

                content_length = head_response.headers.get("content-length")
                if content_length and int(content_length) > self.config.max_image_size:
                    logger.warning(f"Image too large: {content_length} bytes")
                    return None

                # Download the image
                response = await client.get(url)
                response.raise_for_status()

                if len(response.content) > self.config.max_image_size:
                    logger.warning("Image size exceeded during download")
                    return None

                return response.content

        except Exception as e:
            logger.error(f"Image download failed: {e}")
            return None

    async def _analyze_vision_openai(
        self, image_data: str, request: VisionRequest
    ) -> MultimodalResult:
        """Analyze image using OpenAI GPT-4 Vision with enhanced error handling"""
        try:
            if not self.config.openai_api_key:
                return MultimodalResult(
                    success=False,
                    operation="vision_analysis",
                    provider="openai",
                    error="OpenAI API key not configured",
                )

            # Use LiteLLM proxy for OpenAI requests
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": request.prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}",
                                        "detail": request.detail,
                                    },
                                },
                            ],
                        }
                    ],
                    "max_tokens": request.max_tokens,
                }

                # Perform analysis with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = await client.post(
                            f"{self.config.litellm_url}/chat/completions",
                            json=payload,
                            headers={
                                "Authorization": f"Bearer {os.getenv('LITELLM_MASTER_KEY', '')}"
                            },
                        )
                        response.raise_for_status()
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2**attempt)  # Exponential backoff
                            continue
                        raise e

                result_data = response.json()

                if "choices" in result_data and result_data["choices"]:
                    content = result_data["choices"][0]["message"]["content"]

                    return MultimodalResult(
                        success=True,
                        operation="vision_analysis",
                        provider="openai",
                        generated_content=content,
                        metadata={
                            "model": "gpt-4o",
                            "tokens_used": result_data.get("usage", {}).get(
                                "total_tokens", 0
                            ),
                            "detail_level": request.detail,
                        },
                    )
                else:
                    return MultimodalResult(
                        success=False,
                        operation="vision_analysis",
                        provider="openai",
                        error="No response content from OpenAI",
                    )

        except Exception as e:
            logger.error(f"OpenAI vision analysis failed: {e}")
            return MultimodalResult(
                success=False,
                operation="vision_analysis",
                provider="openai",
                error=f"OpenAI vision analysis failed: {str(e)}",
            )

    async def _analyze_vision_anthropic(
        self, image_data: str, request: VisionRequest
    ) -> MultimodalResult:
        """Analyze image using Anthropic Claude with enhanced error handling"""
        try:
            if not self.config.anthropic_api_key:
                return MultimodalResult(
                    success=False,
                    operation="vision_analysis",
                    provider="anthropic",
                    error="Anthropic API key not configured",
                )

            # Use LiteLLM proxy for Anthropic requests
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": "claude-3-5-sonnet-20241022",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": request.prompt},
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": image_data,
                                    },
                                },
                            ],
                        }
                    ],
                    "max_tokens": request.max_tokens,
                }

                # Perform analysis with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = await client.post(
                            f"{self.config.litellm_url}/chat/completions",
                            json=payload,
                            headers={
                                "Authorization": f"Bearer {os.getenv('LITELLM_MASTER_KEY', '')}"
                            },
                        )
                        response.raise_for_status()
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2**attempt)  # Exponential backoff
                            continue
                        raise e

                result_data = response.json()

                if "choices" in result_data and result_data["choices"]:
                    content = result_data["choices"][0]["message"]["content"]

                    return MultimodalResult(
                        success=True,
                        operation="vision_analysis",
                        provider="anthropic",
                        generated_content=content,
                        metadata={
                            "model": "claude-3-5-sonnet-20241022",
                            "tokens_used": result_data.get("usage", {}).get(
                                "total_tokens", 0
                            ),
                        },
                    )
                else:
                    return MultimodalResult(
                        success=False,
                        operation="vision_analysis",
                        provider="anthropic",
                        error="No response content from Anthropic",
                    )

        except Exception as e:
            logger.error(f"Anthropic vision analysis failed: {e}")
            return MultimodalResult(
                success=False,
                operation="vision_analysis",
                provider="anthropic",
                error=f"Anthropic vision analysis failed: {str(e)}",
            )

    async def _analyze_vision_google(
        self, image_data: str, request: VisionRequest
    ) -> MultimodalResult:
        """Analyze image using Google Vision API with enhanced error handling"""
        try:
            if not self.config.google_api_key:
                return MultimodalResult(
                    success=False,
                    operation="vision_analysis",
                    provider="google",
                    error="Google API key not configured",
                )

            # Placeholder for Google Vision API integration
            # This would require implementing Google Vision API calls
            return MultimodalResult(
                success=False,
                operation="vision_analysis",
                provider="google",
                error="Google Vision API not yet implemented",
            )

        except Exception as e:
            logger.error(f"Google vision analysis failed: {e}")
            return MultimodalResult(
                success=False,
                operation="vision_analysis",
                provider="google",
                error=f"Google vision analysis failed: {str(e)}",
            )

    async def _generate_image_openai(
        self, request: ImageGenerationRequest
    ) -> MultimodalResult:
        """Generate image using OpenAI DALL-E with enhanced error handling"""
        try:
            if not self.config.openai_api_key:
                return MultimodalResult(
                    success=False,
                    operation="image_generation",
                    provider="openai",
                    error="OpenAI API key not configured",
                )

            # Use LiteLLM proxy for OpenAI requests
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    "model": "dall-e-3",
                    "prompt": request.prompt,
                    "size": request.size,
                    "quality": request.quality,
                    "n": min(request.n, 1),  # DALL-E 3 only supports n=1
                }

                if request.style:
                    payload["style"] = request.style

                # Perform generation with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = await client.post(
                            f"{self.config.litellm_url}/images/generations",
                            json=payload,
                            headers={
                                "Authorization": f"Bearer {os.getenv('LITELLM_MASTER_KEY', '')}"
                            },
                        )
                        response.raise_for_status()
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2**attempt)  # Exponential backoff
                            continue
                        raise e

                result_data = response.json()

                if "data" in result_data and result_data["data"]:
                    image_url = result_data["data"][0]["url"]

                    # Download the generated image
                    image_path = await self._download_generated_image(
                        image_url, "openai_dalle"
                    )
                    if not image_path:
                        return MultimodalResult(
                            success=False,
                            operation="image_generation",
                            provider="openai",
                            error="Failed to download generated image",
                        )

                    return MultimodalResult(
                        success=True,
                        operation="image_generation",
                        provider="openai",
                        file_path=str(image_path),
                        metadata={
                            "model": "dall-e-3",
                            "size": request.size,
                            "quality": request.quality,
                            "revised_prompt": result_data["data"][0].get(
                                "revised_prompt"
                            ),
                        },
                    )
                else:
                    return MultimodalResult(
                        success=False,
                        operation="image_generation",
                        provider="openai",
                        error="No image data from OpenAI",
                    )

        except Exception as e:
            logger.error(f"OpenAI image generation failed: {e}")
            return MultimodalResult(
                success=False,
                operation="image_generation",
                provider="openai",
                error=f"OpenAI image generation failed: {str(e)}",
            )

    async def _generate_image_stability(
        self, request: ImageGenerationRequest
    ) -> MultimodalResult:
        """Generate image using Stability AI via LiteLLM proxy"""
        try:
            # Parse size
            width, height = 1024, 1024
            if "x" in request.size:
                try:
                    width, height = map(int, request.size.split("x"))
                except ValueError:
                    logger.warning(
                        f"Invalid size format: {request.size}, using default"
                    )

            # Prepare request data for Stability AI
            generation_data = {
                "model": "stable-diffusion-xl-base-1.0",
                "prompt": request.prompt,
                "width": width,
                "height": height,
                "samples": request.n,
                "steps": 30,
                "cfg_scale": 7.0,
                "style_preset": request.style or "enhance",
            }

            # Add negative prompt if provided
            if request.negative_prompt:
                generation_data["negative_prompt"] = request.negative_prompt

            # Add metadata if available
            if request.metadata:
                generation_data.update(request.metadata)

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.config.litellm_url}/v1/images/generations",
                    json=generation_data,
                    headers={
                        "Authorization": f"Bearer {self.config.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    result_data = response.json()

                    # Handle multiple generated images
                    generated_images = []
                    file_paths = []

                    for i, image_data in enumerate(result_data.get("data", [])):
                        if "url" in image_data:
                            # Download image from URL
                            image_path = await self._download_generated_image(
                                image_data["url"], f"stability_{i}"
                            )
                            if image_path:
                                generated_images.append(
                                    {
                                        "url": image_data["url"],
                                        "local_path": str(image_path),
                                        "index": i,
                                    }
                                )
                                file_paths.append(str(image_path))
                        elif "b64_json" in image_data:
                            # Handle base64 encoded image
                            try:
                                image_bytes = base64.b64decode(image_data["b64_json"])
                                timestamp = int(time.time())
                                filename = f"stability_{i}_{timestamp}.png"
                                file_path = self.temp_dir / filename

                                async with aiofiles.open(file_path, "wb") as f:
                                    await f.write(image_bytes)

                                generated_images.append(
                                    {
                                        "local_path": str(file_path),
                                        "index": i,
                                        "format": "base64",
                                    }
                                )
                                file_paths.append(str(file_path))

                            except Exception as e:
                                logger.error(f"Failed to decode base64 image: {e}")

                    if generated_images:
                        return MultimodalResult(
                            success=True,
                            operation="image_generation",
                            provider="stability",
                            file_path=file_paths[0] if file_paths else None,
                            result_data={
                                "generated_images": generated_images,
                                "prompt": request.prompt,
                                "negative_prompt": request.negative_prompt,
                                "size": f"{width}x{height}",
                                "style": request.style,
                                "model": "stable-diffusion-xl-base-1.0",
                            },
                            metadata={
                                "provider": "stability",
                                "model": "stable-diffusion-xl-base-1.0",
                                "generation_params": generation_data,
                                "image_count": len(generated_images),
                            },
                        )
                    else:
                        return MultimodalResult(
                            success=False,
                            operation="image_generation",
                            provider="stability",
                            error="No images generated",
                        )
                else:
                    error_msg = (
                        f"Stability AI generation failed: {response.status_code}"
                    )
                    try:
                        error_detail = response.json()
                        error_msg += (
                            f" - {error_detail.get('error', {}).get('message', '')}"
                        )
                    except:
                        pass

                    logger.error(error_msg)
                    return MultimodalResult(
                        success=False,
                        operation="image_generation",
                        provider="stability",
                        error=error_msg,
                    )

        except Exception as e:
            logger.error(f"Stability AI image generation failed: {e}")
            return MultimodalResult(
                success=False,
                operation="image_generation",
                provider="stability",
                error=f"Stability AI image generation failed: {str(e)}",
            )

    async def _download_generated_image(self, url: str, prefix: str) -> Optional[Path]:
        """Download generated image and save to temp directory"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()

                # Generate unique filename
                timestamp = int(time.time())
                filename = f"{prefix}_{timestamp}.png"
                file_path = self.temp_dir / filename

                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(response.content)

                logger.info(f"Generated image saved to: {file_path}")
                return file_path

        except Exception as e:
            logger.error(f"Failed to download generated image: {e}")
            return None

    async def _prepare_audio_file(
        self, request: AudioAnalysisRequest
    ) -> Optional[Path]:
        """Prepare audio file for analysis with security validation"""
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
                if not self._validate_url_security(request.audio_url):
                    return None
                return await self._download_audio_file(request.audio_url)

            return None

        except Exception as e:
            logger.error(f"Failed to prepare audio file: {e}")
            return None

    async def _download_audio_file(self, url: str) -> Optional[Path]:
        """Download audio file from URL with security validation"""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            temp_file = self.temp_dir / f"audio_{url_hash}"

            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_connections=5),
                follow_redirects=True,
            ) as client:
                # Head request to check content type and size
                head_response = await client.head(url)

                content_type = head_response.headers.get("content-type", "")
                if not content_type.startswith("audio/"):
                    logger.warning(f"Invalid content type: {content_type}")
                    return None

                content_length = head_response.headers.get("content-length")
                if content_length and int(content_length) > self.config.max_video_size:
                    logger.warning(f"Audio file too large: {content_length} bytes")
                    return None

                # Download the file
                response = await client.get(url)
                response.raise_for_status()

                if len(response.content) > self.config.max_video_size:
                    logger.warning("Audio file size exceeded during download")
                    return None

                async with aiofiles.open(temp_file, "wb") as f:
                    await f.write(response.content)

            # Determine file extension from content type
            if "mp3" in content_type:
                final_path = temp_file.with_suffix(".mp3")
            elif "wav" in content_type:
                final_path = temp_file.with_suffix(".wav")
            elif "flac" in content_type:
                final_path = temp_file.with_suffix(".flac")
            else:
                final_path = temp_file.with_suffix(".audio")

            temp_file.rename(final_path)
            return final_path

        except Exception as e:
            logger.error(f"Audio download failed: {e}")
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
            return None

    async def _transcribe_audio(
        self, audio_path: Path, request: AudioAnalysisRequest
    ) -> MultimodalResult:
        """Transcribe audio using available transcription services"""
        try:
            # Use LiteLLM proxy for transcription
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Prepare file for upload
                with open(audio_path, "rb") as audio_file:
                    files = {"file": (audio_path.name, audio_file, "audio/wav")}
                    data = {
                        "model": "whisper-1",
                        "response_format": "json",
                        "language": "en",
                    }

                    # Add metadata if available
                    if request.metadata:
                        data.update(request.metadata)

                    response = await client.post(
                        f"{self.config.litellm_url}/v1/audio/transcriptions",
                        files=files,
                        data=data,
                        headers={
                            "Authorization": f"Bearer {self.config.openai_api_key}"
                        },
                    )

                    if response.status_code == 200:
                        result_data = response.json()
                        transcription = result_data.get("text", "")

                        return MultimodalResult(
                            success=True,
                            operation="audio_transcription",
                            provider="whisper",
                            generated_content=transcription,
                            result_data={
                                "transcription": transcription,
                                "language": result_data.get("language"),
                                "duration": result_data.get("duration"),
                                "segments": result_data.get("segments", []),
                            },
                            metadata={
                                "audio_file": str(audio_path),
                                "file_size": audio_path.stat().st_size,
                                "model": "whisper-1",
                            },
                        )
                    else:
                        error_msg = f"Transcription failed: {response.status_code}"
                        logger.error(error_msg)
                        return MultimodalResult(
                            success=False,
                            operation="audio_transcription",
                            provider="whisper",
                            error=error_msg,
                        )

        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            return MultimodalResult(
                success=False,
                operation="audio_transcription",
                provider="whisper",
                error=f"Audio transcription failed: {str(e)}",
            )

    async def _analyze_audio_emotion(
        self, audio_path: Path, request: AudioAnalysisRequest
    ) -> MultimodalResult:
        """Analyze audio emotion using AI models"""
        try:
            # First transcribe the audio to get text
            transcribe_request = AudioAnalysisRequest(
                audio_data=None,
                analysis_type="transcription",
                provider=request.provider,
                metadata=request.metadata,
            )

            transcription_result = await self._transcribe_audio(
                audio_path, transcribe_request
            )

            if not transcription_result.success:
                return MultimodalResult(
                    success=False,
                    operation="audio_emotion_analysis",
                    provider="emotion",
                    error="Failed to transcribe audio for emotion analysis",
                )

            # Analyze emotion from transcription using LiteLLM
            transcription_text = transcription_result.generated_content

            emotion_prompt = f"""
            Analyze the emotional content of this transcribed speech and provide:
            1. Primary emotion (happy, sad, angry, fearful, surprised, disgusted, neutral)
            2. Emotion intensity (0.0 to 1.0)
            3. Secondary emotions if present
            4. Emotional tone indicators
            5. Confidence score (0.0 to 1.0)
            
            Transcription: "{transcription_text}"
            
            Respond in JSON format:
            {{
                "primary_emotion": "emotion_name",
                "intensity": 0.0,
                "secondary_emotions": ["emotion1", "emotion2"],
                "tone_indicators": ["indicator1", "indicator2"],
                "confidence": 0.0,
                "analysis": "brief explanation"
            }}
            """

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.config.litellm_url}/v1/chat/completions",
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert in emotional analysis of speech and text.",
                            },
                            {"role": "user", "content": emotion_prompt},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500,
                    },
                    headers={
                        "Authorization": f"Bearer {self.config.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    result_data = response.json()
                    emotion_analysis = result_data["choices"][0]["message"]["content"]

                    try:
                        # Parse JSON response
                        emotion_data = json.loads(emotion_analysis)
                    except json.JSONDecodeError:
                        # Fallback if JSON parsing fails
                        emotion_data = {
                            "primary_emotion": "neutral",
                            "intensity": 0.5,
                            "analysis": emotion_analysis,
                        }

                    return MultimodalResult(
                        success=True,
                        operation="audio_emotion_analysis",
                        provider="emotion",
                        generated_content=emotion_analysis,
                        result_data={
                            "emotion_analysis": emotion_data,
                            "transcription": transcription_text,
                            "audio_metadata": {
                                "file_path": str(audio_path),
                                "file_size": audio_path.stat().st_size,
                            },
                        },
                        metadata={"model": "gpt-3.5-turbo", "analysis_type": "emotion"},
                    )
                else:
                    error_msg = f"Emotion analysis failed: {response.status_code}"
                    return MultimodalResult(
                        success=False,
                        operation="audio_emotion_analysis",
                        provider="emotion",
                        error=error_msg,
                    )

        except Exception as e:
            logger.error(f"Audio emotion analysis failed: {e}")
            return MultimodalResult(
                success=False,
                operation="audio_emotion_analysis",
                provider="emotion",
                error=f"Audio emotion analysis failed: {str(e)}",
            )

    async def _classify_audio(
        self, audio_path: Path, request: AudioAnalysisRequest
    ) -> MultimodalResult:
        """Classify audio content using AI models"""
        try:
            # First transcribe the audio to get text
            transcribe_request = AudioAnalysisRequest(
                audio_data=None,
                analysis_type="transcription",
                provider=request.provider,
                metadata=request.metadata,
            )

            transcription_result = await self._transcribe_audio(
                audio_path, transcribe_request
            )

            if not transcription_result.success:
                return MultimodalResult(
                    success=False,
                    operation="audio_classification",
                    provider="classification",
                    error="Failed to transcribe audio for classification",
                )

            # Classify content from transcription using LiteLLM
            transcription_text = transcription_result.generated_content

            classification_prompt = f"""
            Classify this transcribed audio content into the following categories:
            
            Content Type:
            - conversation
            - presentation
            - music
            - podcast
            - interview
            - lecture
            - meeting
            - phone_call
            - other
            
            Topic Categories:
            - business
            - technology
            - education
            - entertainment
            - news
            - personal
            - health
            - finance
            - other
            
            Language Quality:
            - formal
            - informal
            - technical
            - casual
            - professional
            
            Transcription: "{transcription_text}"
            
            Respond in JSON format:
            {{
                "content_type": "type",
                "topic_category": "category",
                "language_quality": "quality",
                "confidence": 0.0,
                "keywords": ["keyword1", "keyword2"],
                "summary": "brief content summary",
                "duration_estimate": "estimated speaking duration",
                "speaker_count": "estimated number of speakers"
            }}
            """

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.config.litellm_url}/v1/chat/completions",
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert in audio content classification and analysis.",
                            },
                            {"role": "user", "content": classification_prompt},
                        ],
                        "temperature": 0.2,
                        "max_tokens": 600,
                    },
                    headers={
                        "Authorization": f"Bearer {self.config.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 200:
                    result_data = response.json()
                    classification_analysis = result_data["choices"][0]["message"][
                        "content"
                    ]

                    try:
                        # Parse JSON response
                        classification_data = json.loads(classification_analysis)
                    except json.JSONDecodeError:
                        # Fallback if JSON parsing fails
                        classification_data = {
                            "content_type": "other",
                            "topic_category": "other",
                            "language_quality": "casual",
                            "confidence": 0.5,
                            "summary": classification_analysis,
                        }

                    return MultimodalResult(
                        success=True,
                        operation="audio_classification",
                        provider="classification",
                        generated_content=classification_analysis,
                        result_data={
                            "classification": classification_data,
                            "transcription": transcription_text,
                            "audio_metadata": {
                                "file_path": str(audio_path),
                                "file_size": audio_path.stat().st_size,
                                "file_extension": audio_path.suffix,
                            },
                        },
                        metadata={
                            "model": "gpt-3.5-turbo",
                            "analysis_type": "classification",
                        },
                    )
                else:
                    error_msg = f"Audio classification failed: {response.status_code}"
                    return MultimodalResult(
                        success=False,
                        operation="audio_classification",
                        provider="classification",
                        error=error_msg,
                    )

        except Exception as e:
            logger.error(f"Audio classification failed: {e}")
            return MultimodalResult(
                success=False,
                operation="audio_classification",
                provider="classification",
                error=f"Audio classification failed: {str(e)}",
            )

    async def _capture_screenshot(
        self, region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[Path]:
        """Capture screenshot with optional region"""
        try:
            if not CV2_AVAILABLE:
                logger.error("OpenCV not available for screen capture")
                return None

            # Generate unique filename
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            file_path = self.temp_dir / filename

            # Use system screenshot command (platform-specific)
            import platform

            system = platform.system()

            if system == "Windows":
                # Use PowerShell for Windows screenshot
                cmd = [
                    "powershell",
                    "-Command",
                    f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen.Bounds | ForEach-Object {{ $bmp = New-Object System.Drawing.Bitmap($_.Width, $_.Height); $graphics = [System.Drawing.Graphics]::FromImage($bmp); $graphics.CopyFromScreen($_.X, $_.Y, 0, 0, $_.Size); $bmp.Save('{file_path}', [System.Drawing.Imaging.ImageFormat]::Png); $graphics.Dispose(); $bmp.Dispose() }}",
                ]
            elif system == "Darwin":  # macOS
                cmd = ["screencapture", "-x", str(file_path)]
            else:  # Linux
                cmd = ["import", "-window", "root", str(file_path)]

            # Execute screenshot command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0 and file_path.exists():
                logger.info(f"Screenshot captured: {file_path}")
                return file_path
            else:
                logger.error(f"Screenshot failed: {stderr.decode()}")
                return None

        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None

    async def _store_multimodal_result(
        self, result: MultimodalResult, metadata: Optional[Dict[str, Any]]
    ):
        """Store multimodal result in backend with error handling"""
        try:
            # Prepare data for storage
            storage_data = {
                "operation": result.operation,
                "provider": result.provider,
                "success": result.success,
                "generated_content": result.generated_content,
                "file_path": result.file_path,
                "result_metadata": result.metadata,
                "created_at": datetime.utcnow().isoformat(),
            }

            # Add request metadata if available
            if metadata:
                storage_data["request_metadata"] = metadata

            # Send to backend
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.config.backend_url}/api/multimodal",
                    json=storage_data,
                )

                if response.status_code == 200:
                    logger.info(f"Multimodal result stored successfully")
                else:
                    logger.warning(
                        f"Failed to store multimodal result: {response.status_code}"
                    )

        except Exception as e:
            logger.error(f"Failed to store multimodal result: {e}")

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
                "vision_providers": self.vision_providers,
                "image_gen_providers": self.image_gen_providers,
                "active_jobs": self.active_jobs,
                "max_concurrent_jobs": self.config.max_concurrent_jobs,
                "rate_limit_config": {
                    "requests_per_minute": self.config.rate_limit_requests,
                    "max_image_size": self.config.max_image_size,
                    "max_video_size": self.config.max_video_size,
                },
                "active_clients": len(self.request_counts),
                "supported_formats": {
                    "images": list(self.supported_image_formats),
                    "videos": list(self.supported_video_formats),
                },
                "screen_capture_enabled": self.config.enable_screen_capture
                and CV2_AVAILABLE,
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
                import shutil

                shutil.rmtree(self.temp_dir, ignore_errors=True)

            self.status = "stopped"
            logger.info("MultimodalAgent cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Factory function for creating MultimodalAgent
def create_multimodal_agent(config_dict: Dict[str, Any]) -> MultimodalAgent:
    """Create a MultimodalAgent instance from configuration"""
    config = MultimodalConfig(**config_dict)
    return MultimodalAgent(config)
