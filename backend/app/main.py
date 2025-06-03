import os
import sys  # Keep sys import first for platform check
import logging

# --- Event Loop Policy (MUST BE SET BEFORE ASYNCIO IMPORT) ---
_event_loop_policy_set = False
if sys.platform == "win32":
    try:
        # Temporarily import asyncio just for this setting
        import asyncio as _asyncio_temp

        _asyncio_temp.set_event_loop_policy(
            _asyncio_temp.WindowsProactorEventLoopPolicy()
        )
        _event_loop_policy_set = True
        # We will log this after full asyncio and logging are imported
    except ImportError:
        # Fallback or error logging if asyncio cannot be imported here
        print("CRITICAL: Could not import asyncio to set event loop policy.")
    finally:
        # Ensure our temporary import doesn't linger
        if "_asyncio_temp" in locals():
            del _asyncio_temp

import asyncio  # Now import asyncio for real
# Import logging

# Rich logging for pretty terminal output
try:
    from rich.logging import RichHandler

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() in ["true", "1", "yes"]
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "pmoves_backend.log")

# Set up root logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove any default handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Console handler (always enabled)
if RICH_AVAILABLE:
    console_handler = RichHandler(
        rich_tracebacks=True, show_time=True, show_level=True, show_path=False
    )
    console_handler.setFormatter(logging.Formatter("%(message)s"))
else:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

logger.addHandler(console_handler)

# File handler (optional, based on env)
if LOG_TO_FILE:
    file_handler = logging.FileHandler(LOG_FILE_NAME, mode="a")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

logger.info(
    f"Logging initialized. Console: always. File: {'enabled' if LOG_TO_FILE else 'disabled'}{f' ({LOG_FILE_NAME})' if LOG_TO_FILE else ''}"
)

# --- Logging Configuration (Setup ASAP after policy set) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)  # Initialize main logger

# Log the policy that was set (or attempted)
if sys.platform == "win32":
    if _event_loop_policy_set:
        logger.info(
            f"Policy set in main.py (top level): {asyncio.get_event_loop_policy().__class__.__name__}"
        )
    else:
        logger.error(
            f"Failed to set WindowsProactorEventLoopPolicy. Current policy: {asyncio.get_event_loop_policy().__class__.__name__}"
        )
else:
    logger.info(
        f"Running on non-Windows platform. Default policy: {asyncio.get_event_loop_policy().__class__.__name__}"
    )


# -*- coding: utf-8 -*-
"""
PMOVES Transcription API Backend

This FastAPI application provides endpoints for:
- Processing YouTube videos (downloading, transcribing).
- Downloading videos/audio using yt-dlp with progress updates.
- Fetching video metadata.
- Fetching web content using Jina Reader API, generating PDFs, storing in Supabase, and enabling vector search.
- Real-time status updates via Server-Sent Events (SSE).
- Content ingestion and vector search capabilities (requires related modules).
"""

# --- Standard Library Imports ---
import os
import re
import json
import shutil

# import logging # Moved up
# import asyncio # Moved up
import functools
import urllib.parse
from datetime import datetime, timedelta, timezone  # Added timezone
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import time
import sys
import uuid
import subprocess  # Added subprocess import
from typing import (
    Any,
)  # Added for Supabase client type hint if needed, or use from existing

# --- Third-Party Imports ---
from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    HTTPException,
    BackgroundTasks,
    Body,
    Request,
    status,
    Query,
    Depends,
    # Security, # This was in original main.py, but APIKeyHeader is used directly in middleware
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse  # Added FileResponse
from fastapi.security import APIKeyHeader  # Added for potential API key auth
from starlette.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, validator, ValidationError, Field, field_validator
import torch  # Still imported from original, ensure necessary

# --- Optional Third-Party Imports (with fallbacks/warnings) ---
try:
    from openai import OpenAI, AsyncOpenAI  # Added AsyncOpenAI
    from openai import APIError as OpenAI_APIError  # Specific OpenAI errors
    from openai import RateLimitError as OpenAI_RateLimitError
    from openai import APIConnectionError as OpenAI_APIConnectionError
    from openai import AuthenticationError as OpenAI_AuthenticationError
except ImportError:
    OpenAI = None
    AsyncOpenAI = None
    OpenAI_APIError = None
    OpenAI_RateLimitError = None
    OpenAI_APIConnectionError = None
    OpenAI_AuthenticationError = None

try:
    from groq import Groq, AsyncGroq  # Added AsyncGroq
except ImportError:
    Groq = None
    AsyncGroq = None

try:
    from rich.console import Console
except ImportError:

    class Console:
        def print(self, *args, **kwargs):
            print(*args)

    Console = Console()  # Instantiate dummy

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from tiktoken import get_encoding
except ImportError:
    get_encoding = None

import aiofiles  # Used for async file operations if needed

# --- Logging Configuration (Moved to top of file and initialized as 'logger') ---
# (Original content removed as it's now at the beginning)

# --- Check Critical Dependencies ---
if OpenAI is None or AsyncOpenAI is None:
    logger.warning(
        "Optional dependency 'openai' not found or incomplete. AI analysis/embedding features may be limited."
    )
if Groq is None or AsyncGroq is None:
    logger.warning(
        "Optional dependency 'groq' not found or incomplete. Groq features will be unavailable."
    )
if yt_dlp is None:
    logger.error(
        "Required dependency 'yt-dlp' not found. Video download and info features will fail."
    )
if get_encoding is None:
    logger.warning(
        "Optional dependency 'tiktoken' not found. Token counting will be estimated."
    )

# --- Rich Console Initialization ---
console = Console()

# --- Environment Variable Loading ---
APP_DIR = Path(__file__).parent.absolute()
ENV_PATH = APP_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    logger.info(f"Loaded environment variables from {ENV_PATH}")
else:
    logger.warning(
        f".env file not found at {ENV_PATH}. Relying on environment variables."
    )
    load_dotenv()  # Attempt default load

# --- API Client Initialization ---
# OpenAI (Async)
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = None
if AsyncOpenAI and openai_api_key:
    try:
        openai_client = AsyncOpenAI(api_key=openai_api_key)
        logger.info("Async OpenAI client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Async OpenAI client: {e}", exc_info=True)
elif AsyncOpenAI:
    logger.warning("OPENAI_API_KEY not set. OpenAI client not initialized.")

# Groq (Async)
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = None
if AsyncGroq and groq_api_key:
    try:
        groq_client = AsyncGroq(api_key=groq_api_key)
        logger.info("Async Groq client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Async Groq client: {e}", exc_info=True)
elif AsyncGroq:
    logger.warning("GROQ_API_KEY not set. Groq client not initialized.")


# --- Local/Project Imports ---
try:
    from .queue_manager import QueueManager
    from .monitoring.logger import PerformanceMonitor, async_timer, CustomLogger
    from .monitoring.metrics import (
        MetricsCollector,
        TranscriptionMetrics,
        router as metrics_router,
        get_metrics_collector,
    )
    from .error_handlers import TranscriptionErrorHandler, ErrorSeverity
    from .transcribe1 import (
        process_video,
        VideoProcessRequest as TranscribeVideoRequest,
    )  # Renamed Pydantic model
    from .general_utils import (
        save_text_to_markdown,
        clean_filename,
        format_timestamp,
        sanitize_filename,
        generate_pdf_from_markdown_string,  # Added for PDF generation
    )
    from .fetch_content import fetch_content_from_url, generate_unique_filename
    from .crawl4ai_docker_fetcher import fetch_with_crawl4ai_docker as fetch_with_crawl4ai # Use docker fetcher
    from .app_config import WORKSPACE_ROOT, SUBFOLDERS
    from .psearchworking import (
        search_all,
        analyze_search_results,
        get_client as get_supabase_client,
        SearchParameters,
        global_search_params,
        SearchResult,
        TokenCounter as PSearchTokenCounter,
        ModelSelector,
    )
    from .config.search_config import (
        get_preset,
        validate_search_params,
        router as search_config_router,  # etc.
    )
    from .routes.content_upserter import router as content_upserter_router
    from .routes.fetch_history_routes import (
        router as fetch_history_router,
    )  # Added this line
    from .routes.llm_routes import router as llm_router  # Added for new LLM endpoints
    from .routes import configurations_routes, agent_registry_routes # Added for new system config/agent routes
    from .monitoring.sse_monitor import sse_monitoring_middleware
    from .monitoring.routes import router as monitoring_router
    from .utils.llm_logging import log_llm_call  # Added for LLM call logging
    from .utils.llm_registry_service import (
        initialize_llm_registry,
        _periodic_refresh_task as schedule_llm_registry_refresh,
        # generate_embedding and get_model_details are removed from here
        get_llm_registry_service,  # Ensure this is imported if not already
    )
    from .ollama_initializer import (
        ensure_ollama_model_loaded,
    )  # Import the Ollama initializer
    # Add the new security middleware import
    from .middleware.security_middleware import APIKeySecurityMiddleware

    PROJECT_MODULES_LOADED = True
except ImportError as e:
    logger.error(
        f"Failed to import one or more project modules: {e}. Check installation and package structure.",
        exc_info=True,
    )
    PROJECT_MODULES_LOADED = False

    # --- Define dummy classes/functions with CORRECT SYNTAX ---
    logger.warning("Defining dummy components due to import errors.")

    class QueueManager:
        """Dummy QueueManager with correct syntax."""

        def __init__(self):
            self.status_queue = asyncio.Queue()
            self.transcription_queue = asyncio.Queue()
            logger.info("Initialized dummy QueueManager queues.")

        async def start(self):
            logger.warning("Called dummy QueueManager.start()")
            pass

        async def stop(self):
            logger.warning("Called dummy QueueManager.stop()")
            pass

        def has_active_transcriptions(self):
            return False  # Add dummy method

    class PerformanceMonitor:
        """Dummy PerformanceMonitor."""

        def __init__(self, logger_instance):
            pass

        def start_timer(self, name: str):
            pass

        def stop_timer(self, name: str) -> float:
            return 0.0

    class MetricsCollector:
        """Dummy MetricsCollector."""

        async def collect_system_metrics(self):
            pass

        def add_metric(self, *args, **kwargs):
            pass

    class TranscriptionMetrics:
        """Dummy TranscriptionMetrics."""

        def record_request(self, success: bool):
            pass

    # --- Dummy Functions ---
    def get_supabase_client():
        logger.error("Dummy: Supabase client unavailable.")
        return None

    DEFAULT_OUTPUT_FOLDER = "./output"

    async def process_video(*args, **kwargs):
        logger.error("Dummy: process_video unavailable.")

    async def search_all(*args, **kwargs):
        logger.error("Dummy: search_all unavailable.")
        return [], None, None

    def analyze_search_results(*args, **kwargs):
        logger.error("Dummy: analyze_search_results unavailable.")
        return "Analysis unavailable."

    async def fetch_content_from_url(*args, **kwargs):
        logger.error("Dummy: fetch_content_from_url unavailable.")
        return {"error": "unavailable"}

    async def convert_md_to_pdf_util(*args, **kwargs):
        logger.error("Dummy: convert_markdown_to_pdf unavailable.")
        return False

    def generate_unique_filename(url, ext):
        return f"dummy_{url[:10]}_{int(time.time())}.{ext}"

    # --- More Dummy Classes ---
    class SearchParameters:
        """Dummy SearchParameters."""

        def get_all_params(self) -> dict:
            return {}

        def get_params(self, tier: str) -> dict:
            return {}

        def load_current(self):
            pass

        def update_params(self, tier: str, **kwargs):
            pass

        def update_from_frontend(self, **kwargs):
            return True  # Add dummy method

    global_search_params = SearchParameters()

    class SearchResult:
        """Dummy SearchResult."""

        def __init__(self, **kwargs):
            pass

        def to_dict(self):
            return {}

    class PSearchTokenCounter:
        """Dummy TokenCounter."""

        def get_stats(self) -> dict:
            return {
                "embedding_tokens": 0,
                "generation_tokens": {"input": 0, "output": 0},
                "total_tokens": 0,
            }

        def count_embedding_tokens(self, text: str) -> int:
            return 0

        def count_generation_tokens(
            self, input_text: str, output_text: Optional[str] = None
        ) -> dict:
            return {"input": 0, "output": 0}

    class ModelSelector:
        """Dummy ModelSelector."""

        @staticmethod
        def generate_analysis(text: str, provider: str = "openai") -> str:
            return "Dummy Analysis Unavailable."

    # --- Dummy Routers/Middleware ---
    content_upserter_router = None
    metrics_router = None
    monitoring_router = None
    sse_monitoring_middleware = None

# --- Initialize Core Components ---
if PROJECT_MODULES_LOADED:
    performance_monitor = PerformanceMonitor(logger)
    metrics_collector = MetricsCollector()
    transcription_metrics = TranscriptionMetrics()
    try:
        queue_manager = QueueManager()
    except Exception as e:
        logger.error(f"Failed to initialize QueueManager: {e}", exc_info=True)
        sys.exit("QueueManager initialization failed.")
else:
    logger.warning("Using dummy components due to import errors.")
    performance_monitor = PerformanceMonitor(logger)
    metrics_collector = MetricsCollector()
    transcription_metrics = TranscriptionMetrics()
    queue_manager = QueueManager()  # Dummy instance

# Download-specific queue
download_status_queue = asyncio.Queue()


# --- TokenCounter Class ---
# (Keep existing TokenCounter class - lines 375-447)
class TokenCounter:
    """Tracks token usage for embeddings and generations."""

    def __init__(self):
        self.embedding_tokens = 0
        self.generation_tokens = {"input": 0, "output": 0}
        self.encoders = None
        if get_encoding:
            try:
                self.encoders = {
                    "cl100k_base": get_encoding("cl100k_base"),
                    "gpt-4": get_encoding("cl100k_base"),
                }
                logger.info("TokenCounter initialized with tiktoken encoders.")
            except Exception as e:
                logger.warning(
                    f"Could not initialize tiktoken encoders: {e}. Token counting will be estimated."
                )
        else:
            logger.warning(
                "TokenCounter initialized without tiktoken. Token counting will be estimated."
            )

    def _estimate_tokens(self, text: str) -> int:
        """Estimate tokens based on character count."""
        return len(text) // 4

    def count_embedding_tokens(self, text: str) -> int:
        """Count or estimate tokens for embedding."""
        if not self.encoders or "cl100k_base" not in self.encoders:
            tokens = self._estimate_tokens(text)
            self.embedding_tokens += tokens
            return tokens
        try:
            tokens = len(self.encoders["cl100k_base"].encode(text))
            self.embedding_tokens += tokens
            return tokens
        except Exception as e:
            logger.warning(
                f"Could not count embedding tokens using tiktoken: {e}. Estimating."
            )
            tokens = self._estimate_tokens(text)
            self.embedding_tokens += tokens
            return tokens

    def count_generation_tokens(
        self, input_text: str, output_text: Optional[str] = None
    ) -> dict:
        """Count or estimate tokens for generation."""
        result = {"input": 0, "output": 0}
        encoder = self.encoders.get("gpt-4") if self.encoders else None

        try:
            if encoder:
                result["input"] = len(encoder.encode(input_text))
                if output_text:
                    result["output"] = len(encoder.encode(output_text))
            else:
                result["input"] = self._estimate_tokens(input_text)
                if output_text:
                    result["output"] = self._estimate_tokens(output_text)
        except Exception as e:
            logger.warning(
                f"Could not count generation tokens using tiktoken: {e}. Estimating."
            )
            result["input"] = self._estimate_tokens(input_text)
            if output_text:
                result["output"] = self._estimate_tokens(output_text)

        self.generation_tokens["input"] += result["input"]
        self.generation_tokens["output"] += result["output"]
        return result

    def get_stats(self) -> dict:
        """Get current token usage statistics."""
        total = self.embedding_tokens + sum(self.generation_tokens.values())
        return {
            "embedding_tokens": self.embedding_tokens,
            "generation_tokens": self.generation_tokens,
            "total_tokens": total,
        }


# Initialize token counter
token_counter = TokenCounter()


# --- Supabase Client Function ---
# (Keep existing get_client function - lines 451-465)
def get_client():
    """Get a Supabase client instance using the imported function."""
    if not PROJECT_MODULES_LOADED or get_supabase_client is None:
        logger.error(
            "Cannot get Supabase client: psearchworking module or get_client function not loaded."
        )
        raise RuntimeError("Supabase client function is unavailable.")
    try:
        client = get_supabase_client()
        if client is None:
            logger.error("get_supabase_client() returned None.")
            raise RuntimeError("Failed to obtain Supabase client instance.")
        # logger.debug("Supabase client obtained successfully.")
        return client
    except Exception as e:
        logger.error(
            f"Error obtaining Supabase client via get_supabase_client(): {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Failed to obtain Supabase client: {e}")


# --- Pydantic Models ---
# (Keep existing models: ComprehensiveSearchRequest, ComprehensiveSearchResponse, VideoRequest, VectorSearchRequest, VectorSearchResponse, DownloadRequest, VideoInfoRequest - lines 469-586)
class ComprehensiveSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    max_results: int = Field(
        30, ge=10, le=100, description="Maximum TOTAL results desired across methods"
    )
    run_analysis: bool = Field(
        True, description="Whether to run AI analysis on results"
    )


class ComprehensiveSearchResponse(BaseModel):
    """Response model for the comprehensive search endpoint."""

    query: str
    results: List[
        Dict[str, Any]
    ]  # List of dictionaries matching SearchResult.to_dict()
    openai_analysis: Optional[str] = None
    groq_analysis: Optional[str] = None
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Search metadata, like timing, token counts, effective params",
    )

    class Config:
        from_attributes = True  # For Pydantic v2


class VideoRequest(BaseModel):
    youtube_video_url: str
    obsidian_dir: str  # Client must provide path to existing Obsidian vault/folder
    output_folder: str  # Client provides desired base output path
    transcription_model: str = "faster-whisper"
    use_groq: Optional[bool] = None  # Allow explicit setting, but validator overrides

    @field_validator("youtube_video_url")
    def validate_youtube_url(cls, v):
        youtube_regex = r"^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$"
        if not re.match(youtube_regex, v, re.IGNORECASE):
            raise ValueError("Invalid YouTube URL format")
        return v

    @field_validator("output_folder")
    def output_folder_must_be_valid(cls, v):
        if not v:
            v = os.path.join(WORKSPACE_ROOT, SUBFOLDERS["transcriptions"]["markdown"])
        try:
            path = Path(v).resolve()
            if not path.parent.exists():
                raise ValueError(f"Parent directory does not exist: {path.parent}")
            return str(path)
        except Exception as e:
            raise ValueError(f"Invalid output folder path '{v}': {e}")

    @field_validator("obsidian_dir")
    def obsidian_dir_must_exist(cls, v):
        if not v:
            raise ValueError("Obsidian directory path must be provided")
        try:
            path = Path(v).resolve()
            if not path.is_dir():
                raise ValueError("Path is not an existing directory")
            return str(path)
        except Exception as e:
            raise ValueError(f"Invalid Obsidian directory path '{v}': {e}")

    @field_validator("transcription_model")
    def validate_transcription_model(cls, v):
        valid_models = [
            "faster-whisper",
            "groq",
        ]  # Add specific models if needed e.g. "groq/whisper-large-v3"
        if v.lower() not in valid_models and not v.lower().startswith("groq/"):
            raise ValueError(
                f"Invalid transcription model. Use 'faster-whisper', 'groq', or specific 'groq/model-name'."
            )
        return v.lower()

    from pydantic import model_validator

    @model_validator(mode="after")
    def check_and_set_use_groq(self) -> "VideoRequest":
        model_name = self.transcription_model
        is_groq_model = model_name == "groq" or model_name.startswith("groq/")

        if self.use_groq is not None and self.use_groq != is_groq_model:
            logger.warning(
                f"Provided 'use_groq' ({self.use_groq}) contradicts model '{model_name}'. Overriding based on model."
            )

        self.use_groq = is_groq_model  # Set use_groq based on the model selected

        if self.use_groq and groq_client is None:
            raise ValueError(
                "Groq transcription model selected, but Groq client is not available/configured."
            )

        return self


class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    # Add fields for other search function parameters if needed
    content_weight: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    summary_weight: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    video_filter: Optional[str] = Field(None)

    @field_validator("query")
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Search query must not be empty")
        return v.strip()


class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(default_factory=list)
    ai_response: Optional[str] = Field(None)  # Keep for potential future use
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True  # Pydantic v2


class DownloadRequest(BaseModel):
    url: str
    options: Dict[str, Any] = Field(default_factory=dict, description="yt-dlp options")


class VideoInfoRequest(BaseModel):
    url: str


# --- Fetch History Models ---
class FetchHistoryBase(BaseModel):
    url: str = Field(
        ..., description="The URL that was fetched or attempted to be fetched."
    )
    fetching_engine: str = Field(
        ..., description="The engine used for fetching (e.g., 'jina', 'crawl4ai')."
    )
    status: str = Field(
        default="pending",
        description="The status of the fetch job (e.g., 'pending', 'success', 'failed').",
    )
    output_type: Optional[str] = Field(
        None,
        description="The type of output generated (e.g., 'markdown', 'pdf_link', 'json', 'unknown').",
    )  # ADDED
    engine_specific_parameters: Optional[Dict[str, Any]] = Field(
        None, description="Parameters specific to the fetching engine used."
    )
    user_id: Optional[uuid.UUID] = Field(
        None, description="Optional ID of the user who initiated the fetch."
    )
    error_message: Optional[str] = Field(
        None, description="Error message if the fetch job failed."
    )
    content_summary: Optional[str] = Field(
        None, description="A brief summary or preview of the fetched content."
    )
    raw_content_path: Optional[str] = Field(
        None, description="Path to the stored raw fetched content, if applicable."
    )
    processed_content_path: Optional[str] = Field(
        None,
        description="Path to the stored processed content (e.g., PDF), if applicable.",
    )
    supabase_content_id: Optional[uuid.UUID] = Field(
        None,
        description="ID of the related content in Supabase 'webpage_content' table, if applicable.",
    )


class FetchHistoryCreate(FetchHistoryBase):
    pass


class FetchHistoryResponse(FetchHistoryBase):
    id: uuid.UUID = Field(
        ..., description="Unique identifier for the fetch history record."
    )
    fetch_date: datetime = Field(
        ..., description="Timestamp of when the fetch job was recorded."
    )

    class Config:
        from_attributes = True


# --- Initialize FastAPI app ---
# (Keep existing app initialization - lines 589-602)
app = FastAPI(
    title="PMOVES Transcription API",
    description="API for YouTube video processing, download, and search.",
    version="1.2.0",  # Incremented version for fetch/pdf/search features
    openapi_tags=[
        {"name": "Processing", "description": "Video transcription and processing."},
        {"name": "Download", "description": "Video/Audio download operations."},
        {"name": "Search", "description": "Content search functionalities."},
        {"name": "Status", "description": "Real-time status updates via SSE."},
        {"name": "Utility", "description": "Helper endpoints."},
        {"name": "Health", "description": "Service health checks."},
        {"name": "Content Fetch", "description": "Fetch web content, generate PDFs."},
        {"name": "Files", "description": "Serve generated files (e.g., PDFs)."},
        {
            "name": "Fetch History",
            "description": "Manage and view fetch history records.",
        },  # Keep only one
        {
            "name": "LLM Endpoints",
            "description": "Endpoints for interacting with LLM capabilities.",
        },
    ],
)

# --- Configure CORS --- (Ensure this is early)
allowed_origins = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")
logger.info(f"Configuring CORS for origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Content-Type",
        "X-Content-Type-Options",
        "Content-Disposition",
    ],
)

# --- Add Custom Middlewares ---

# Add APIKeySecurityMiddleware FIRST
# This ensures that authentication/authorization happens before other processing like logging or monitoring for protected routes.
app.add_middleware(APIKeySecurityMiddleware)
logger.info("APIKeySecurityMiddleware enabled.")

# SSE Monitoring Middleware (if available)
if (
    PROJECT_MODULES_LOADED
    and "sse_monitoring_middleware" in locals()
    and sse_monitoring_middleware
):
    try:
        app.middleware("http")(sse_monitoring_middleware)
        logger.info("SSE monitoring middleware enabled.")
    except Exception as e:
        logger.warning(f"Failed to enable SSE monitoring middleware: {e}")

# Error Handling Middleware (should be early, but after Auth if Auth can raise HTTPExceptions handled by it)
# Given APIKeySecurityMiddleware returns Response directly, its placement relative to error handler is less critical for its own errors.
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_exc:
        raise http_exc  # Re-raise for FastAPI to handle
    except Exception as exc:
        logger.error(
            f"Unhandled exception during request to {request.url.path}", exc_info=exc
        )
        error_details = {
            "error_code": "UNEXPECTED_SERVER_ERROR",
            "message": "An internal server error occurred.",
        }
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if PROJECT_MODULES_LOADED and "TranscriptionErrorHandler" in locals():
            try:
                error_details = TranscriptionErrorHandler.handle_error(
                    "UNEXPECTED_SERVER_ERROR", exc, path=str(request.url.path)
                )
            except Exception as handler_err:
                logger.error(f"Error handler itself failed: {handler_err}")
        return JSONResponse(status_code=status_code, content=error_details)

# Request Logging Middleware (can be after Auth and Error Handling)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"--> {method} {path} from {client_host}")
    response = await call_next(request)  # Process request
    process_time = time.time() - start_time
    status_code = response.status_code
    logger.info(f"<-- {method} {path} - Status={status_code} ({process_time:.3f}s)")
    return response

# --- Setup Monitoring (from monitoring/backend_integration.py) ---
# This should be after other essential middleware like CORS and Auth, 
# but before routes are defined if it adds any itself (like /metrics, /health).
# The setup_backend_monitoring function from the guide adds its own middleware.
if PROJECT_MODULES_LOADED: # Assuming monitoring setup depends on project modules
    try:
        from monitoring.backend_integration import setup_backend_monitoring
        # The setup_backend_monitoring will add the PMOVESBackendMonitoring middleware
        monitor = setup_backend_monitoring(app, "pmoves-backend") 
        logger.info("Backend monitoring setup successfully.")
    except ImportError as e_mon_import:
        logger.error(f"Failed to import or setup monitoring: {e_mon_import}", exc_info=True)
    except Exception as e_mon_setup:
        logger.error(f"Error during monitoring setup: {e_mon_setup}", exc_info=True)
else:
    logger.warning("Project modules not loaded, skipping backend monitoring setup.")

# --- Include Routers ---
# Include routers for different parts of the API
app.include_router(llm_router, prefix="/llm", tags=["LLM"])  # LLM related endpoints
app.include_router(
    fetch_history_router, prefix="/api/fetch-history", tags=["Fetch History"]
)  # Fetch History endpoints
app.include_router(
    content_upserter_router, prefix="/api/content-upserter", tags=["Content Upserter"]
)  # Content Upserter endpoints
app.include_router(
    metrics_router, prefix="/api/metrics", tags=["Metrics"]
)  # Monitoring metrics endpoints
app.include_router(
    monitoring_router, prefix="/api/monitoring", tags=["Monitoring"]
)  # General monitoring endpoints


# --- App Lifecycle Events ---
# (Keep existing startup/shutdown events - lines 672-697)
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup initiated...")
    try:
        await queue_manager.start()
        if PROJECT_MODULES_LOADED:
            collector = get_metrics_collector()
            # import asyncio # Already imported at the top
            asyncio.create_task(collector.collect_system_metrics())
            logger.info("System metrics collection scheduled.")
        logger.info("Queue manager started.")

        # --- Initialize Ollama Model ---
        # Ensure Ollama model is loaded before initializing the LLM registry
        if PROJECT_MODULES_LOADED and "ensure_ollama_model_loaded" in globals():
            try:
                logger.info("Ensuring Ollama model is loaded...")
                await ensure_ollama_model_loaded()
                logger.info("Ollama model initialization process initiated.")
            except Exception as e_ollama_init:
                logger.error(
                    f"Error during Ollama model initialization: {e_ollama_init}",
                    exc_info=True,
                )
        else:
            logger.warning(
                "Ollama initializer function (ensure_ollama_model_loaded) not found in globals or PROJECT_MODULES_LOADED is false. Ollama model loading on startup will be skipped."
            )
        # --- End Ollama Initialization ---

        # --- Initialize LLM Registry ---
        # Check if the functions are in the global scope of this module
        if (
            PROJECT_MODULES_LOADED
            and "initialize_llm_registry" in globals()
            and "schedule_llm_registry_refresh" in globals()
        ):
            try:
                logger.info("Initializing LLM model registry...")
                # Directly call the imported functions
                await initialize_llm_registry()  # Initial fetch
                # asyncio.create_task(
                #     schedule_llm_registry_refresh()
                # )  # Schedule periodic refresh - COMMENTED OUT
                logger.info(
                    "LLM model registry initialized (periodic refresh disabled)." # UPDATED LOG
                )
            except Exception as e_llm_reg:
                logger.error(
                    f"Error initializing LLM model registry: {e_llm_reg}", exc_info=True
                )
        else:
            logger.warning(
                "LLM registry functions (initialize_llm_registry or schedule_llm_registry_refresh) not found in globals or PROJECT_MODULES_LOADED is false. LLM model management will be disabled."
            )

        if yt_dlp is None:
            logger.error("yt-dlp is missing, download features will be unavailable.")

    except (
        Exception
    ) as e:  # This except matches the main try block at the start of startup_event
        logger.error(f"Error during application startup: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown initiated...")
    try:
        await queue_manager.stop()
        logger.info("Queue manager stopped.")
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}", exc_info=True)


# --- SSE Message Formatter ---
# (Keep existing format_sse_message function - lines 700-747)
def format_sse_message(
    message_type: str, content: Any, metadata: Optional[dict] = None
) -> str:
    """Formats a message dictionary into an SSE string, ensuring content is serializable."""
    message = {
        "type": message_type,
        "content": None,  # Initialize content to None
        "timestamp": datetime.now().isoformat(),
        "id": str(time.time()),  # Add a unique ID for each message
    }
    if metadata:
        message["metadata"] = metadata

    serializable_content = None
    if isinstance(content, (str, int, float, bool, type(None))):
        serializable_content = content
    elif isinstance(content, (dict, list)):
        serializable_content = content
    elif hasattr(content, "to_dict") and callable(content.to_dict):
        try:
            serializable_content = content.to_dict()
        except Exception as e:
            logger.warning(
                f"Error calling to_dict() for SSE content type {message_type}: {e}. Content: {str(content)[:100]}"
            )
            serializable_content = f"Error serializing object: {str(content)[:100]}"
    elif hasattr(content, "__dict__"):
        try:
            json.dumps(content.__dict__)
            serializable_content = content.__dict__
        except TypeError:
            logger.warning(
                f"Could not directly serialize __dict__ for SSE content type {message_type}. Sending string representation. Content: {str(content)[:100]}"
            )
            serializable_content = str(content)  # Fallback to string representation
    else:
        serializable_content = str(content)

    message["content"] = serializable_content

    try:
        json_str = json.dumps(message)
        return (
            json_str  # EventSourceResponse will handle the "data: " prefix and "\n\n"
        )
    except TypeError as e:
        logger.error(
            f"FINAL fallback: Failed to serialize SSE message of type {message_type}: {e}. Content: {str(serializable_content)[:100]}"
        )
        error_content = {
            "error": "Failed to serialize message content",
            "original_type": message_type,
        }
        # EventSourceResponse will handle the "data: " prefix and "\n\n"
        return json.dumps(
            {
                "type": "error",
                "content": error_content,
                "timestamp": datetime.now().isoformat(),
            }
        )


# --- Combined SSE Updates Endpoint ---
# (Keep existing /combined-updates endpoint - lines 752-983)
@app.get("/combined-updates", tags=["Status"])
async def get_combined_updates(request: Request):
    """SSE endpoint for combined status and transcription updates."""
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "N/A")
    logger.info(
        f"SSE connection requested from {client_host} (Origin: {origin}) for /combined-updates."
    )

    async def event_generator():
        logger.info(f"SSE (Combined): GENERATOR ENTERED for {client_host}.")
        try:
            status_q = queue_manager.status_queue
            transcription_q = queue_manager.transcription_queue
            logger.info(
                f"SSE (Combined): Got queue references. TQ ID: {id(transcription_q)}, SQ ID: {id(status_q)}"
            )
            last_activity_time = time.time()
            heartbeat_interval = 2
            connection_timeout = 300

            transcription_task = asyncio.create_task(transcription_q.get())
            setattr(transcription_task, "_queue_name", "transcription")
            status_task = asyncio.create_task(status_q.get())
            setattr(status_task, "_queue_name", "status")
            heartbeat_task = asyncio.create_task(asyncio.sleep(heartbeat_interval))
            setattr(heartbeat_task, "_is_heartbeat", True)

            all_tasks = {transcription_task, status_task, heartbeat_task}
            logger.info(
                f"SSE (Combined): Initialized {len(all_tasks)} persistent tasks. Entering main try block."
            )
        except Exception as setup_err:
            logger.error(
                f"SSE (Combined): ERROR DURING INITIAL SETUP: {setup_err}",
                exc_info=True,
            )
            try:
                yield format_sse_message(
                    "error", f"SSE generator setup failed: {setup_err}"
                )
            except:
                pass
            return

        try:
            connection_established_msg = format_sse_message(
                "status",
                "SSE connection established",
                {
                    "connection_id": str(time.time()),
                    "server_time": datetime.now().isoformat(),
                },
            )
            yield connection_established_msg
            last_activity_time = time.time()
            yield format_sse_message("heartbeat", "initial_ping")
            await asyncio.sleep(1)
            yield format_sse_message("heartbeat", "connection_check")
            await asyncio.sleep(1)
            yield format_sse_message("heartbeat", "connection_check_2")

            while True:
                logger.debug(
                    f"SSE (Combined): Entering new loop iteration for {client_host}"
                )
                try:
                    logger.info(
                        f"SSE (Combined): LOOP START - Waiting on {len(all_tasks)} persistent tasks."
                    )
                    done, pending = await asyncio.wait(
                        all_tasks, return_when=asyncio.FIRST_COMPLETED
                    )
                    logger.info(
                        f"SSE (Combined): WAIT COMPLETED - Done: {len(done)}, Pending: {len(pending)}"
                    )

                    for task in done:
                        if getattr(task, "_is_heartbeat", False):
                            logger.debug("SSE (Combined): Heartbeat task completed.")
                            try:
                                yield format_sse_message("heartbeat", "ping_interval")
                                last_activity_time = time.time()
                                logger.debug("SSE (Combined): Sent interval heartbeat.")
                            except Exception as send_err:
                                logger.error(
                                    f"Failed to send interval heartbeat: {send_err}. Closing connection."
                                )
                                raise send_err
                            all_tasks.remove(task)
                            new_heartbeat_task = asyncio.create_task(
                                asyncio.sleep(heartbeat_interval)
                            )
                            setattr(new_heartbeat_task, "_is_heartbeat", True)
                            all_tasks.add(new_heartbeat_task)
                            logger.debug(
                                f"SSE (Combined): Replaced completed heartbeat task with new task {id(new_heartbeat_task)}"
                            )
                            continue

                        original_queue = None
                        queue_name = getattr(task, "_queue_name", None)
                        if queue_name == "transcription":
                            original_queue = transcription_q
                        elif queue_name == "status":
                            original_queue = status_q

                        if original_queue is None:
                            logger.error(
                                f"SSE (Combined): Completed task {id(task)} is not a known queue task."
                            )
                            continue

                        try:
                            item = task.result()
                            logger.info(
                                f"SSE (Combined): ITEM RETRIEVED from {queue_name} queue {id(original_queue)}. Type: {type(item).__name__}. Content: {str(item)[:100]}..."
                            )
                            sse_msg = None
                            if isinstance(item, str):
                                try:
                                    payload_dict = json.loads(item)
                                    msg_type = payload_dict.get(
                                        "type",
                                        "transcription_segment"
                                        if original_queue == transcription_q
                                        else "status",
                                    )
                                    msg_content = payload_dict.get(
                                        "content", payload_dict
                                    )
                                    sse_msg = format_sse_message(msg_type, msg_content)
                                except json.JSONDecodeError:
                                    logger.error(
                                        f"SSE (Combined): Failed to decode JSON from {queue_name} queue {id(original_queue)}: {item[:100]}..."
                                    )
                                    sse_msg = format_sse_message(
                                        "error",
                                        f"Invalid data received from backend queue: {item[:100]}...",
                                    )
                                except Exception as format_err:
                                    logger.error(
                                        f"SSE (Combined): Error formatting message after JSON decode: {format_err}",
                                        exc_info=True,
                                    )
                                    sse_msg = format_sse_message(
                                        "error",
                                        f"Internal error formatting SSE message: {format_err}",
                                    )
                            else:
                                logger.error(
                                    f"SSE (Combined): Received non-string item type '{type(item).__name__}' from {queue_name} queue {id(original_queue)}. Content: {str(item)[:100]}"
                                )
                                sse_msg = format_sse_message(
                                    "error",
                                    f"Invalid data type received from backend queue: {type(item).__name__}",
                                )

                            if sse_msg:
                                try:
                                    yield sse_msg
                                    last_activity_time = time.time()
                                    logger.info(
                                        f"SSE SEND (Combined): {sse_msg.strip()[:150]}..."
                                    )
                                except Exception as send_err:
                                    logger.error(
                                        f"Failed to send update to SSE client: {send_err}"
                                    )
                                    raise send_err
                            else:
                                logger.warning(
                                    f"SSE (Combined): No valid SSE message generated for item from {original_queue} queue."
                                )

                            original_queue.task_done()
                            all_tasks.remove(task)
                            if original_queue == transcription_q:
                                new_task = asyncio.create_task(transcription_q.get())
                                setattr(new_task, "_queue_name", "transcription")
                                all_tasks.add(new_task)
                                logger.debug(
                                    f"SSE (Combined): Replaced completed transcription task with new task {id(new_task)}"
                                )
                            elif original_queue == status_q:
                                new_task = asyncio.create_task(status_q.get())
                                setattr(new_task, "_queue_name", "status")
                                all_tasks.add(new_task)
                                logger.debug(
                                    f"SSE (Combined): Replaced completed status task with new task {id(new_task)}"
                                )

                        except asyncio.CancelledError:
                            logger.info(
                                f"SSE (Combined): A queue get() task {id(task)} was cancelled."
                            )
                        except Exception as e:
                            logger.error(
                                f"SSE (Combined): Error processing completed task result for task {id(task)}: {e}",
                                exc_info=True,
                            )
                            try:
                                yield format_sse_message(
                                    "error",
                                    f"Internal SSE error processing task result: {str(e)}",
                                )
                            except Exception as send_err:
                                logger.error(
                                    f"Failed to send task processing error to SSE client: {send_err}"
                                )
                                raise send_err

                except asyncio.CancelledError:
                    logger.info(
                        f"SSE connection closed by client {client_host} for /combined-updates (Caught CancelledError in loop)."
                    )
                    break
                except Exception as loop_err:
                    error_message = f"FATAL Error in /combined-updates SSE generator loop: {loop_err}"
                    logger.error(error_message, exc_info=True)
                    try:
                        yield format_sse_message(
                            "error", f"Fatal SSE generator loop error: {str(loop_err)}"
                        )
                    except Exception:
                        pass
                    break

            logger.info(
                f"SSE event generator loop exited for {client_host} (/combined-updates)."
            )

        finally:
            logger.info(
                f"SSE event generator entering finally block for {client_host} (/combined-updates)."
            )
            logger.info(
                f"SSE (Combined): Cancelling {len(all_tasks)} remaining tasks in final cleanup."
            )
            for task in list(all_tasks):
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error awaiting cancellation of task {id(task)}: {e}")
            logger.info(
                f"SSE event generator finished final cleanup for {client_host} (/combined-updates)."
            )

    response = EventSourceResponse(event_generator(), media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = origin if origin != "N/A" else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Transfer-Encoding"] = "chunked"
    logger.info(f"SSE response headers: {response.headers}")
    return response


# --- OPTIONS handler for Combined SSE ---
# (Keep existing /combined-updates OPTIONS handler - lines 1006-1010)
@app.options("/combined-updates", tags=["Status"])
async def options_combined_updates(request: Request):
    """Handle OPTIONS preflight requests for /combined-updates."""
    return _handle_options_request(request, allowed_origins)


# --- Download Status SSE Endpoint ---
# (Keep existing /api/download-status endpoint - lines 1013-1084)
@app.get("/api/download-status", tags=["Status", "Download"])
async def get_download_status(request: Request):
    """SSE endpoint specifically for download status updates."""
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "N/A")
    logger.info(
        f"Download status SSE connection requested from {client_host} (Origin: {origin})."
    )

    async def event_generator():
        q = download_status_queue
        last_activity_time = time.time()
        heartbeat_interval = 20

        try:
            yield format_sse_message("status", "Connected to download status stream")
            last_activity_time = time.time()

            while True:
                try:
                    status_update_str = await asyncio.wait_for(
                        q.get(), timeout=heartbeat_interval
                    )
                    logger.debug(
                        f"SSE (Download): Sending update: {status_update_str[:100]}..."
                    )
                    try:
                        update_data = json.loads(status_update_str)
                        yield f"data: {status_update_str}\n\n"  # Send raw JSON string
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(
                            f"Download SSE received non-JSON: {status_update_str[:100]}... Error: {e}"
                        )
                        yield format_sse_message(
                            "status", status_update_str
                        )  # Send as plain
                    q.task_done()
                    last_activity_time = time.time()

                except asyncio.TimeoutError:
                    logger.debug("SSE (Download): Sending heartbeat.")
                    yield format_sse_message("heartbeat", "ping")
                    last_activity_time = time.time()
                    continue

                except asyncio.QueueEmpty:
                    await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info(f"Download SSE connection closed by client {client_host}.")
        except Exception as e:
            error_message = f"Error in download status SSE generator: {e}"
            logger.error(error_message, exc_info=True)
            try:
                yield format_sse_message("error", error_message)
            except Exception as send_err:
                logger.error(f"Failed to send error to download SSE client: {send_err}")
        finally:
            logger.info(f"Download SSE event generator finished for {client_host}.")

    response = EventSourceResponse(event_generator(), media_type="text/event-stream")
    origin = request.headers.get("origin", "N/A")
    response.headers["Access-Control-Allow-Origin"] = origin if origin != "N/A" else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Transfer-Encoding"] = "chunked"
    logger.info(f"Download SSE response headers: {response.headers}")
    return response


# --- OPTIONS handler for Download Status SSE ---
# (Keep existing /api/download-status OPTIONS handler - lines 1087-1090)
@app.options("/api/download-status", tags=["Status", "Download"])
async def options_download_status(request: Request):
    """Handle OPTIONS preflight requests for /api/download-status."""
    return _handle_options_request(request, allowed_origins)


# --- Helper for OPTIONS requests ---
# (Keep existing _handle_options_request function - lines 1093-1109)
def _handle_options_request(request: Request, allowed_origins_list: List[str]):
    origin = request.headers.get("origin")
    method = request.headers.get("access-control-request-method")
    logger.info(
        f"OPTIONS request for {request.url.path} from origin: {origin}, method: {method}"
    )

    if origin in allowed_origins_list:
        response = JSONResponse(content={"detail": "OK"}, status_code=200)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, OPTIONS"  # Adjust as needed per endpoint
        )
        response.headers["Access-Control-Allow-Headers"] = (
            "*"  # Or be specific: "Content-Type, Authorization, X-Requested-With"
        )
        response.headers["Access-Control-Max-Age"] = (
            "86400"  # Cache preflight for 1 day
        )
        logger.debug(f"OPTIONS response headers: {response.headers}")
        return response
    else:
        logger.warning(f"OPTIONS request from disallowed origin: {origin}")
        return JSONResponse(content={"detail": "Origin not allowed"}, status_code=400)


# --- Transcription Status Endpoint ---
# (Keep existing /transcription-status endpoint - lines 1113-1131)
@app.get("/transcription-status", tags=["Status"])
async def transcription_status():
    """Check if there's an active transcription process running."""
    try:
        active = False
        if (
            queue_manager
            and hasattr(queue_manager, "_running")
            and queue_manager._running
        ):
            active = not queue_manager.transcription_queue.empty()
            if hasattr(queue_manager, "has_active_transcriptions"):
                active = active or queue_manager.has_active_transcriptions()
        return {"active": active}
    except Exception as e:
        logger.error(f"Error checking transcription status: {e}")
        return {"active": False, "error": str(e)}


# --- Process Video Endpoint ---
# (Keep existing /process-video/ endpoint - lines 1134-1212)
@app.post("/process-video/", tags=["Processing"])
async def process_video_endpoint(
    request: VideoRequest, background_tasks: BackgroundTasks
):
    """Initiate background processing (download, transcribe) for a YouTube video."""
    if not PROJECT_MODULES_LOADED or process_video is None:
        raise HTTPException(
            status_code=501,
            detail="Video processing feature is unavailable due to missing modules.",
        )

    try:
        logger.info(f"Processing video request for URL: {request.youtube_video_url}")
        console.print(f"[cyan]Obsidian Dir:[/cyan] {request.obsidian_dir}")
        console.print(f"[cyan]Output Folder:[/cyan] {request.output_folder}")
        console.print(
            f"[cyan]Model:[/cyan] {request.transcription_model}, [cyan]Use Groq:[/cyan] {request.use_groq}"
        )

        transcription_metrics.record_request(True)
        output_path = Path(request.output_folder)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured output folder exists: {output_path}")
        except OSError as e:
            logger.error(
                f"Failed to create output folder {output_path}: {e}", exc_info=True
            )
            raise HTTPException(
                status_code=500, detail=f"Could not create output directory: {e}"
            )

        model_config = {
            "model": request.transcription_model,
            "use_groq": request.use_groq,
        }

        try:
            from .transcribe1 import extract_video_id

            video_id = extract_video_id(request.youtube_video_url)
        except Exception as e:
            logger.warning(f"Could not extract video ID for tracking: {e}")
            video_id = request.youtube_video_url

        from .process_video_wrapper import process_video_with_tracking

        background_tasks.add_task(
            process_video_with_tracking,
            youtube_video_url=request.youtube_video_url,
            obsidian_dir=request.obsidian_dir,
            status_queue=queue_manager.status_queue,
            transcription_queue=queue_manager.transcription_queue,
            output_folder=request.output_folder,
            model_config=model_config,
            video_id=video_id,
        )

        logger.info(
            f"Background task added for processing: {request.youtube_video_url}"
        )

        return {
            "status": "started",
            "message": "Video processing initiated in the background.",
            "details": {
                "url": request.youtube_video_url,
                "output_folder": request.output_folder,
                "obsidian_dir": request.obsidian_dir,
            },
            "timestamp": datetime.now().isoformat(),
        }

    except ValidationError as e:
        transcription_metrics.record_request(False)
        logger.warning(
            f"Validation error processing video request: {e.errors()}", exc_info=False
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()
        )
    except HTTPException as e:
        transcription_metrics.record_request(False)
        raise e
    except Exception as e:
        transcription_metrics.record_request(False)
        logger.error(
            f"Unexpected error initiating video processing for {request.youtube_video_url}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start video processing task.",
        )


# --- Video Download Feature ---
# (Keep existing download_video_task, report_download_progress, report_postprocess_progress, /api/download endpoint - lines 1217-1459)
async def download_video_task(url: str, options: dict, status_queue: asyncio.Queue):
    """Background task using yt-dlp (run in thread) with progress reporting."""
    if yt_dlp is None:
        logger.error("yt-dlp library is not installed. Cannot download video.")
        await status_queue.put(
            format_sse_message(
                "error", "Download feature unavailable: yt-dlp library not installed."
            )
        )
        return

    download_dir = options.get("download_dir", os.path.join(os.getcwd(), "downloads"))
    logger.info(f"Download task started for URL: {url}, saving to: {download_dir}")

    try:
        os.makedirs(download_dir, exist_ok=True)
    except OSError as e:
        logger.error(
            f"Failed to create download directory {download_dir}: {e}", exc_info=True
        )
        await status_queue.put(
            format_sse_message("error", f"Failed to create download directory: {e}")
        )
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_template = os.path.join(download_dir, f"%(title)s_{timestamp}.%(ext)s")

    ydl_opts = {
        "outtmpl": filename_template,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "keepvideo": options.get("keepVideo", True),
        "overwrites": False,
        "ffmpeg_location": options.get("ffmpegPath"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "noplaylist": True,
        "playlist_items": None,
    }

    video_format = options.get("format")
    if video_format == "best":
        pass
    elif video_format in ["1080p", "720p", "480p", "360p"]:
        res = video_format.replace("p", "")
        ydl_opts["format"] = (
            f"bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best[height<={res}]"
        )
    elif video_format == "audio_best":
        ydl_opts["format"] = "bestaudio/best"
        options["extractAudio"] = True
        options.setdefault("audioFormat", "mp3")

    if options.get("extractAudio"):
        audio_format = options.get("audioFormat", "mp3")
        audio_quality = options.get("audioQuality", "192")
        ydl_opts.setdefault("postprocessors", []).append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": audio_quality,
            }
        )
        if not ydl_opts["keepvideo"] and video_format != "audio_best":
            ydl_opts["format"] = "bestaudio/best"

    if options.get("embedThumbnail") and video_format != "audio_best":
        ydl_opts["writethumbnail"] = True
        ydl_opts.setdefault("postprocessors", []).append({"key": "EmbedThumbnail"})

    if options.get("embedMetadata", True):
        ydl_opts.setdefault("postprocessors", []).append(
            {"key": "FFmpegMetadata", "add_metadata": True}
        )

    if options.get("subtitles"):
        sub_lang = options.get("subtitleLanguage", "en")
        sub_auto = options.get("autoSubtitles", False)
        sub_format = options.get("subtitleFormat", "srt")
        ydl_opts.update(
            {
                "writesubtitles": True,
                "writeautomaticsub": sub_auto,
                "subtitleslangs": [sub_lang] if sub_lang != "all" else ["all"],
                "subtitlesformat": sub_format,
            }
        )
        if options.get("embedSubtitles") and video_format != "audio_best":
            ydl_opts.setdefault("postprocessors", []).append(
                {"key": "FFmpegEmbedSubtitle"}
            )

    is_playlist_url = "list=" in url or "/playlist?" in url
    if is_playlist_url and options.get("downloadPlaylist"):
        playlist_items = None
        items_str = options.get("playlistItems")
        start = options.get("playlistStart")
        end = options.get("playlistEnd")
        if items_str:
            playlist_items = items_str
        elif start or end:
            playlist_items = f"{start or ''}-{end or ''}"
        ydl_opts["noplaylist"] = False
        ydl_opts["playlist_items"] = playlist_items
        logger.info(f"Playlist download enabled. Items: '{playlist_items or 'all'}'")
    elif is_playlist_url:
        logger.info("Playlist URL detected, but only downloading single video.")
        ydl_opts["noplaylist"] = True

    try:
        await status_queue.put(
            format_sse_message(
                "status", f"Starting download: {url}", {"download_dir": download_dir}
            )
        )
        logger.info("Running yt-dlp download process in thread...")
        loop = asyncio.get_running_loop()
        ydl_opts["progress_hooks"] = [
            functools.partial(report_download_progress, loop, status_queue)
        ]
        ydl_opts["postprocessor_hooks"] = [
            functools.partial(report_postprocess_progress, loop, status_queue)
        ]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        logger.info(f"yt-dlp download thread finished for {url}.")
        await status_queue.put(
            format_sse_message("complete", f"Download finished for: {url}")
        )
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp download error for {url}: {e}", exc_info=False)
        await status_queue.put(format_sse_message("error", f"Download failed: {e}"))
    except Exception as e:
        logger.error(
            f"Unexpected error during download task for {url}: {e}", exc_info=True
        )
        await status_queue.put(
            format_sse_message("error", f"Unexpected download error: {e}")
        )


def report_download_progress(
    loop: asyncio.AbstractEventLoop, status_queue: asyncio.Queue, d: dict
):
    """Hook for yt-dlp download progress, puts message to asyncio queue."""
    if loop is None:
        logger.error("Asyncio loop is None in report_download_progress.")
        return
    if d["status"] == "downloading":
        try:
            progress = d.get("fraction", 0) * 100
            speed = d.get("speed_str", d.get("speed", "N/A"))
            eta = d.get("eta_str", d.get("eta", "N/A"))
            filename = d.get("filename", d.get("info_dict", {}).get("filename", "..."))
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
            size_str = "N/A"
            if total_bytes:
                if total_bytes < 1024 * 1024:
                    size_str = f"{total_bytes / 1024:.1f} KiB"
                elif total_bytes < 1024 * 1024 * 1024:
                    size_str = f"{total_bytes / (1024 * 1024):.1f} MiB"
                else:
                    size_str = f"{total_bytes / (1024 * 1024 * 1024):.2f} GiB"
            content = {
                "progress": round(progress, 1),
                "speed": speed,
                "eta": eta,
                "filename": os.path.basename(filename),
                "total_size": size_str,
                "status": "Downloading",
            }
            message = format_sse_message("progress", content)
            asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)
        except Exception as e:
            pass
    elif d["status"] == "finished":
        filename = d.get("filename", d.get("info_dict", {}).get("filename", "file"))
        message = format_sse_message(
            "status", f"Downloaded {os.path.basename(filename)}. Post-processing..."
        )
        asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)
    elif d["status"] == "error":
        err_msg = d.get("error", "Unknown download error")
        filename = d.get("filename", d.get("info_dict", {}).get("filename", "N/A"))
        message = format_sse_message(
            "error", f"Error downloading {os.path.basename(filename)}: {err_msg}"
        )
        asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)


def report_postprocess_progress(
    loop: asyncio.AbstractEventLoop, status_queue: asyncio.Queue, d: dict
):
    """Hook for yt-dlp post-processing progress."""
    if loop is None:
        logger.error("Asyncio loop is None in report_postprocess_progress.")
        return
    status = d.get("status")
    pp_name = d.get("postprocessor")
    info = d.get("info_dict", {})
    filename = os.path.basename(info.get("filepath", info.get("filename", "file")))
    if status == "started" or status == "processing":
        message = format_sse_message(
            "status", f"Post-processing ({pp_name}): Starting on {filename}..."
        )
    elif status == "finished":
        message = format_sse_message(
            "status", f"Post-processing ({pp_name}): Finished for {filename}."
        )
    elif status == "error":
        message = format_sse_message(
            "error", f"Post-processing ({pp_name}): Failed for {filename}. Check logs."
        )
    else:
        return
    asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)


@app.post("/api/download", tags=["Download"])
async def download_video_endpoint(
    request: DownloadRequest, background_tasks: BackgroundTasks
):
    """Start a video/audio download task in the background."""
    if yt_dlp is None:
        raise HTTPException(
            status_code=501,
            detail="Download feature unavailable: yt-dlp library not installed.",
        )
    try:
        logger.info(f"Download request received for URL: {request.url}")
        console.print(f"[yellow]Options:[/yellow] {request.options}")
        request.options.setdefault(
            "download_dir", os.path.join(os.getcwd(), "downloads")
        )
        background_tasks.add_task(
            download_video_task, request.url, request.options, download_status_queue
        )
        return {
            "status": "success",
            "message": "Download task initiated in background.",
            "url": request.url,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(
            f"Error starting download task for {request.url}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to start download task: {e}"
        )


# --- Get Video Info Endpoint ---
# (Keep existing /api/video-info endpoint - lines 1463-1551)
@app.post("/api/video-info", tags=["Download", "Utility"])
async def get_video_info(request: VideoInfoRequest):
    """Get metadata for a YouTube video or playlist without downloading."""
    if yt_dlp is None:
        raise HTTPException(
            status_code=501,
            detail="Info feature unavailable: yt-dlp library not installed.",
        )
    logger.info(f"Video info request for URL: {request.url}")
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
    }
    info = None
    try:
        logger.debug(f"Extracting info for {request.url} in thread...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(
                ydl.extract_info, request.url, download=False
            )
        logger.debug(f"Info extraction finished.")
        if not info:
            raise HTTPException(
                status_code=404,
                detail="Could not extract information for the given URL.",
            )

        is_playlist = info.get("_type") == "playlist"
        playlist_count = len(info.get("entries", [])) if is_playlist else 0
        title = info.get("title", "N/A")
        author = info.get("uploader", info.get("channel", "N/A"))
        thumbnail = info.get("thumbnail")
        video_id = info.get("id", "")
        original_url = info.get("webpage_url", request.url)
        duration_str = "N/A"
        if is_playlist:
            duration_str = f"{playlist_count} videos"
        else:
            duration_sec = info.get("duration")
            if duration_sec:
                try:
                    duration_str = str(timedelta(seconds=int(duration_sec)))
                except (
                    ValueError,
                    TypeError,
                ):  # Catch specific errors during conversion
                    logger.warning(
                        f"Could not convert duration '{duration_sec}' to timedelta."
                    )
                    pass  # Keep duration_str as "N/A"
            if not thumbnail and info.get("thumbnails"):
                thumbnail = info["thumbnails"][-1]["url"]

        formats = info.get("formats", [])
        available_formats_notes = (
            sorted(
                list(
                    set(
                        f.get("format_note", f.get("resolution", f.get("ext")))
                        for f in formats
                        if f.get("format_note") or f.get("resolution") or f.get("ext")
                    )
                )
            )
            if formats
            else ["N/A (requires detailed fetch)"]
        )
        subs = info.get("subtitles", {})
        auto_subs = info.get("automatic_captions", {})
        available_subtitles = sorted(list(subs.keys()))
        available_auto_captions = sorted(list(auto_subs.keys()))

        return {
            "title": title,
            "author": author,
            "thumbnail": thumbnail,
            "duration": duration_str,
            "is_playlist": is_playlist,
            "playlist_count": playlist_count if is_playlist else 1,
            "available_formats": available_formats_notes,
            "available_subtitles": available_subtitles,
            "available_auto_captions": available_auto_captions,
            "id": video_id,
            "original_url": original_url,
        }
    except yt_dlp.utils.DownloadError as e:
        logger.warning(f"yt-dlp info extraction failed for {request.url}: {e}")
        status_code = 400
        detail = f"Failed to process URL"
        if "Unsupported URL" in str(e):
            status_code = 400
            detail = "Unsupported URL"
        elif "Video unavailable" in str(e):
            status_code = 404
            detail = "Video unavailable"
        elif "Private video" in str(e):
            status_code = 403
            detail = "Video is private"
        elif "Sign in to confirm your age" in str(e):
            status_code = 403
            detail = "Video requires age verification (login)"
        raise HTTPException(status_code=status_code, detail=f"{detail}: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected error fetching video info for {request.url}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail=f"Unexpected error fetching video info: {e}"
        )


# --- List Downloads Endpoint ---
# (Keep existing /api/list-downloads endpoint - lines 1555-1634)
@app.get("/api/list-downloads", tags=["Download"])
async def list_downloads(directory: Optional[str] = Query(None)):
    """List files in the specified download directory."""
    logger.info(f"List downloads request for directory: {directory}")
    list_dir = directory
    if not list_dir:
        try:
            user_downloads = str(Path.home() / "Downloads")
            if Path(user_downloads).is_dir():
                list_dir = user_downloads
            else:
                list_dir = os.path.abspath(os.path.join(os.getcwd(), "downloads"))
        except Exception:
            list_dir = os.path.abspath("./downloads")

    list_dir_path = Path(list_dir).resolve()
    if not list_dir_path.is_dir():
        logger.warning(
            f"Attempted to list non-existent or non-directory path: {list_dir_path}"
        )
        return {"files": []}
    try:
        entries = await asyncio.to_thread(os.listdir, list_dir_path)
        files_list = []
        for entry_name in entries:
            entry_path = list_dir_path / entry_name
            if await asyncio.to_thread(os.path.isfile, entry_path):
                try:
                    stat = await asyncio.to_thread(os.stat, entry_path)
                    size_bytes = stat.st_size
                    mod_time = datetime.fromtimestamp(stat.st_mtime)
                    file_extension = entry_path.suffix.lower()
                    file_type = "Other"
                    if file_extension in [".mp4", ".mkv", ".webm", ".avi", ".mov"]:
                        file_type = "Video"
                    elif file_extension in [
                        ".mp3",
                        ".wav",
                        ".aac",
                        ".m4a",
                        ".opus",
                        ".ogg",
                    ]:
                        file_type = "Audio"
                    elif file_extension in [".srt", ".vtt", ".ass"]:
                        file_type = "Subtitle"
                    size_str = "N/A"
                    if size_bytes is not None:
                        if size_bytes < 1024:
                            size_str = f"{size_bytes} B"
                        elif size_bytes < 1024 * 1024:
                            size_str = f"{size_bytes / 1024:.1f} KB"
                        elif size_bytes < 1024 * 1024 * 1024:
                            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                        else:
                            size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
                    files_list.append(
                        {
                            "name": entry_name,
                            "type": file_type,
                            "size": size_str,
                            "modified": mod_time.isoformat(),
                            "path": str(entry_path),
                        }
                    )
                except Exception as file_info_err:
                    logger.warning(
                        f"Error getting info for file {entry_path}: {file_info_err}"
                    )
                    files_list.append(
                        {
                            "name": entry_name,
                            "type": "Unknown",
                            "size": "N/A",
                            "modified": "N/A",
                            "path": str(entry_path),
                        }
                    )
        files_list.sort(key=lambda x: x.get("modified", "0"), reverse=True)
        logger.info(f"Listed {len(files_list)} files in {list_dir_path}")
        return {"files": files_list}
    except Exception as e:
        logger.error(
            f"Error listing files in directory {list_dir_path}: {e}", exc_info=True
        )
        return {"files": [], "error": f"Failed to list files: {e}"}


# --- Fetch History API Endpoints ---


@app.post(
    "/api/fetch-history",
    response_model=FetchHistoryResponse,
    tags=["Fetch History"],
    status_code=status.HTTP_201_CREATED,
)
async def create_fetch_history_entry(payload: FetchHistoryCreate):
    """
    Create a new fetch history entry.
    """
    logger.info(
        f"Creating fetch history entry for URL: {payload.url} with engine: {payload.fetching_engine}"
    )
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database client unavailable.",
            )

        # Prepare data for insertion, Pydantic model ensures correct types for what's passed
        # fetch_date and id are handled by the database by default
        data_to_insert = payload.model_dump(
            exclude_unset=True
        )  # Use model_dump for Pydantic v2

        response = await asyncio.to_thread(
            supabase_client.table("fetch_history").insert(data_to_insert).execute
        )

        if hasattr(response, "data") and response.data:
            created_entry_data = response.data[0]
            logger.info(
                f"Successfully created fetch history entry with ID: {created_entry_data.get('id')}"
            )
            # Ensure all fields required by FetchHistoryResponse are present, or handle defaults
            # The DB defaults should cover 'id' and 'fetch_date'
            return FetchHistoryResponse(**created_entry_data)
        elif hasattr(response, "error") and response.error:
            logger.error(
                f"Supabase error creating fetch history entry: {response.error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {response.error.message}",
            )
        else:
            logger.error(
                f"Unexpected response from Supabase during fetch history creation: {response}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected database response.",
            )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(
            f"Error creating fetch history entry for URL {payload.url}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create fetch history entry: {str(e)}",
        )


@app.get(
    "/api/fetch-history",
    response_model=List[FetchHistoryResponse],
    tags=["Fetch History"],
)
async def list_fetch_history_entries(
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return."
    ),
    offset: int = Query(
        0, ge=0, description="Number of records to skip for pagination."
    ),
):
    """
    List existing fetch history entries, ordered by fetch_date descending.
    """
    logger.info(f"Listing fetch history entries with limit={limit}, offset={offset}")
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database client unavailable.",
            )

        response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .select("*")
            .order("fetch_date", desc=True)
            .limit(limit)
            .offset(offset)
            .execute
        )

        if hasattr(response, "data"):
            entries_data = response.data
            logger.info(
                f"Successfully retrieved {len(entries_data)} fetch history entries."
            )
            # Pydantic will validate each item in the list against FetchHistoryResponse
            return [FetchHistoryResponse(**entry) for entry in entries_data]
        elif hasattr(response, "error") and response.error:
            logger.error(
                f"Supabase error listing fetch history entries: {response.error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {response.error.message}",
            )
        else:
            logger.error(
                f"Unexpected response from Supabase during fetch history listing: {response}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected database response.",
            )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error listing fetch history entries: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list fetch history entries: {str(e)}",
        )


# --- Get Default Directory Endpoint ---
# (Keep existing /api/default-directory endpoint - lines 1640-1667)
@app.get("/api/default-directory", tags=["Utility"])
async def get_default_directory():
    """Suggest a default download directory path (client can override)."""
    path_str = ""
    warning = None
    try:
        try:
            user_downloads = str(Path.home() / "Downloads")
            if Path(user_downloads).is_dir():
                path_str = user_downloads
            else:
                path_str = os.path.abspath(os.path.join(os.getcwd(), "downloads"))
                warning = (
                    "User 'Downloads' directory not found, suggesting relative path."
                )
        except Exception:
            path_str = os.path.abspath(os.path.join(os.getcwd(), "downloads"))
            warning = (
                "Could not determine user home directory, suggesting relative path."
            )
        logger.info(f"Providing default download directory suggestion: {path_str}")
        response = {"path": path_str}
        if warning:
            response["warning"] = warning
        return response
    except Exception as e:
        logger.error(f"Error determining default directory: {e}", exc_info=True)
        fallback_dir = os.path.abspath("./downloads")
        return {
            "path": fallback_dir,
            "warning": "Could not determine default path, using relative './downloads'.",
        }


# --- PDF Storage Path ---
PDF_STORAGE_BASE_DIR = Path(os.getenv("PDF_STORAGE_PATH", "./temp_pdfs")).resolve()
try:
    PDF_STORAGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured PDF storage directory exists: {PDF_STORAGE_BASE_DIR}")
except OSError as e:
    logger.error(
        f"CRITICAL: Could not create PDF storage directory {PDF_STORAGE_BASE_DIR}: {e}. PDF features will fail.",
        exc_info=True,
    )
    # Depending on requirements, might want to exit or just disable PDF features
    # sys.exit(f"Failed to create PDF storage directory: {PDF_STORAGE_BASE_DIR}")


# --- Helper: Generate Embedding (Now uses LLM Registry) ---
async def get_embedding_with_registry(
    text: str,
    model_id: str = os.getenv(
        "DEFAULT_EMBEDDING_MODEL_ID", "openai/text-embedding-ada-002"
    ),
) -> Optional[List[float]]:
    """Generates embedding for text using the LLM registry service."""
    # Get the LLM registry service instance
    try:
        registry_service = get_llm_registry_service()
    except RuntimeError as e:
        logger.error(
            f"LLM Registry service not initialized: {e}. Cannot generate embedding."
        )
        # Log attempt (similar to old get_openai_embedding logging but for registry failure)
        # This part can be enhanced with more structured logging via llm_logging utility if needed
        return None

    if not text or not text.strip():
        logger.warning("Attempted to generate embedding for empty text.")
        return None

    logger.info(
        f"Requesting embedding for text (snippet: '{text[:50]}...') using model_id: {model_id} via LLM Registry."
    )

    # The llm_registry_service.generate_embedding function is expected to handle its own
    # detailed logging to the llm_call_logs table via LiteLLM's callback system or internally.
    # So, we don't need to replicate the detailed llm_log_data construction here.

    try:
        embedding = await registry_service.generate_embedding(
            model_id=model_id, text=text
        )  # Call method on instance
        if embedding:
            logger.info(
                f"Successfully generated embedding using model {model_id} via LLM Registry."
            )
            # Token counting for embeddings might be handled by LiteLLM callbacks or needs adjustment here
            # For now, assuming TokenCounter is for OpenAI direct calls or needs to be adapted.
            # token_counter.count_embedding_tokens(text) # This might need re-evaluation
        else:
            logger.error(
                f"Failed to generate embedding using model {model_id} via LLM Registry (returned None)."
            )
        return embedding
    except Exception as e:
        logger.error(
            f"Unexpected error calling generate_embedding_from_registry for model {model_id}: {e}",
            exc_info=True,
        )
        return None


# --- Helper: Upsert Content to Supabase ---
async def upsert_content_to_supabase(
    url: str,
    title: str,
    markdown_content: str,
    embedding: Optional[List[float]],
    pdf_path: Optional[str] = None,
) -> Optional[str]:
    """Upserts fetched content, embedding, and PDF path to Supabase using the SQL function."""
    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            logger.error("Supabase client unavailable. Cannot upsert content.")
            return None

        # Generate a unique content_id (e.g., UUID) for new entries
        # The SQL function handles finding existing entries by URL
        content_id = str(uuid.uuid4())

        # Prepare parameters for the SQL function
        params = {
            "p_content_id": content_id,
            "p_title": title,
            "p_url": url,
            "p_content": markdown_content,
            "p_embedding": embedding,  # Pass the list of floats
            "p_pdf_path": pdf_path,
            # "p_source_file": None # Or pass pdf_path here if using source_file column
        }

        logger.info(f"Calling Supabase RPC upsert_webpage_content for URL: {url}")
        response = await asyncio.to_thread(
            supabase_client.rpc("upsert_webpage_content", params).execute
        )
        # response = supabase_client.rpc('upsert_webpage_content', params).execute() # Original sync call

        # Check response (supabase-py v1 might differ from v2 in response structure)
        # Assuming response.data contains the returned content_id
        if hasattr(response, "data") and response.data:
            returned_id = response.data
            logger.info(
                f"Successfully upserted content for URL {url}. Returned ID: {returned_id}"
            )
            return returned_id
        elif hasattr(response, "error") and response.error:
            logger.error(
                f"Supabase RPC error upserting content for {url}: {response.error}"
            )
            return None
        else:
            # Handle unexpected response structure (log and return None)
            logger.warning(
                f"Unexpected response structure from Supabase upsert RPC for {url}: {response}"
            )
            return None

    except Exception as e:
        logger.error(
            f"Error upserting content to Supabase for URL {url}: {e}", exc_info=True
        )
        return None


# --- Helper: Update Fetch History Record ---
async def _update_fetch_history_record(
    supabase_client: Any,  # from supabase import Client as SupabaseClient - or use Any
    history_id: Optional[uuid.UUID],
    update_data: Dict[str, Any],
    all_request_params_for_history: Dict[str, Any],
) -> Tuple[
    Optional[str], bool
]:  # Returns (SSE message string or None, db_write_successful_flag)
    """
    Helper to update a fetch_history record.
    Returns an SSE message string for the event_generator to yield,
    and a boolean indicating if the database write operation was successful for this call.
    The database update itself is attempted regardless.
    """
    if not history_id or not supabase_client:
        logger.warning(
            f"Attempted to update fetch history with invalid history_id ({history_id}) or supabase_client."
        )
        return format_sse_message(
            "error",
            "history_update_skipped_invalid_params",
            {
                "message": f"Skipping history update for {history_id} due to invalid client or ID."
            },
        ), False

    payload_to_send = {
        **update_data,
        "engine_specific_parameters": all_request_params_for_history,
    }
    # Ensure no None values accidentally overwrite existing data unless intended by update_data
    payload_to_send = {
        k: v for k, v in payload_to_send.items() if v is not None or k in update_data
    }

    sse_message_to_yield: Optional[str] = None
    db_write_successful = False
    try:
        logger.info(
            f"Attempting to update fetch_history record ID: {history_id} with status: {update_data.get('status')}"
        )
        update_response = await asyncio.to_thread(
            supabase_client.table("fetch_history")
            .update(payload_to_send)
            .eq("id", history_id)
            .execute
        )

        if hasattr(update_response, "data") and update_response.data:
            logger.info(
                f"Successfully updated fetch history {history_id} with status: {update_data.get('status')}"
            )
            sse_message_to_yield = format_sse_message(
                "status",
                "history_updated",
                {
                    "message": f"Fetch history record {history_id} updated.",
                    "status": update_data.get("status"),
                },
            )
            db_write_successful = True
        elif hasattr(update_response, "error") and update_response.error:
            err_msg = (
                update_response.error.message
                if hasattr(update_response.error, "message")
                else str(update_response.error)
            )
            logger.error(f"Failed to update fetch history {history_id}: {err_msg}")
            sse_message_to_yield = format_sse_message(
                "warning",
                "history_update_failed",
                {"message": f"Could not update history record {history_id}: {err_msg}"},
            )
        else:
            logger.error(
                f"Unexpected response structure when updating fetch history {history_id}: {update_response}"
            )
            sse_message_to_yield = format_sse_message(
                "warning",
                "history_update_unexpected_response",
                {"message": f"Unexpected DB response for history update {history_id}."},
            )
    except Exception as e:
        logger.error(
            f"Exception updating fetch history {history_id}: {e}", exc_info=True
        )
        sse_message_to_yield = format_sse_message(
            "warning",
            "history_update_exception",
            {"message": f"Exception during history update for {history_id}: {str(e)}"},
        )

    return sse_message_to_yield, db_write_successful


# --- Fetch Content Endpoint (MODIFIED for SSE) ---
@app.get("/fetch-content", tags=["Content Fetch"])
async def fetch_content_endpoint(
    request: Request,  # Added Request for client host logging
    url: str = Query(..., description="URL to fetch content from"),
    engine: str = Query(
        "jina", description="Fetching engine to use ('jina' or 'crawl4ai')"
    ),
    generate_pdf: bool = Query(
        True,
        description="Generate PDF from fetched content (used by both engines if capable)",
    ),
    upload_to_supabase: bool = Query(
        False,
        description="Upload content and embedding to Supabase (post-fetch process)",
    ),
    # --- Browser/Crawling Generic Parameters (used by crawl4ai, some by Jina if applicable) ---
    headless: Optional[bool] = Query(
        True, description="Run browser in headless mode (crawl4ai)"
    ),
    user_agent: Optional[str] = Query(
        None, description="Custom user agent string for the browser (crawl4ai)"
    ),
    proxy_url: Optional[str] = Query(
        None, description="Proxy URL for browser requests (crawl4ai)"
    ),  # ADDED
    enable_javascript: Optional[bool] = Query(
        True, description="Enable JavaScript execution (crawl4ai)"
    ),
    ignore_https_errors: Optional[bool] = Query(
        True, description="Ignore HTTPS errors (crawl4ai)"
    ),  # ADDED
    light_mode: Optional[bool] = Query(
        False, description="Enable light mode (reduces resource usage) (crawl4ai)"
    ),  # ADDED
    text_mode: Optional[bool] = Query(
        False, description="Enable text-only mode (crawl4ai)"
    ),  # ADDED
    browser_cookies: Optional[str] = Query(
        None, description="JSON string of cookies to set (crawl4ai)"
    ),  # ADDED
    browser_headers: Optional[str] = Query(
        None, description="JSON string of headers to set (crawl4ai)"
    ),  # ADDED
    browser_use_persistent_context: Optional[bool] = Query(
        False, description="Use persistent browser context (crawl4ai)"
    ),  # ADDED
    browser_user_data_dir: Optional[str] = Query(
        None, description="Path to browser user data directory (crawl4ai)"
    ),  # ADDED
    browser_extra_args: Optional[str] = Query(
        None, description="Comma-separated list of extra browser arguments (crawl4ai)"
    ),  # ADDED
    viewport_width: Optional[int] = Query(
        None, description="Browser viewport width (crawl4ai)"
    ),  # ADDED
    viewport_height: Optional[int] = Query(
        None, description="Browser viewport height (crawl4ai)"
    ),  # ADDED
    browser_engine: str = Query(
        "playwright",
        description="Browser engine ('playwright' or 'selenium') (crawl4ai, Jina)",
    ),
    browser_viewport: str = Query(
        "1920x1080",
        description="Browser viewport (e.g., '1920x1080') (Jina specific, use viewport_width/height for crawl4ai)",
    ),  # Clarified
    browser_locale: str = Query(
        "en-US", description="Browser locale (e.g., 'en-US') (crawl4ai, Jina)"
    ),
    take_screenshot: Optional[bool] = Query(
        False, description="Enable screenshot capture (crawl4ai)"
    ),
    take_screenshot_on_error: Optional[bool] = Query(
        True,
        description="Capture screenshot if an error occurs during crawling (crawl4ai)",
    ),
    respect_robots_txt: Optional[bool] = Query(
        True, description="Whether to respect robots.txt rules (crawl4ai)"
    ),
    # --- Timeouts ---
    jina_timeout_seconds: int = Query(
        300, description="Timeout in seconds for Jina fetch operation"
    ),
    crawl4ai_interaction_timeout_ms: Optional[int] = Query(
        30000,
        description="Page interaction timeout for crawl4ai in ms (e.g., for JS execution)",
    ),
    navigation_timeout_ms: Optional[int] = Query(
        60000, description="Page navigation timeout for crawl4ai in ms"
    ),
    page_load_timeout_ms: Optional[int] = Query(
        None,
        description="Overall page load timeout for crawl4ai in ms (defaults to navigation_timeout_ms if None)",
    ),  # Matches crawl4ai_fetcher
    page_load_wait_condition: Optional[str] = Query(
        None,
        description="Page load wait condition (e.g., 'load', 'domcontentloaded', 'networkidle') (crawl4ai)",
    ),  # ADDED
    wait_for_element_js_condition: Optional[str] = Query(
        None,
        description="JavaScript expression to wait for before proceeding (crawl4ai)",
    ),  # ADDED
    # --- Content Extraction & Formatting Parameters (primarily crawl4ai, some overlap with Jina) ---
    target_selector: Optional[str] = Query(
        None,
        description="CSS Selector for target elements to focus on (crawl4ai, Jina)",
    ),  # Renamed from target_elements_css_selectors
    excluded_selector: Optional[str] = Query(
        None, description="CSS Selector for elements to exclude (crawl4ai, Jina)"
    ),  # Renamed from excluded_elements_css_selector
    excluded_tags: Optional[str] = Query(
        None, description="Comma-separated list of HTML tags to exclude (crawl4ai)"
    ),  # ADDED
    extract_only_text_content: Optional[bool] = Query(
        False, description="Extract only text content, no HTML structure (crawl4ai)"
    ),  # ADDED
    process_iframes_content: Optional[bool] = Query(
        False, description="Process content within iframes (crawl4ai)"
    ),  # ADDED
    word_count_threshold: Optional[int] = Query(
        None,
        description="Minimum word count for content to be considered valid (crawl4ai)",
    ),  # ADDED
    remove_forms: Optional[bool] = Query(
        False, description="Remove form elements from content (crawl4ai)"
    ),  # ADDED
    keep_data_attributes: Optional[bool] = Query(
        False, description="Keep data-* attributes in HTML (crawl4ai)"
    ),  # ADDED
    execute_javascript_on_page_load: Optional[str] = Query(
        None, description="JavaScript code to execute on page load (crawl4ai)"
    ),  # ADDED
    scan_full_page_auto_scroll: Optional[bool] = Query(
        False, description="Enable auto-scroll to capture full page content (crawl4ai)"
    ),  # ADDED
    scroll_delay_seconds: Optional[float] = Query(
        None,
        description="Delay in seconds between scrolls for full page capture (crawl4ai)",
    ),  # ADDED
    attempt_remove_overlay_elements: Optional[bool] = Query(
        False, description="Attempt to remove overlay elements (crawl4ai)"
    ),  # ADDED
    simulate_user_behavior: Optional[bool] = Query(
        False, description="Simulate user behavior like mouse movements (crawl4ai)"
    ),  # ADDED
    enable_magic_handling: Optional[bool] = Query(
        False,
        description="Enable crawl4ai's 'magic' handling for complex sites (crawl4ai)",
    ),  # ADDED
    override_navigator_properties: Optional[bool] = Query(
        False, description="Override browser navigator properties (crawl4ai)"
    ),  # ADDED
    cache_mode: Optional[str] = Query(
        None,
        description="Cache mode for crawl4ai (e.g., 'ENABLED', 'BYPASS', 'REFRESH')",
    ),  # ADDED
    capture_screenshot_base64: Optional[bool] = Query(
        False, description="Capture screenshot as base64 (crawl4ai)"
    ),  # ADDED (distinct from take_screenshot)
    # generate_pdf: bool = Query(True, ...) is already present
    capture_mhtml_snapshot: Optional[bool] = Query(
        False, description="Capture MHTML snapshot of the page (crawl4ai)"
    ),  # ADDED
    exclude_external_images: Optional[bool] = Query(
        False, description="Exclude external images from extraction (crawl4ai)"
    ),  # ADDED
    image_alt_text_min_word_count: Optional[int] = Query(
        None,
        description="Min word count for image alt text to be considered (crawl4ai)",
    ),  # ADDED
    image_relevance_score_threshold: Optional[int] = Query(
        None, description="Relevance score threshold for images (crawl4ai)"
    ),  # ADDED
    exclude_external_links: Optional[bool] = Query(
        False, description="Exclude external links from extraction (crawl4ai)"
    ),  # ADDED
    exclude_social_media_links: Optional[bool] = Query(
        False, description="Exclude social media links (crawl4ai)"
    ),  # ADDED
    custom_excluded_domains: Optional[str] = Query(
        None, description="Comma-separated list of custom domains to exclude (crawl4ai)"
    ),  # ADDED
    # respect_robots_txt: Optional[bool] = Query(True, ...) is already present
    verbose_logging: Optional[bool] = Query(
        False, description="Enable verbose logging for crawl4ai"
    ),  # ADDED
    log_page_console_output: Optional[bool] = Query(
        False, description="Log page console output during crawl (crawl4ai)"
    ),  # ADDED
    crawl_session_id: Optional[str] = Query(
        None, description="Session ID for crawl4ai"
    ),  # ADDED
    crawl_css_selector: Optional[str] = Query(
        None,
        description="Global CSS selector for crawl4ai (distinct from target_selector)",
    ),  # ADDED
    crawl4ai_markdown_generator: Optional[str] = Query(
        None, description="Specify markdown generator for crawl4ai (e.g., 'Default')"
    ),  # ADDED
    # --- Deep Crawl Individual Parameters (used if deep_crawl_config blob is not provided) ---
    deep_crawl_strategy_name: Optional[str] = Query(
        None,
        alias="deep_crawl_strategy_name",
        description="Name of the deep crawl strategy (e.g., BFSDeepCrawlStrategy)",
    ),
    deep_crawl_max_depth: Optional[int] = Query(
        None,
        alias="deep_crawl_max_depth",
        description="Maximum depth for deep crawling",
    ),
    deep_crawl_max_pages: Optional[int] = Query(
        None,
        alias="deep_crawl_max_pages",
        description="Maximum number of pages for deep crawling",
    ),
    deep_crawl_include_external: Optional[bool] = Query(
        None,
        alias="deep_crawl_include_external",
        description="Include external links in deep crawl",
    ),
    deep_crawl_score_threshold: Optional[float] = Query(
        None,
        alias="deep_crawl_score_threshold",
        description="Score threshold for deep crawl strategies like BFS/DFS",
    ),
    deep_crawl_filter_regexes: Optional[str] = Query(
        None,
        alias="deep_crawl_filter_regexes",
        description="Comma-separated regex patterns for URL filtering in deep crawl",
    ),
    deep_crawl_url_scorer_type: Optional[str] = Query(
        None,
        alias="deep_crawl_url_scorer_type",
        description="Type of URL scorer for BestFirstCrawlingStrategy (e.g., KeywordRelevanceScorer)",
    ),
    deep_crawl_scorer_keywords: Optional[str] = Query(
        None,
        alias="deep_crawl_scorer_keywords",
        description="Comma-separated keywords for KeywordRelevanceScorer",
    ),
    deep_crawl_scorer_weight: Optional[float] = Query(
        None,
        alias="deep_crawl_scorer_weight",
        description="Weight for KeywordRelevanceScorer",
    ),
    deep_crawl_config: Optional[str] = Query(
        None, description="JSON string for deep crawl strategy configuration (crawl4ai)"
    ),  # ADDED
    extraction_config: Optional[str] = Query(
        None, description="JSON string for extraction strategy configuration (crawl4ai)"
    ),  # ADDED
    extraction_strategy: Optional[str] = Query(
        None, # Changed default from "markdown" to None
        description="Content extraction strategy for crawl4ai (e.g., 'llm', 'cosine', 'jsoncss', or None for default processing)",
    ),  # This was for Jina, now more general
    output_format: Optional[str] = Query(
        "markdown",
        description="Desired output format from crawl4ai (e.g., 'markdown', 'text')",
    ),  # This was for Jina, now more general
    token_budget: int = Query(
        4000,
        description="Max tokens for content processing (crawl4ai token_limit, Jina token_budget)",
    ),
    remove_images: bool = Query(
        False, description="Remove images from content (crawl4ai, Jina)"
    ),
    extract_links: bool = Query(
        True, description="Extract links from content (crawl4ai, Jina)"
    ),
    extract_metadata: bool = Query(
        True, description="Extract page metadata (crawl4ai, Jina)"
    ),
    markdown_flavor: str = Query(
        "github", description="Markdown flavor for output (crawl4ai, Jina)"
    ),
    # --- LLM Specific Parameters (for crawl4ai's LLM features like captioning or LLM extraction) ---
    image_captioning: bool = Query(
        False, description="Enable image captioning (crawl4ai with LLM, Jina)"
    ),
    llm_provider: Optional[str] = Query(
        None,
        alias="crawl4ai_llm_provider_model",
        description="LLM provider and model for crawl4ai (e.g., 'gemini/gemini-pro', 'openai/gpt-3.5-turbo', 'ollama/mistral')"
    ),
    llm_api_key: Optional[str] = Query(
        None,
        description="API key for the LLM provider (use environment variables if None)",
    ),
    crawl4ai_llm_base_url: Optional[str] = Query( # ADDED
        None, description="Base URL for the LLM provider (crawl4ai)" # ADDED
    ), # ADDED
    llm_temperature: Optional[float] = Query(
        0.7, ge=0.0, le=2.0, description="LLM temperature for crawl4ai"
    ),
    llm_max_tokens: Optional[int] = Query(
        1000, ge=1, description="LLM max tokens for generation for crawl4ai"
    ),
    # --- Jina Specific Parameters (ignored by crawl4ai) ---
    json_response: bool = Query(
        True,
        description="Request raw JSON response from Jina (contains metadata) (Jina specific)",
    ),  # Should be Jina specific
    cache_ttl: int = Query(
        3600, description="Cache TTL in seconds (Jina specific)"
    ),  # Should be Jina specific
):
    """
    Fetches content using the specified engine and streams progress via SSE.
    Optionally generates PDF, generates embedding, and stores in Supabase.
    """
    client_host = request.client.host if request.client else "unknown"
    logger.info(
        f"SSE /fetch-content request from {client_host} for URL: {url}, Engine: {engine}, PDF: {generate_pdf}, Supabase: {upload_to_supabase}"
    )

    if not PROJECT_MODULES_LOADED:

        async def error_gen_no_modules():
            yield format_sse_message(
                "error", "Core project modules not loaded. Fetch feature unavailable."
            )

        return EventSourceResponse(error_gen_no_modules())

    # Gather all original request parameters for potential use by fetchers
    all_request_params = {
        "url": url,
        "engine": engine,
        "generate_pdf": generate_pdf,
        "upload_to_supabase": upload_to_supabase,
        "headless": headless,
        "user_agent": user_agent,
        "proxy_url": proxy_url,  # ADDED
        "enable_javascript": enable_javascript,
        "ignore_https_errors": ignore_https_errors,  # ADDED
        "light_mode": light_mode,
        "text_mode": text_mode,  # ADDED
        "browser_cookies": browser_cookies,
        "browser_headers": browser_headers,  # ADDED
        "browser_use_persistent_context": browser_use_persistent_context,  # ADDED
        "browser_user_data_dir": browser_user_data_dir,
        "browser_extra_args": browser_extra_args,  # ADDED
        "viewport_width": viewport_width,
        "viewport_height": viewport_height,  # ADDED
        "browser_engine": browser_engine,
        "browser_viewport": browser_viewport,
        "browser_locale": browser_locale,
        "take_screenshot": take_screenshot,
        "take_screenshot_on_error": take_screenshot_on_error,
        "respect_robots_txt": respect_robots_txt,
        "jina_timeout_seconds": jina_timeout_seconds,
        "crawl4ai_interaction_timeout_ms": crawl4ai_interaction_timeout_ms,
        "navigation_timeout_ms": navigation_timeout_ms,
        "page_load_timeout_ms": page_load_timeout_ms,
        "page_load_wait_condition": page_load_wait_condition,  # ADDED
        "wait_for_element_js_condition": wait_for_element_js_condition,  # ADDED
        "target_selector": target_selector,
        "excluded_selector": excluded_selector,
        "excluded_tags": excluded_tags,  # ADDED
        "extract_only_text_content": extract_only_text_content,  # ADDED
        "process_iframes_content": process_iframes_content,  # ADDED
        "word_count_threshold": word_count_threshold,  # ADDED
        "remove_forms": remove_forms,
        "keep_data_attributes": keep_data_attributes,  # ADDED
        "execute_javascript_on_page_load": execute_javascript_on_page_load,  # ADDED
        "scan_full_page_auto_scroll": scan_full_page_auto_scroll,  # ADDED
        "scroll_delay_seconds": scroll_delay_seconds,  # ADDED
        "attempt_remove_overlay_elements": attempt_remove_overlay_elements,  # ADDED
        "simulate_user_behavior": simulate_user_behavior,  # ADDED
        "enable_magic_handling": enable_magic_handling,  # ADDED
        "override_navigator_properties": override_navigator_properties,  # ADDED
        "cache_mode": cache_mode,  # ADDED
        "capture_screenshot_base64": capture_screenshot_base64,  # ADDED
        "capture_mhtml_snapshot": capture_mhtml_snapshot,  # ADDED
        "exclude_external_images": exclude_external_images,  # ADDED
        "image_alt_text_min_word_count": image_alt_text_min_word_count,  # ADDED
        "image_relevance_score_threshold": image_relevance_score_threshold,  # ADDED
        "exclude_external_links": exclude_external_links,  # ADDED
        "exclude_social_media_links": exclude_social_media_links,  # ADDED
        "custom_excluded_domains": custom_excluded_domains,  # ADDED
        "verbose_logging": verbose_logging,
        "log_page_console_output": log_page_console_output,  # ADDED
        "crawl_session_id": crawl_session_id,
        "crawl_css_selector": crawl_css_selector,  # ADDED
        "crawl4ai_markdown_generator": crawl4ai_markdown_generator,  # ADDED
        # Deep Crawl Individual Parameters
        "deep_crawl_strategy_name": deep_crawl_strategy_name,
        "deep_crawl_max_depth": deep_crawl_max_depth,
        "deep_crawl_max_pages": deep_crawl_max_pages,
        "deep_crawl_include_external": deep_crawl_include_external,
        "deep_crawl_score_threshold": deep_crawl_score_threshold,
        "deep_crawl_filter_regexes": deep_crawl_filter_regexes,
        "deep_crawl_url_scorer_type": deep_crawl_url_scorer_type,
        "deep_crawl_scorer_keywords": deep_crawl_scorer_keywords,
        "deep_crawl_scorer_weight": deep_crawl_scorer_weight,
        "deep_crawl_config": deep_crawl_config,  # This is the JSON blob
        "extraction_config": extraction_config,  # ADDED
        "extraction_strategy": extraction_strategy,
        "output_format": output_format,
        "token_budget": token_budget,
        "remove_images": remove_images,
        "extract_links": extract_links,
        "extract_metadata": extract_metadata,
        "markdown_flavor": markdown_flavor,
        "image_captioning": image_captioning,
        "llm_provider": llm_provider,
        "llm_api_key": llm_api_key,
        "crawl4ai_llm_base_url": crawl4ai_llm_base_url, # ADDED
        "llm_temperature": llm_temperature,
        "llm_max_tokens": llm_max_tokens,
        "json_response": json_response,
        "cache_ttl": cache_ttl,
    }
    # logger.debug(f"All request params for /fetch-content: {all_request_params}")

    # logger.debug(f"All request params for /fetch-content: {all_request_params}")

    async def event_generator():
        # --- Fetch History Variables ---
        fetch_history_id: Optional[uuid.UUID] = None
        supabase_client_for_history: Optional[Any] = None  # Holds Supabase client
        terminal_status_written_to_db: bool = False  # NEW: Tracks if 'success' or 'failed' status was successfully written

        # --- Other original variables ---
        fetched_data_dict: Optional[Dict[str, Any]] = None
        markdown_content: Optional[str] = None
        title: str = "Untitled"
        fetched_url_actual: str = url
        pdf_relative_path: Optional[str] = None
        embedding_generated: bool = False
        supabase_content_id_str: Optional[str] = None

        try:
            # --- Get Supabase Client for History ---
            try:
                supabase_client_for_history = get_client()
                if not supabase_client_for_history:
                    logger.error(
                        "Failed to get Supabase client for fetch history (get_client returned None)."
                    )
                    yield format_sse_message(
                        "error",
                        "database_client_unavailable",
                        {
                            "message": "Database client is essential for history tracking and is unavailable."
                        },
                    )
                    return  # Stop if DB client cannot be obtained
            except RuntimeError as e_db_client:
                logger.error(
                    f"RuntimeError getting Supabase client for fetch history: {e_db_client}",
                    exc_info=True,
                )
                yield format_sse_message(
                    "error",
                    "database_connection_failed",
                    {
                        "message": f"Database connection error for history: {str(e_db_client)}"
                    },
                )
                return  # Stop if DB client cannot be obtained
            except Exception as e_db_client_other:
                logger.error(
                    f"Unexpected error getting Supabase client for fetch history: {e_db_client_other}",
                    exc_info=True,
                )
                yield format_sse_message(
                    "error",
                    "database_client_error",
                    {
                        "message": f"Unexpected database client error for history: {str(e_db_client_other)}"
                    },
                )
                return

            # --- Create Initial Fetch History Record ---
            if supabase_client_for_history:
                try:
                    initial_history_payload_dict = {
                        "url": url,
                        "fetching_engine": engine,
                        "status": "pending",
                        # engine_specific_parameters will be added in the final update
                    }
                    # Validate with Pydantic model before sending to DB
                    FetchHistoryCreate(**initial_history_payload_dict)

                    create_response = await asyncio.to_thread(
                        supabase_client_for_history.table("fetch_history")
                        .insert(initial_history_payload_dict)
                        .execute
                    )
                    if hasattr(create_response, "data") and create_response.data:
                        fetch_history_id = create_response.data[0].get("id")
                        if fetch_history_id:
                            logger.info(
                                f"Initial fetch history record created with ID: {fetch_history_id} for URL: {url}"
                            )
                            yield format_sse_message(
                                "status",
                                "history_created",
                                {
                                    "message": f"Fetch history record created: {fetch_history_id}",
                                    "history_id": str(fetch_history_id),
                                },
                            )
                        else:
                            logger.error(
                                f"Initial fetch history record created for {url} but ID was not returned in data: {create_response.data}"
                            )
                            yield format_sse_message(
                                "warning",
                                "history_creation_no_id",
                                {"message": "History record created but ID missing."},
                            )
                    elif hasattr(create_response, "error") and create_response.error:
                        err_msg = (
                            create_response.error.message
                            if hasattr(create_response.error, "message")
                            else str(create_response.error)
                        )
                        logger.error(
                            f"Failed to create initial fetch history record for {url}: {err_msg}"
                        )
                        yield format_sse_message(
                            "warning",
                            "history_creation_failed",
                            {
                                "message": f"Could not create initial history record: {err_msg}"
                            },
                        )
                    else:
                        logger.error(
                            f"Unexpected response from Supabase during initial fetch history creation for {url}: {create_response}"
                        )
                        yield format_sse_message(
                            "warning",
                            "history_creation_unexpected_response",
                            {
                                "message": "Unexpected DB response for initial history creation."
                            },
                        )
                except ValidationError as ve:
                    logger.error(
                        f"Validation error for initial fetch history payload for {url}: {ve.errors()}",
                        exc_info=True,
                    )
                    yield format_sse_message(
                        "error",
                        "history_payload_invalid",
                        {"message": f"Initial history data invalid: {str(ve)}"},
                    )
                    # Potentially return if this is critical
                except Exception as e_hist_create:
                    logger.error(
                        f"Exception creating initial fetch history for {url}: {e_hist_create}",
                        exc_info=True,
                    )
                    yield format_sse_message(
                        "warning",
                        "history_creation_exception",
                        {
                            "message": f"Error during initial history creation: {str(e_hist_create)}"
                        },
                    )

            yield format_sse_message(
                "status",
                "initializing",
                {"message": f"Initializing fetch process for {url} with {engine}..."},
            )
            await asyncio.sleep(0.1)  # Small delay for frontend to catch up

            if engine.lower() == "crawl4ai":
                if (
                    fetch_with_crawl4ai is None
                ):  # Check if the function itself is available
                    yield format_sse_message(
                        "error", "Crawl4ai fetcher module not available."
                    )
                    # Update history if possible
                    if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                        error_update_data = {
                            "status": "failed",
                            "error_message": "Crawl4ai fetcher module not available on server.",
                        }
                        _, db_write_ok = await _update_fetch_history_record(
                            supabase_client_for_history,
                            fetch_history_id,
                            error_update_data,
                            all_request_params,
                        )
                        if db_write_ok: terminal_status_written_to_db = True
                    return
                logger.info(f"Using crawl4ai engine for URL: {url}")
                async for sse_event_json_str_from_fetcher in fetch_with_crawl4ai(
                    url=url, original_request_params=all_request_params
                ):
                    try:
                        event_data_from_fetcher = json.loads(
                            sse_event_json_str_from_fetcher
                        )

                        # --- LLM Logging Integration ---
                        if event_data_from_fetcher.get("type") == "llm_log_event":
                            llm_log_data = event_data_from_fetcher.get("data")
                            if (
                                llm_log_data and supabase_client_for_history
                            ):  # Ensure data and client exist
                                try:
                                    # Use await if log_llm_call is async, otherwise remove await
                                    await log_llm_call(
                                        llm_log_data_dict=llm_log_data,
                                        supabase_client=supabase_client_for_history,
                                    )
                                    logger.info(
                                        f"LLM call logged for type: {llm_log_data.get('llm_call_type')}, model: {llm_log_data.get('model_name')}"
                                    )
                                except Exception as e_log_llm:
                                    logger.error(
                                        f"Failed to log LLM call via utility: {e_log_llm}",
                                        exc_info=True,
                                    )
                            elif not llm_log_data:
                                logger.warning(
                                    "llm_log_event received but 'data' payload was missing."
                                )
                            elif not supabase_client_for_history:
                                logger.warning(
                                    "llm_log_event received but supabase_client_for_history was not available for logging."
                                )
                            continue  # Skip yielding this event to the client
                        # --- End LLM Logging Integration ---

                        # --- Populate fetched_data_dict if it's the main crawl result ---
                        if event_data_from_fetcher.get("type") == "crawl_result":
                            logger.info(f"Storing data from crawl_result event for URL: {event_data_from_fetcher.get('url')}")
                            
                            # Attempt to extract title
                            current_title = event_data_from_fetcher.get("metadata", {}).get("title")
                            if not current_title and event_data_from_fetcher.get("markdown"):
                                # Try to get from H1 in markdown
                                title_match_md = re.search(r"^#\s*(.+)", event_data_from_fetcher.get("markdown", ""), re.MULTILINE)
                                if title_match_md:
                                    current_title = title_match_md.group(1).strip()
                            # Fallback title if none found from metadata or markdown H1
                            if not current_title: 
                                current_title = f"Content from {event_data_from_fetcher.get('url', url)}"

                            # This variable is used after the loop for PDF/Supabase
                            fetched_data_dict = {
                                "url": event_data_from_fetcher.get("url", url),
                                "title": current_title,
                                "markdown": event_data_from_fetcher.get("markdown"),
                                "content": event_data_from_fetcher.get("content"), # HTML content
                                "text": event_data_from_fetcher.get("text"),
                                "links": event_data_from_fetcher.get("links", []),
                                "metadata": event_data_from_fetcher.get("metadata", {}),
                                "screenshot_base64": event_data_from_fetcher.get("screenshot_base64"),
                                "status_code": event_data_from_fetcher.get("status_code"),
                                "error": event_data_from_fetcher.get("error_message") or event_data_from_fetcher.get("error"),
                                # pdf_path will be added later by main.py if PDF generation is successful
                            }
                            logger.debug(f"Internal fetched_data_dict populated from crawl_result. Title: {fetched_data_dict.get('title')}, URL: {fetched_data_dict.get('url')}")
                        
                        # --- Construct the SSE event to send to the client ---
                        final_sse_event_dict = {
                            "type": event_data_from_fetcher.get("type"),
                            "timestamp": datetime.now(timezone.utc).isoformat(), # Ensure UTC
                            "id": str(uuid.uuid4().hex), # Use hex for shorter unique ID
                        }
                        if "status" in event_data_from_fetcher:
                            final_sse_event_dict["status"] = (
                                event_data_from_fetcher.get("status")
                            )

                        # Populate message/details for error events for the client
                        if (
                            event_data_from_fetcher.get("type") == "error"
                            and "llm_error" in event_data_from_fetcher
                        ):
                            final_sse_event_dict["message"] = (
                                event_data_from_fetcher.get(
                                    "message", "LLM operation failed."
                                )
                            )
                            final_sse_event_dict["llm_error"] = event_data_from_fetcher[
                                "llm_error"
                            ]
                            logger.error(
                                f"LLM Error event from crawl4ai_fetcher: {json.dumps(event_data_from_fetcher['llm_error'])}"
                            )
                        elif event_data_from_fetcher.get("type") == "error":
                            # General error from crawl4ai_fetcher
                            if "message" in event_data_from_fetcher:
                                final_sse_event_dict["message"] = (
                                    event_data_from_fetcher.get("message")
                                )
                            if "details" in event_data_from_fetcher:
                                final_sse_event_dict["details"] = (
                                    event_data_from_fetcher.get("details")
                                )
                        else: # Non-error events - populate 'content' for the client
                            client_facing_content_payload = {}
                            if "message" in event_data_from_fetcher: # Messages are always useful
                                client_facing_content_payload["message"] = event_data_from_fetcher.get("message")

                            # For crawl_result events, provide a summary/data subset to the client
                            if event_data_from_fetcher.get("type") == "crawl_result" and fetched_data_dict: # Check fetched_data_dict to ensure it was populated
                                client_facing_content_payload["data"] = {
                                    "url": fetched_data_dict.get("url"),
                                    "title": fetched_data_dict.get("title"), # Use consistent title
                                    "status_code": fetched_data_dict.get("status_code"),
                                    "error": fetched_data_dict.get("error"), # Pass error if present in main data
                                    "markdown_preview": (fetched_data_dict.get("markdown") or "")[:250] + "..." if fetched_data_dict.get("markdown") else "No markdown content.",
                                    "text_preview": (fetched_data_dict.get("text") or "")[:250] + "..." if fetched_data_dict.get("text") else "No text content.",
                                    "has_screenshot": bool(fetched_data_dict.get("screenshot_base64")),
                                    "links_count": len(fetched_data_dict.get("links", [])),
                                }
                            elif "data" in event_data_from_fetcher: # For other event types that might have a 'data' field (e.g. from Jina, or a 'completed' event with data)
                                client_facing_content_payload["data"] = event_data_from_fetcher.get("data")
                            
                            if client_facing_content_payload:
                                final_sse_event_dict["content"] = client_facing_content_payload
                            elif "message" in event_data_from_fetcher: # Fallback if only a message
                                final_sse_event_dict["content"] = event_data_from_fetcher.get("message")
                        
                        # Note: The original logic that set `fetched_data_dict` from a "completed" event's "data" field
                        # is intentionally omitted here for the crawl4ai loop, as `crawl_result` is the definitive source.
                        # If a "completed" event from crawl4ai were to have a "data" field with essential *additional* info
                        # for `fetched_data_dict`, that would need separate handling, but current fetcher doesn't do that.

                        logger.info(
                            f"Yielding to client from crawl4ai loop: Type '{final_sse_event_dict.get('type')}', Status: '{final_sse_event_dict.get('status', 'N/A')}', ID: {final_sse_event_dict.get('id')}"
                        )
                        yield json.dumps(final_sse_event_dict)

                        if (
                            event_data_from_fetcher.get("type") == "error"
                            or event_data_from_fetcher.get("status") == "error"
                        ):
                            error_message_for_db = str(
                                event_data_from_fetcher.get(
                                    "message", "Unknown error from fetcher"
                                )
                            )
                            if "llm_error" in event_data_from_fetcher and isinstance(
                                event_data_from_fetcher["llm_error"], dict
                            ):
                                error_message_for_db = f"LLM Error: {event_data_from_fetcher['llm_error'].get('message', error_message_for_db)}. Details: {json.dumps(event_data_from_fetcher['llm_error'].get('details'))}"

                            logger.error(
                                f"Error event from crawl4ai_fetcher: {error_message_for_db}"
                            )
                            if fetch_history_id and supabase_client_for_history:
                                error_update_data = {
                                    "status": "failed",
                                    "error_message": error_message_for_db[:1000],
                                }
                                _, db_write_ok = await _update_fetch_history_record(
                                    supabase_client_for_history,
                                    fetch_history_id,
                                    error_update_data,
                                    all_request_params,
                                )
                                if db_write_ok and error_update_data.get("status") in [
                                    "success",
                                    "failed",
                                ]:
                                    terminal_status_written_to_db = True
                            return
                    except json.JSONDecodeError:
                        logger.error(
                            f"Failed to decode JSON from crawl4ai_fetcher: {sse_event_json_str_from_fetcher}"
                        )
                        yield format_sse_message(
                            "error", "Received invalid data from crawl4ai engine."
                        )
                        if fetch_history_id and supabase_client_for_history:
                            error_update_data = {
                                "status": "failed",
                                "error_message": "Received invalid JSON data from crawl4ai engine.",
                            }
                            _, db_write_ok = await _update_fetch_history_record(
                                supabase_client_for_history,
                                fetch_history_id,
                                error_update_data,
                                all_request_params,
                            )
                            if db_write_ok and error_update_data.get("status") in [
                                "success",
                                "failed",
                            ]:
                                terminal_status_written_to_db = True
                        return
                    except Exception as e_inner_crawl:
                        logger.error(
                            f"Error processing event from crawl4ai_fetcher: {e_inner_crawl}",
                            exc_info=True,
                        )
                        yield format_sse_message(
                            "error",
                            f"Internal error processing crawl4ai event: {str(e_inner_crawl)}",
                        )
                        if fetch_history_id and supabase_client_for_history:
                            failure_update_data = {
                                "status": "failed",
                                "error_message": f"Internal error processing crawl4ai event: {str(e_inner_crawl)}"[
                                    :1000
                                ],
                            }
                            _, db_write_ok = await _update_fetch_history_record(
                                supabase_client_for_history,
                                fetch_history_id,
                                failure_update_data,
                                all_request_params,
                            )
                            if db_write_ok and failure_update_data.get("status") in [
                                "success",
                                "failed",
                            ]:
                                terminal_status_written_to_db = True
                        return

            elif engine.lower() == "jina":
                if fetch_content_from_url is None:
                    yield format_sse_message(
                        "error", "Jina fetcher (fetch_content_from_url) not available."
                    )
                    return
                logger.info(f"Using Jina engine for URL: {url}")
                yield format_sse_message(
                    "status",
                    "fetching",
                    {"message": f"Fetching content from {url} with Jina..."},
                )
                try:
                    # json_response is the boolean from the endpoint Query parameters
                    jina_handler_output = await fetch_content_from_url(
                        url=url,
                        json_response=json_response,
                        timeout=jina_timeout_seconds,
                        target_selector=target_selector,
                        excluded_selector=excluded_selector,
                        browser_engine=browser_engine,
                        token_budget=token_budget,
                        remove_images=remove_images,
                        extract_links=extract_links,
                        image_captioning=image_captioning,
                        cache_ttl=cache_ttl,
                        markdown_flavor=markdown_flavor,
                        browser_viewport=browser_viewport,
                        browser_locale=browser_locale,
                        extract_metadata=extract_metadata,
                    )

                    if json_response:  # Client wanted JSON
                        if not isinstance(
                            jina_handler_output, dict
                        ) or jina_handler_output.get("error"):
                            error_detail = (
                                jina_handler_output.get(
                                    "content", "Unknown error from Jina"
                                )
                                if isinstance(jina_handler_output, dict)
                                else str(jina_handler_output)
                            )
                            logger.error(
                                f"Jina engine failed (JSON mode) for {url}. Response: {error_detail[:200]}"
                            )
                            yield format_sse_message(
                                "error", f"Jina engine failed: {error_detail}"
                            )
                            return
                        fetched_data_dict = jina_handler_output
                    else:  # Client wanted plain text (json_response is False)
                        if not isinstance(jina_handler_output, str):
                            logger.error(
                                f"Jina engine (Text mode) for {url} returned non-string: {type(jina_handler_output)}. Content: {str(jina_handler_output)[:200]}"
                            )
                            yield format_sse_message(
                                "error",
                                "Jina engine failed: Invalid response in text mode.",
                            )
                            return

                        title_match = re.search(
                            r"^(?:# |\*\*Title:\*\*|Title:)\s*(.+)",
                            jina_handler_output,
                            re.IGNORECASE | re.MULTILINE,
                        )
                        extracted_title = (
                            title_match.group(1).strip()
                            if title_match
                            else "Untitled (from Text)"
                        )
                        fetched_data_dict = {
                            "markdown": jina_handler_output,
                            "content": jina_handler_output,
                            "title": extracted_title,
                            "url": url,
                            "links": [],
                            "metadata": {},
                            "pdf_path": None,
                        }

                    yield format_sse_message(
                        "status",
                        "processing",
                        {"message": "Processing content fetched by Jina..."},
                    )
                    await asyncio.sleep(0.5)  # Simulate processing

                except Exception as e_jina:
                    logger.error(
                        f"Error calling Jina fetch_content_from_url for {url}: {e_jina}",
                        exc_info=True,
                    )
                    yield format_sse_message(
                        "error", f"Error with Jina engine: {str(e_jina)}"
                    )
                    return
            else:
                logger.warning(
                    f"Unknown or unsupported engine '{engine}' requested for URL: {url}. Defaulting to Jina."
                )
                # Essentially duplicate Jina logic here or refactor Jina part into a sub-generator
                # For now, let's assume Jina is the default if not crawl4ai
                if fetch_content_from_url is None:
                    yield format_sse_message(
                        "error", "Default Jina fetcher not available."
                    )
                    return
                yield format_sse_message(
                    "status",
                    "fetching",
                    {"message": f"Fetching content from {url} with Jina (default)..."},
                )
                try:
                    # json_response is the boolean from the endpoint Query parameters
                    jina_default_handler_output = await fetch_content_from_url(
                        url=url,
                        json_response=json_response,
                        timeout=jina_timeout_seconds,
                        target_selector=target_selector,
                        excluded_selector=excluded_selector,
                        browser_engine=browser_engine,
                        token_budget=token_budget,
                        remove_images=remove_images,
                        extract_links=extract_links,
                        image_captioning=image_captioning,
                        cache_ttl=cache_ttl,
                        markdown_flavor=markdown_flavor,
                        browser_viewport=browser_viewport,
                        browser_locale=browser_locale,
                        extract_metadata=extract_metadata,
                    )

                    if json_response:  # Client wanted JSON
                        if not isinstance(
                            jina_default_handler_output, dict
                        ) or jina_default_handler_output.get("error"):
                            error_detail = (
                                jina_default_handler_output.get(
                                    "content", "Unknown error from Jina (default)"
                                )
                                if isinstance(jina_default_handler_output, dict)
                                else str(jina_default_handler_output)
                            )
                            logger.error(
                                f"Jina (default) engine failed (JSON mode) for {url}. Response: {error_detail[:200]}"
                            )
                            yield format_sse_message(
                                "error", f"Jina (default) engine failed: {error_detail}"
                            )
                            return
                        fetched_data_dict = jina_default_handler_output
                    else:  # Client wanted plain text
                        if not isinstance(jina_default_handler_output, str):
                            logger.error(
                                f"Jina (default) engine (Text mode) for {url} returned non-string: {type(jina_default_handler_output)}. Content: {str(jina_default_handler_output)[:200]}"
                            )
                            yield format_sse_message(
                                "error",
                                "Jina (default) engine failed: Invalid response in text mode.",
                            )
                            return

                        title_match = re.search(
                            r"^(?:# |\*\*Title:\*\*|Title:)\s*(.+)",
                            jina_default_handler_output,
                            re.IGNORECASE | re.MULTILINE,
                        )
                        extracted_title = (
                            title_match.group(1).strip()
                            if title_match
                            else "Untitled (from Text Default)"
                        )
                        fetched_data_dict = {
                            "markdown": jina_default_handler_output,
                            "content": jina_default_handler_output,
                            "title": extracted_title,
                            "url": url,
                            "links": [],
                            "metadata": {},
                            "pdf_path": None,
                        }

                    yield format_sse_message(
                        "status",
                        "processing",
                        {"message": "Processing content fetched by Jina (default)..."},
                    )
                    await asyncio.sleep(0.5)
                except Exception as e_jina_def:
                    logger.error(
                        f"Error calling Jina (default) for {url}: {e_jina_def}",
                        exc_info=True,
                    )
                    yield format_sse_message(
                        "error", f"Error with Jina (default) engine: {str(e_jina_def)}"
                    )
                    return

            # --- Final check for fetched_data_dict before proceeding (Mainly for crawl4ai path) ---
            if not fetched_data_dict and engine.lower() == "crawl4ai":
                logger.error(
                    f"Failed to retrieve or process data using crawl4ai for {url}. No 'crawl_result' event populated the internal data dictionary."
                )
                yield format_sse_message(
                    "error",
                    "no_crawl_result_data",
                    {
                        "message": "Crawl4AI engine completed but no main data was processed internally. Check fetcher logs for 'crawl_result' event details."
                    },
                )
                # Update history if not already done by an error event
                if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                    final_error_update_data = {
                        "status": "failed",
                        "error_message": "Crawl4AI: No 'crawl_result' data processed by backend.",
                        "output_type": "unknown",
                    }
                    _, db_write_ok = await _update_fetch_history_record(
                        supabase_client_for_history,
                        fetch_history_id,
                        final_error_update_data,
                        all_request_params,
                    )
                    if db_write_ok: terminal_status_written_to_db = True
                return # Critical failure for crawl4ai if fetched_data_dict is still None

            # --- Post-fetch processing (PDF, Supabase) ---
            # This block should now be reliably reached if crawl4ai produced a crawl_result or if Jina succeeded.
            final_data_for_db_and_pdf: Dict[str, Any] = { # For final history update
                "status": "processing_failed", # Default status if subsequent steps fail
                "output_type": "unknown",
                "error_message": None,
                "content_summary": None,
                "raw_content_path": None,
                "processed_content_path": None, # e.g. PDF path
                "supabase_content_id": None,
            }


            if fetched_data_dict and not (fetched_data_dict.get("error") and fetched_data_dict.get("status_code", 200) >= 400):  # If no critical error at the top level of fetched_data_dict
                # Also check status_code if error is present but might be informational (e.g. error key for non-fatal issue)
                # If error is present AND status_code indicates client/server error, then treat as failure.
                
                markdown_content = fetched_data_dict.get("markdown")
                text_content_for_embedding = fetched_data_dict.get("text", markdown_content or "") # Prefer text, fallback to MD
                title = fetched_data_dict.get("title", "Untitled")
                fetched_url_actual = fetched_data_dict.get("url", url)
                pdf_path_from_fetcher = fetched_data_dict.get("pdf_path") # Jina might provide this
                screenshot_base64_data = fetched_data_dict.get("screenshot_base64")

                # Determine primary content type for history
                if markdown_content:
                    final_data_for_db_and_pdf["output_type"] = "markdown"
                elif fetched_data_dict.get("content"): # HTML
                    final_data_for_db_and_pdf["output_type"] = "html"
                elif text_content_for_embedding: # Plain text
                     final_data_for_db_and_pdf["output_type"] = "text"
                
                # Create a summary (first ~300 chars of text or markdown)
                summary_source = text_content_for_embedding if text_content_for_embedding else markdown_content
                if summary_source:
                    final_data_for_db_and_pdf["content_summary"] = (summary_source[:297] + "...") if len(summary_source) > 300 else summary_source


                # --- Yield final content to client (if not already fully sent) ---
                # This provides a consolidated result to the client, especially if PDF/Supabase steps are involved.
                # The 'crawl_result' SSE from crawl4ai fetcher already sent detailed data.
                # This is more of a "final processing summary" for main.py's own steps.
                
                yield format_sse_message(
                    "status",
                    "content_extracted",
                    {
                        "message": f"Content extracted for {fetched_url_actual}. Title: {title}",
                        "title": title,
                        "url": fetched_url_actual,
                        "has_markdown": bool(markdown_content),
                        "has_text": bool(text_content_for_embedding),
                        "has_screenshot": bool(screenshot_base64_data),
                        "output_type": final_data_for_db_and_pdf["output_type"],
                    },
                )
                await asyncio.sleep(0.1)


                if not markdown_content and not text_content_for_embedding and not fetched_data_dict.get("content"):
                    logger.warning(f"No markdown, text, or HTML content found in fetched_data_dict for {url}. PDF generation and Supabase upload might be skipped or fail.")
                    final_data_for_db_and_pdf["status"] = "completed_no_content"
                    final_data_for_db_and_pdf["error_message"] = "Fetcher returned no substantive content (markdown, text, or HTML)."
                    final_data_for_db_and_pdf["output_type"] = "no_content"
                    yield format_sse_message(
                        "warning", 
                        "no_substantive_content",
                        {"message": "No substantive content (markdown, text, or HTML) was found to process further."}
                    )

                else:
                    # --- PDF Generation (if requested and has markdown) ---
                    if generate_pdf:
                        if markdown_content:
                            yield format_sse_message(
                                "status",
                                "pdf_generation_starting",
                                {"message": "Generating PDF from markdown..."},
                            )
                            try:
                                pdf_relative_path = await convert_md_to_pdf_util(
                                    markdown_content, fetched_url_actual, title
                                )
                                if pdf_relative_path:
                                    final_data_for_db_and_pdf["processed_content_path"] = pdf_relative_path
                                    # Update output_type if it was just markdown, now it's also PDF
                                    if final_data_for_db_and_pdf["output_type"] == "markdown":
                                        final_data_for_db_and_pdf["output_type"] = "markdown_and_pdf"
                                    elif final_data_for_db_and_pdf["output_type"] == "html": # if MD was derived from HTML
                                         final_data_for_db_and_pdf["output_type"] = "html_markdown_and_pdf"
                                    else: # text, etc.
                                        final_data_for_db_and_pdf["output_type"] = "pdf"


                                    yield format_sse_message(
                                        "status",
                                        "pdf_generation_complete",
                                        {
                                            "message": f"PDF generated: {pdf_relative_path}",
                                            "pdf_path": pdf_relative_path,
                                            "pdf_url": f"/view-pdf?path={urllib.parse.quote(pdf_relative_path)}",
                                            "download_url": f"/download-pdf?path={urllib.parse.quote(pdf_relative_path)}",
                                        },
                                    )
                                else:
                                    logger.error(f"PDF generation failed for {url}, no path returned.")
                                    yield format_sse_message(
                                        "warning",
                                        "pdf_generation_failed",
                                        {"message": "PDF generation failed."},
                                    )
                            except Exception as e_pdf:
                                logger.error(
                                    f"Error during PDF generation for {url}: {e_pdf}",
                                    exc_info=True,
                                )
                                yield format_sse_message(
                                    "warning",
                                    "pdf_generation_error",
                                    {"message": f"PDF generation error: {str(e_pdf)}"},
                                )
                        elif pdf_path_from_fetcher: # e.g. Jina already made a PDF
                            final_data_for_db_and_pdf["processed_content_path"] = pdf_path_from_fetcher
                            final_data_for_db_and_pdf["output_type"] = "pdf_direct" # Or append if other content types also exist
                            logger.info(f"Using pre-generated PDF from fetcher: {pdf_path_from_fetcher}")
                            yield format_sse_message(
                                "status",
                                "pdf_provided_by_fetcher",
                                {
                                    "message": f"PDF provided by fetcher: {pdf_path_from_fetcher}",
                                    "pdf_path": pdf_path_from_fetcher,
                                    "pdf_url": f"/view-pdf?path={urllib.parse.quote(pdf_path_from_fetcher)}",
                                    "download_url": f"/download-pdf?path={urllib.parse.quote(pdf_path_from_fetcher)}",
                                },
                            )
                        else: # No markdown and no pre-existing PDF from fetcher
                             yield format_sse_message(
                                "status",
                                "pdf_generation_skipped",
                                {"message": "PDF generation skipped (no markdown content or pre-existing PDF)."},
                            )
                    else: # generate_pdf is False
                        yield format_sse_message("status", "pdf_generation_disabled", {"message": "PDF generation disabled by request."})


                    # --- Supabase Upload (if requested and has content) ---
                    if upload_to_supabase:
                        if not text_content_for_embedding and not markdown_content: # Ensure there's something to embed/store
                            logger.warning(f"Supabase upload skipped for {url}: No text or markdown content available for embedding/storage.")
                            yield format_sse_message("warning", "supabase_upload_skipped_no_content", {"message": "Supabase upload skipped: no text/markdown content."})
                        elif not supabase_client_for_history: # Check if client is available (it should be from history creation)
                            logger.error(f"Supabase client not available, skipping upload for {url}.")
                            yield format_sse_message("error", "supabase_client_unavailable_for_upload", {"message": "Supabase client unavailable for upload."})
                        else:
                            yield format_sse_message(
                                "status",
                                "embedding_and_upload_starting",
                                {"message": "Generating embedding and uploading to Supabase..."},
                            )
                            embedding_text = text_content_for_embedding if text_content_for_embedding else markdown_content
                            try:
                                embedding = await get_embedding_with_registry(embedding_text) # Use registry
                                embedding_generated = bool(embedding)
                                
                                if embedding_generated:
                                    yield format_sse_message("status", "embedding_generated", {"message": "Embedding generated."})
                                else:
                                    yield format_sse_message("warning", "embedding_failed", {"message": "Embedding generation failed or returned empty."})

                                supabase_content_id_str = await upsert_content_to_supabase(
                                    supabase_client=supabase_client_for_history, # Reuse client
                                    url=fetched_url_actual,
                                    title=title,
                                    markdown_content=markdown_content, # Store full markdown
                                    embedding=embedding,
                                    pdf_path=final_data_for_db_and_pdf.get("processed_content_path"), # Use path from DB dict
                                    metadata_payload=fetched_data_dict.get("metadata"), # Pass along metadata
                                    raw_html_content=fetched_data_dict.get("content"), # Store raw HTML if available
                                    text_content=text_content_for_embedding, # Store plain text
                                    screenshot_base64=screenshot_base64_data # Store screenshot
                                )
                                if supabase_content_id_str:
                                    final_data_for_db_and_pdf["supabase_content_id"] = supabase_content_id_str
                                    yield format_sse_message(
                                        "status",
                                        "upload_complete",
                                        {
                                            "message": f"Content uploaded to Supabase. ID: {supabase_content_id_str}",
                                            "supabase_id": supabase_content_id_str,
                                        },
                                    )
                                else:
                                    logger.error(
                                        f"Supabase upload failed for {url}, no ID returned."
                                    )
                                    yield format_sse_message(
                                        "warning",
                                        "upload_failed",
                                        {"message": "Supabase upload failed."},
                                    )
                            except Exception as e_supabase:
                                logger.error(
                                    f"Error during Supabase embedding/upload for {url}: {e_supabase}",
                                    exc_info=True,
                                )
                                yield format_sse_message(
                                    "warning",
                                    "upload_error",
                                    {"message": f"Supabase upload error: {str(e_supabase)}"},
                                )
                    else: # upload_to_supabase is False
                        yield format_sse_message("status", "supabase_upload_disabled", {"message": "Supabase upload disabled by request."})
                    
                    final_data_for_db_and_pdf["status"] = "success" # If we got here through content processing
            
            elif fetched_data_dict and (fetched_data_dict.get("error") or fetched_data_dict.get("status_code", 200) >=400) : # Fetcher itself reported an error in the main data payload
                error_from_fetcher = fetched_data_dict.get("error", "Unknown error from fetcher payload.")
                status_code_from_fetcher = fetched_data_dict.get("status_code", "N/A")
                logger.error(
                    f"Fetcher returned an error in its main payload for {url}. Status: {status_code_from_fetcher}, Error: {error_from_fetcher}"
                )
                yield format_sse_message(
                    "error",
                    "fetcher_payload_error",
                    {
                        "message": f"Content fetcher reported an error: {error_from_fetcher}",
                        "status_code": status_code_from_fetcher,
                        "details": str(fetched_data_dict) # Log the whole dict for debugging
                    },
                )
                final_data_for_db_and_pdf["status"] = "failed"
                final_data_for_db_and_pdf["error_message"] = f"Fetcher Error (status {status_code_from_fetcher}): {error_from_fetcher}"
                final_data_for_db_and_pdf["output_type"] = "error_payload"


            else:  # fetched_data_dict is None or empty (should be caught by the check after crawl4ai loop for that engine)
                if engine.lower() != "crawl4ai": # Only log this if not crawl4ai, as crawl4ai has its own check
                    logger.error(
                        f"Failed to retrieve or process data using {engine} for {url}. No valid data dictionary was produced."
                    )
                    yield format_sse_message(
                        "error",
                        "no_valid_data_dictionary",
                        {
                            "message": f"Engine {engine} completed but no valid data was processed internally. Check engine's direct output."
                        },
                    )
                # Ensure history is updated if we fall through here without a specific error status written
                final_data_for_db_and_pdf["status"] = "failed" # Default to failed if no data
                final_data_for_db_and_pdf["error_message"] = final_data_for_db_and_pdf.get("error_message") or f"{engine.capitalize()} fetch completed but no data processed by backend."
                final_data_for_db_and_pdf["output_type"] = "processing_failure"


            # --- Final Update to Fetch History ---
            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                # Use the data accumulated in final_data_for_db_and_pdf
                logger.info(f"Attempting final history update for ID {fetch_history_id} with status: {final_data_for_db_and_pdf.get('status')}")
                sse_hist_update_msg, db_write_ok = await _update_fetch_history_record(
                    supabase_client_for_history,
                    fetch_history_id,
                    final_data_for_db_and_pdf, # Pass the dictionary
                    all_request_params,
                )
                if sse_hist_update_msg: # This contains either success or failure of DB write
                    yield sse_hist_update_msg 
                if db_write_ok and final_data_for_db_and_pdf.get("status") in ["success", "failed", "completed_no_content", "processing_failed"]:
                     terminal_status_written_to_db = True # Final status is now in DB


            yield format_sse_message(
                "status",
                "completed",
                {"message": f"Fetch process for {url} concluded with overall status: {final_data_for_db_and_pdf.get('status', 'unknown')}."},
            )

        except asyncio.CancelledError:
            logger.info(f"Fetch process for {url} was cancelled by client.")
            yield format_sse_message("status", "cancelled", {"message": "Process cancelled by client."})
            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                cancel_update_data = {"status": "cancelled", "error_message": "Process cancelled by client."}
                await _update_fetch_history_record(
                    supabase_client_for_history, fetch_history_id, cancel_update_data, all_request_params
                )
        except Exception as e_outer:
            logger.error(
                f"Unhandled error in fetch content event generator for {url}: {e_outer}",
                exc_info=True,
            )
            yield format_sse_message(
                "error", "unhandled_exception", {"message": f"Server error: {str(e_outer)}"}
            )
            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                unhandled_exc_update_data = {
                    "status": "failed",
                    "error_message": f"Unhandled exception: {str(e_outer)[:500]}", # Truncate
                    "output_type": "exception",
                }
                await _update_fetch_history_record(
                    supabase_client_for_history,
                    fetch_history_id,
                    unhandled_exc_update_data,
                    all_request_params,
                )
        finally:
            logger.info(f"SSE event stream for {url} finished.")
            # Final history update if a terminal status wasn't successfully written for some reason
            if fetch_history_id and supabase_client_for_history and not terminal_status_written_to_db:
                logger.warning(f"Fetch for {url} (ID: {fetch_history_id}) ended without a confirmed terminal status in DB. Attempting final 'unknown_outcome' update.")
                final_fallback_data = {
                    "status": "unknown_outcome",
                    "error_message": "Process ended; terminal status could not be confirmed in database.",
                }
                await _update_fetch_history_record(
                    supabase_client_for_history, fetch_history_id, final_fallback_data, all_request_params
                )


    return EventSourceResponse(event_generator())


# --- PDF Serving Endpoints ---


def secure_path_join(base: Path, requested_path: str) -> Optional[Path]:
    """Safely join a base directory and a requested path, preventing traversal."""
    try:
        # Normalize the requested path to prevent tricks like '..'
        normalized_req_path = os.path.normpath(requested_path)

        # Disallow absolute paths in the request
        if os.path.isabs(normalized_req_path):
            logger.warning(f"Attempted absolute path request: {normalized_req_path}")
            return None

        # Join base and requested path
        full_path = base.joinpath(normalized_req_path).resolve()

        # Crucial check: Ensure the resolved path is still within the base directory
        if base.resolve() in full_path.parents or base.resolve() == full_path:
            # Further check: ensure the part after the base matches the normalized request
            # This helps prevent issues if base itself contains '..' like structures (though resolve() should handle it)
            relative_part = full_path.relative_to(base.resolve())
            if str(relative_part) == normalized_req_path:
                return full_path
            else:
                logger.warning(
                    f"Path validation failed: Relative part mismatch. Base='{base}', Req='{requested_path}', Resolved='{full_path}', Relative='{relative_part}'"
                )
                return None
        else:
            logger.warning(
                f"Directory traversal attempt blocked: Base='{base}', Req='{requested_path}', Resolved='{full_path}'"
            )
            return None
    except Exception as e:
        logger.error(f"Error during secure path join: {e}", exc_info=True)
        return None


@app.get("/view-pdf", tags=["Files"])
async def view_pdf_endpoint(
    path: str = Query(
        ..., description="Relative path to the PDF file within the storage directory"
    ),
):
    """Serves a generated PDF file for inline viewing."""
    logger.info(f"Request to view PDF: {path}")
    secure_full_path = secure_path_join(PDF_STORAGE_BASE_DIR, path)

    if secure_full_path is None:
        raise HTTPException(status_code=400, detail="Invalid file path requested.")

    if not await asyncio.to_thread(os.path.isfile, secure_full_path):
        logger.error(f"PDF not found for viewing at resolved path: {secure_full_path}")
        raise HTTPException(status_code=404, detail="PDF file not found.")

    try:
        return FileResponse(
            path=str(secure_full_path),
            media_type="application/pdf",
            filename=secure_full_path.name,  # Provides a default filename if user saves
            content_disposition_type="inline",  # Display in browser
        )
    except Exception as e:
        logger.error(
            f"Error serving PDF {secure_full_path} for viewing: {e}", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Could not serve PDF file.")


@app.get("/download-pdf", tags=["Files"])
async def download_pdf_endpoint(
    path: str = Query(
        ..., description="Relative path to the PDF file within the storage directory"
    ),
):
    """Serves a generated PDF file for download as an attachment."""
    logger.info(f"Request to download PDF: {path}")
    secure_full_path = secure_path_join(PDF_STORAGE_BASE_DIR, path)

    if secure_full_path is None:
        raise HTTPException(status_code=400, detail="Invalid file path requested.")

    if not await asyncio.to_thread(os.path.isfile, secure_full_path):
        logger.error(f"PDF not found for download at resolved path: {secure_full_path}")
        raise HTTPException(status_code=404, detail="PDF file not found.")

    try:
        # Use a generic filename or derive from path if needed
        download_filename = f"downloaded_{secure_full_path.name}"
        return FileResponse(
            path=str(secure_full_path),
            media_type="application/pdf",
            filename=download_filename,  # Suggests this filename to the browser
            content_disposition_type="attachment",  # Force download dialog
        )
    except Exception as e:
        logger.error(
            f"Error serving PDF {secure_full_path} for download: {e}", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Could not serve PDF file.")


# --- Include Other Routers ---
# (Keep existing router includes - lines 1722-1741)
if PROJECT_MODULES_LOADED:
    if "content_upserter_router" in locals() and content_upserter_router:
        try:
            app.include_router(
                content_upserter_router,
                prefix="/api/content",
                tags=["Content Management"],
            )
        except Exception as e:
            logger.warning(f"Failed to include content_upserter_router: {e}")

    if "fetch_history_router" in locals() and fetch_history_router:  # Added this block
        try:
            app.include_router(
                fetch_history_router, prefix="/api", tags=["Fetch History"]
            )  # Using /api prefix for consistency
        except Exception as e:
            logger.warning(f"Failed to include fetch_history_router: {e}")

    if "llm_router" in locals() and llm_router:  # Added for new LLM endpoints
        try:
            app.include_router(llm_router, prefix="/api/v1", tags=["LLM Endpoints"])
            # Add new routers here, near other /api/v1 routes
            app.include_router(configurations_routes.router, prefix="/api/v1/configurations", tags=["App Configurations"])
            app.include_router(agent_registry_routes.router, prefix="/api/v1/agent-registry", tags=["Agent Registry"])
        except Exception as e:
            logger.warning(f"Failed to include llm_router or new system routers: {e}")

    if "metrics_router" in locals() and metrics_router:
        try:
            app.include_router(
                metrics_router, prefix="/monitoring", tags=["Monitoring"]
            )
        except Exception as e:
            logger.warning(f"Failed to include metrics_router: {e}")

    if (
        "monitoring_router" in locals()
        and metrics_router != monitoring_router
        and monitoring_router
    ):
        try:
            app.include_router(
                monitoring_router, prefix="/monitoring", tags=["Monitoring"]
            )
        except Exception as e:
            logger.warning(f"Failed to include monitoring_router: {e}")

    if "search_config_router" in locals() and search_config_router:
        try:
            app.include_router(
                search_config_router,
                prefix="/api/search-config",
                tags=["Search Configuration"],
            )
        except Exception as e:
            logger.warning(f"Failed to include search_config_router: {e}")

# --- Include Debug Endpoints ---
try:
    from .debug_endpoints import router as debug_router

    app.include_router(debug_router) # Typically included without a prefix for broader access
    logger.info("Debug endpoints included.")
except Exception as e:
    logger.warning(f"Failed to include debug endpoints: {e}")


# --- Vector Search Endpoint (MODIFIED to use SQL Function) ---
@app.post("/api/vector-search", response_model=VectorSearchResponse, tags=["Search"])
async def vector_search_endpoint(request: VectorSearchRequest):
    """Perform vector search using the advanced_hybrid_search SQL function."""
    logger.info(
        f"Vector search request: Query='{request.query[:50]}...', Max={request.max_results}, Threshold={request.threshold}"
    )

    supabase_client = None
    try:
        supabase_client = get_client()
        if not supabase_client:
            raise HTTPException(status_code=503, detail="Database client unavailable.")

        # Embedding service check is now implicitly handled by get_embedding_with_registry
        # if not openai_client: # This check is no longer directly relevant here
        #      raise HTTPException(status_code=503, detail="Embedding service unavailable.")

        # 1. Generate query embedding using the registry
        # Allow client to specify embedding model_id in request, or use a default
        embedding_model_id_from_request = getattr(
            request, "embedding_model_id", None
        )  # If added to VectorSearchRequest
        default_embedding_model_id = os.getenv(
            "DEFAULT_EMBEDDING_MODEL_ID", "openai/text-embedding-ada-002"
        )  # Example
        chosen_embedding_model_id = (
            embedding_model_id_from_request or default_embedding_model_id
        )

        query_embedding = await get_embedding_with_registry(
            request.query, model_id=chosen_embedding_model_id
        )

        if query_embedding is None:
            # get_embedding_with_registry logs errors internally.
            # Raise a structured error for the client.
            error_detail_payload = {
                "error_code": "EMBEDDING_GENERATION_FAILED",
                "message": f"Failed to generate query embedding for vector search using model '{chosen_embedding_model_id}'.",
                "llm_error_type": "EmbeddingError",
                "details": {
                    "query_preview": (request.query[:100] + "...")
                    if request.query and len(request.query) > 100
                    else request.query,
                    "model_used": chosen_embedding_model_id,
                    "suggestion": "Check server logs for detailed error information from the LLM registry and embedding service.",
                },
            }
            logger.error(
                f"Raising HTTPException for vector search due to embedding failure (via registry). Payload: {json.dumps(error_detail_payload)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail_payload,
            )

        # 2. Prepare parameters for the SQL function
        #    Match parameters defined in the SQL function (adjust dimension if needed)
        params = {
            "query_embedding": query_embedding,
            "match_count": request.max_results,
            "min_similarity": request.threshold,  # Assuming threshold maps to min_similarity
            "content_weight": request.content_weight,  # Pass weights from request
            "summary_weight": request.summary_weight,
            "video_filter": request.video_filter,  # Pass filter from request
        }
        logger.debug(
            f"Calling Supabase RPC advanced_hybrid_search with params: match_count={params['match_count']}, min_similarity={params['min_similarity']}, content_weight={params['content_weight']}, summary_weight={params['summary_weight']}, video_filter={params['video_filter']}"
        )

        # 3. Call the Supabase function via RPC
        response = await asyncio.to_thread(
            supabase_client.rpc("advanced_hybrid_search", params).execute
        )
        # response = supabase_client.rpc('advanced_hybrid_search', params).execute() # Original sync call

        # 4. Process results
        search_results = []
        if hasattr(response, "data") and response.data:
            search_results = response.data
            logger.info(
                f"Advanced hybrid search returned {len(search_results)} results."
            )
        elif hasattr(response, "error") and response.error:
            logger.error(
                f"Supabase RPC error during advanced_hybrid_search: {response.error}"
            )
            raise HTTPException(
                status_code=500, detail=f"Database search error: {response.error}"
            )
        else:
            logger.warning(
                f"Unexpected response structure from Supabase search RPC: {response}"
            )
            # Return empty results

        # 5. Prepare response metadata (optional AI response generation removed for now)
        metadata = {
            "query": request.query,
            "results_count": len(search_results),
            "search_function": "advanced_hybrid_search",
            "parameters_used": {
                "threshold": request.threshold,
                "max_results": request.max_results,
                "content_weight": request.content_weight,
                "summary_weight": request.summary_weight,
                "video_filter": request.video_filter,
            },
            "token_usage": token_counter.get_stats(),  # Include token stats
        }

        return VectorSearchResponse(
            results=search_results,  # The SQL function should return dicts directly
            ai_response=None,  # AI response generation can be added later if needed
            metadata=metadata,
        )

    except HTTPException as http_exc:
        raise http_exc  # Re-raise FastAPI errors
    except Exception as e:
        logger.error(
            f"Error during vector search for query '{request.query[:50]}...': {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")


# --- Comprehensive Search Endpoint (Using psearchworking) ---
# (Keep existing /api/search endpoint - lines 1806-1945)
@app.post("/api/search", response_model=ComprehensiveSearchResponse, tags=["Search"])
async def comprehensive_search_endpoint(
    request: ComprehensiveSearchRequest,  # Request body
    # Query parameters for overrides
    fg_similarity_threshold: Optional[float] = Query(
        None, alias="fine_grained_similarity_threshold"
    ),
    fg_content_weight: Optional[float] = Query(
        None, alias="fine_grained_content_weight"
    ),
    fg_result_percentage: Optional[float] = Query(
        None, alias="fine_grained_result_percentage"
    ),
    fg_max_results: Optional[int] = Query(None, alias="fine_grained_max_results"),
    ctx_similarity_threshold: Optional[float] = Query(
        None, alias="contextual_similarity_threshold"
    ),
    ctx_content_weight: Optional[float] = Query(
        None, alias="contextual_content_weight"
    ),
    ctx_result_percentage: Optional[float] = Query(
        None, alias="contextual_result_percentage"
    ),
    ctx_max_results: Optional[int] = Query(None, alias="contextual_max_results"),
    ov_similarity_threshold: Optional[float] = Query(
        None, alias="overview_similarity_threshold"
    ),
    ov_content_weight: Optional[float] = Query(None, alias="overview_content_weight"),
    ov_result_percentage: Optional[float] = Query(
        None, alias="overview_result_percentage"
    ),
    ov_max_results: Optional[int] = Query(None, alias="overview_max_results"),
    preset: Optional[str] = Query(None),
):
    """
    Perform comprehensive search using logic from psearchworking.
    Accepts optional query parameters to override search settings.
    """
    if not PROJECT_MODULES_LOADED or search_all is None or global_search_params is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search feature is unavailable due to import errors.",
        )

    logger.info(
        f"Search request: Query='{request.query[:50]}...', MaxRes={request.max_results}, Analysis={request.run_analysis}, Preset='{preset}'"
    )

    try:
        update_successful = global_search_params.update_from_frontend(
            preset=preset,
            fine_grained_similarity_threshold=fg_similarity_threshold,
            fine_grained_content_weight=fg_content_weight,
            fine_grained_result_percentage=fg_result_percentage,
            fine_grained_max_results=fg_max_results,
            contextual_similarity_threshold=ctx_similarity_threshold,
            contextual_content_weight=ctx_content_weight,
            contextual_result_percentage=ctx_result_percentage,
            contextual_max_results=ctx_max_results,
            overview_similarity_threshold=ov_similarity_threshold,
            overview_content_weight=ov_content_weight,
            overview_result_percentage=ov_result_percentage,
            overview_max_results=ov_max_results,
        )
        if not update_successful:
            logger.warning(
                "Search parameters updated from frontend might be invalid (e.g., sum > 1.0). Check psearchworking validation logic."
            )
        logger.debug(
            f"Effective search params used: {global_search_params.get_all_params()}"
        )
    except Exception as param_err:
        logger.error(f"Error updating search parameters: {param_err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid search parameters provided.",
        )

    start_time = time.time()
    try:
        results, openai_analysis, groq_analysis = await asyncio.to_thread(
            search_all,
            query=request.query,
            max_results=request.max_results,
            skip_prompts=True,
            run_analysis=request.run_analysis,
        )

        search_duration = time.time() - start_time
        logger.info(
            f"Search completed in {search_duration:.2f}s. Found {len(results)} results."
        )

        formatted_results = []
        if results:
            try:
                formatted_results = [res.to_dict() for res in results]
                logger.info(
                    f"Successfully converted {len(formatted_results)} SearchResult objects to dictionaries"
                )
            except (AttributeError, TypeError) as e:
                logger.warning(
                    f"Error converting SearchResult objects to dictionaries: {e}"
                )
                formatted_results = []
                for res in results:
                    try:
                        result_dict = {
                            "id": f"{getattr(res, 'content_id', 'N/A')}_{getattr(res, 'segment_id', '0')}_{getattr(res, 'start_time', '0')}",
                            "content_id": getattr(res, "content_id", None),
                            "content": getattr(res, "content", None),
                            "similarity": getattr(res, "similarity", 0.0),
                            "source": getattr(res, "source", "unknown"),
                            "title": getattr(res, "title", ""),
                            "start_time": getattr(res, "start_time", None),
                            "end_time": getattr(res, "end_time", None),
                            "url": getattr(res, "url", ""),
                            "watch_url": getattr(res, "watch_url", ""),
                            "video_id": getattr(res, "video_id", None),
                            "segment_id": getattr(res, "segment_id", None),
                            "summary": getattr(res, "summary", ""),
                            "metadata": getattr(res, "metadata", {}),
                            "search_method": getattr(res, "search_method", "unknown"),
                            "content_type": getattr(res, "content_type", "unknown"),
                        }
                        formatted_results.append(result_dict)
                    except Exception as item_err:
                        logger.error(f"Error formatting individual result: {item_err}")
                logger.info(
                    f"Manually converted {len(formatted_results)} SearchResult objects to dictionaries"
                )

        metadata = {
            "query": request.query,
            "total_results_found": len(results),
            "search_duration_seconds": round(search_duration, 2),
            "analysis_run": request.run_analysis,
            "effective_params": global_search_params.get_all_params(),
            "search_complete": True,
            "analysis_complete": request.run_analysis
            and (openai_analysis is not None or groq_analysis is not None),
        }
        try:
            try:
                from .psearchworking import token_counter as psearch_token_counter

                metadata["token_usage"] = psearch_token_counter.get_stats()
            except (ImportError, AttributeError):
                metadata["token_usage"] = token_counter.get_stats()
        except (NameError, AttributeError) as tk_err:
            logger.warning(f"Could not get token stats: {tk_err}")

        return ComprehensiveSearchResponse(
            query=request.query,
            results=formatted_results,
            openai_analysis=openai_analysis,
            groq_analysis=groq_analysis,
            metadata=metadata,
        )

    except Exception as e:
        search_duration = time.time() - start_time
        logger.error(
            f"Error during search execution ({search_duration:.2f}s): {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search execution failed: {e}",
        )


# --- Search SSE Endpoint (Using psearchworking) ---
# (Keep existing /api/search-sse endpoint - lines 1948-2131)
@app.get("/api/search-sse", tags=["Search"])
async def search_sse_endpoint(
    request: Request,
    query: str = Query(..., min_length=1),
    max_results: int = Query(30, ge=10, le=100),
    run_analysis: bool = Query(True),
    preset: Optional[str] = Query(None),
    fg_similarity_threshold: Optional[float] = Query(
        None, alias="fine_grained_similarity_threshold"
    ),
    fg_content_weight: Optional[float] = Query(
        None, alias="fine_grained_content_weight"
    ),
    fg_result_percentage: Optional[float] = Query(
        None, alias="fine_grained_result_percentage"
    ),
    fg_max_results: Optional[int] = Query(None, alias="fine_grained_max_results"),
    ctx_similarity_threshold: Optional[float] = Query(
        None, alias="contextual_similarity_threshold"
    ),
    ctx_content_weight: Optional[float] = Query(
        None, alias="contextual_content_weight"
    ),
    ctx_result_percentage: Optional[float] = Query(
        None, alias="contextual_result_percentage"
    ),
    ctx_max_results: Optional[int] = Query(None, alias="contextual_max_results"),
    ov_similarity_threshold: Optional[float] = Query(
        None, alias="overview_similarity_threshold"
    ),
    ov_content_weight: Optional[float] = Query(None, alias="overview_content_weight"),
    ov_result_percentage: Optional[float] = Query(
        None, alias="overview_result_percentage"
    ),
    ov_max_results: Optional[int] = Query(None, alias="overview_max_results"),
):
    """
    Server-Sent Events endpoint for real-time search updates.
    Provides incremental updates as the search progresses.
    """
    if not PROJECT_MODULES_LOADED or search_all is None or global_search_params is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search feature is unavailable due to import errors.",
        )

    client_host = request.client.host if request.client else "unknown"
    logger.info(
        f"SSE search request from {client_host}: Query='{query[:50]}...', MaxRes={max_results}, Analysis={run_analysis}, Preset='{preset}'"
    )

    async def event_generator():
        try:
            yield format_sse_message(
                "status", "Starting search operation", {"stage": "start"}
            )
            await asyncio.sleep(0.5)

            yield format_sse_message(
                "status", "Configuring search parameters", {"stage": "search"}
            )
            try:
                update_successful = global_search_params.update_from_frontend(
                    preset=preset,
                    fine_grained_similarity_threshold=fg_similarity_threshold,
                    fine_grained_content_weight=fg_content_weight,
                    fine_grained_result_percentage=fg_result_percentage,
                    fine_grained_max_results=fg_max_results,
                    contextual_similarity_threshold=ctx_similarity_threshold,
                    contextual_content_weight=ctx_content_weight,
                    contextual_result_percentage=ctx_result_percentage,
                    contextual_max_results=ctx_max_results,
                    overview_similarity_threshold=ov_similarity_threshold,
                    overview_content_weight=ov_content_weight,
                    overview_result_percentage=ov_result_percentage,
                    overview_max_results=ov_max_results,
                )
                if not update_successful:
                    logger.warning(
                        "Search parameters updated from frontend might be invalid"
                    )
                    yield format_sse_message(
                        "status",
                        "Warning: Some search parameters may be invalid",
                        {"stage": "search"},
                    )
                logger.debug(
                    f"Effective search params used: {global_search_params.get_all_params()}"
                )
            except Exception as param_err:
                logger.error(
                    f"Error updating search parameters: {param_err}", exc_info=True
                )
                yield format_sse_message(
                    "error", f"Invalid search parameters: {param_err}"
                )
                return

            start_time = time.time()
            yield format_sse_message(
                "status", "Executing search query", {"stage": "filter"}
            )
            try:
                results, openai_analysis, groq_analysis = await asyncio.to_thread(
                    search_all,
                    query=query,
                    max_results=max_results,
                    skip_prompts=True,
                    run_analysis=run_analysis,
                )
                search_duration = time.time() - start_time
                logger.info(
                    f"Search completed in {search_duration:.2f}s. Found {len(results)} results."
                )
                yield format_sse_message(
                    "status", "Combining search results", {"stage": "combine"}
                )
                await asyncio.sleep(0.5)

                formatted_results = []
                if results:
                    try:
                        formatted_results = [res.to_dict() for res in results]
                    except (AttributeError, TypeError) as e:
                        logger.warning(
                            f"Error converting SearchResult objects to dictionaries: {e}"
                        )
                        formatted_results = []
                        for res in results:
                            try:
                                result_dict = {
                                    "id": f"{getattr(res, 'content_id', 'N/A')}_{getattr(res, 'segment_id', '0')}_{getattr(res, 'start_time', '0')}",
                                    "content_id": getattr(res, "content_id", None),
                                    "content": getattr(res, "content", None),
                                    "similarity": getattr(res, "similarity", 0.0),
                                    "source": getattr(res, "source", "unknown"),
                                    "title": getattr(res, "title", ""),
                                    "start_time": getattr(res, "start_time", None),
                                    "end_time": getattr(res, "end_time", None),
                                    "url": getattr(res, "url", ""),
                                    "watch_url": getattr(res, "watch_url", ""),
                                    "video_id": getattr(res, "video_id", None),
                                    "segment_id": getattr(res, "segment_id", None),
                                    "summary": getattr(res, "summary", ""),
                                    "metadata": getattr(res, "metadata", {}),
                                    "search_method": getattr(
                                        res, "search_method", "unknown"
                                    ),
                                    "content_type": getattr(
                                        res, "content_type", "unknown"
                                    ),
                                }
                                formatted_results.append(result_dict)
                            except Exception as item_err:
                                logger.error(
                                    f"Error formatting individual result: {item_err}"
                                )

                metadata = {
                    "query": query,
                    "total_results_found": len(results),
                    "search_duration_seconds": round(search_duration, 2),
                    "analysis_run": run_analysis,
                    "effective_params": global_search_params.get_all_params(),
                    "search_complete": True,
                    "stage": "complete",
                }
                try:
                    try:
                        from .psearchworking import (
                            token_counter as psearch_token_counter,
                        )

                        metadata["token_usage"] = psearch_token_counter.get_stats()
                    except (ImportError, AttributeError):
                        metadata["token_usage"] = token_counter.get_stats()
                except (NameError, AttributeError) as tk_err:
                    logger.warning(f"Could not get token stats: {tk_err}")

                if run_analysis:
                    yield format_sse_message(
                        "status", "Analyzing search results", {"stage": "analyze"}
                    )
                    if openai_analysis:
                        yield format_sse_message(
                            "analysis", openai_analysis, {"provider": "openai"}
                        )
                    if groq_analysis:
                        yield format_sse_message(
                            "analysis", groq_analysis, {"provider": "groq"}
                        )
                    metadata["analysis_complete"] = bool(
                        openai_analysis or groq_analysis
                    )

                yield format_sse_message(
                    "results", formatted_results, {**metadata, "stage": "complete"}
                )
                yield format_sse_message(
                    "complete", "Search process completed", {"stage": "complete"}
                )

            except Exception as e:
                search_duration = time.time() - start_time
                error_msg = f"Search execution failed: {e}"
                logger.error(
                    f"Error during search execution ({search_duration:.2f}s): {e}",
                    exc_info=True,
                )
                yield format_sse_message("error", error_msg)

        except asyncio.CancelledError:
            logger.info(f"SSE connection closed by client {client_host}")
        except Exception as e:
            logger.error(
                f"Unexpected error in search SSE generator: {e}", exc_info=True
            )
            yield format_sse_message("error", f"Unexpected error: {e}")

    return EventSourceResponse(event_generator())


# --- Root and Health Check ---
# (Keep existing / and /health endpoints - lines 2133-2160)
@app.get("/", tags=["Utility"])
async def root():
    """Root endpoint providing basic service status."""
    logger.info("Root endpoint '/' called.")
    return {
        "service": "PMOVES Transcription API",
        "status": "running",
        "version": app.version,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    logger.debug("Health check '/health' called")
    db_status = "connected"
    try:
        client = get_client()
    except Exception as e:
        db_status = f"error: {e}"
        logger.warning(f"Health check: Supabase client unavailable: {e}")
    return {
        "status": "healthy",
        "dependencies": {"database": db_status},
        "timestamp": datetime.now().isoformat(),
    }


# --- Test Event Loop Policy Route ---
@app.get("/test-event-loop-policy", tags=["Utility", "Debug"])
async def test_event_loop_policy_route():
    # asyncio is imported at the top. logger is defined globally.
    policy_name = asyncio.get_event_loop_policy().__class__.__name__
    logger.info(f"Policy in /test-event-loop-policy route: {policy_name}")
    return {"active_policy": policy_name}


# --- ASGI Server Runner ---
# (Keep existing __main__ block - lines 2165-2194)
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Uvicorn server directly...")
    # Log policy before Uvicorn run
    logger.info(
        f"Policy before Uvicorn run in __main__: {asyncio.get_event_loop_policy().__class__.__name__}"
    )
    app_host = os.getenv("HOST", "127.0.0.1")
    try:
        app_port = int(os.getenv("PORT", "8000"))
    except ValueError:
        logger.warning(f"Invalid PORT env var '{os.getenv('PORT')}', using 8000.")
        app_port = 8000
    reload_flag = os.getenv("ENABLE_RELOAD", "false").lower() in ["true", "1", "yes"]
    if reload_flag:
        logger.warning("Auto-reload enabled. Recommended only for development.")
    uvicorn.run(
        f"{Path(__file__).stem}:app",
        host=app_host,
        port=app_port,
        reload=reload_flag,
        log_level="info",
    )


# --- App Config Endpoint ---
@app.get("/api/app-config", tags=["Utility"])
async def get_app_config():
    """Expose backend folder and subfolder config to the frontend."""
    return {"WORKSPACE_ROOT": WORKSPACE_ROOT, "SUBFOLDERS": SUBFOLDERS}


# --- Workspace Directory Listing Endpoint ---
@app.get("/api/list-workspace", tags=["Utility"])
async def list_workspace():
    """Recursively list all files and folders under the workspace root."""

    def list_dir(path, rel_path=""):
        items = []
        for entry in os.scandir(path):
            entry_rel_path = os.path.join(rel_path, entry.name)
            if entry.is_dir():
                items.append(
                    {
                        "name": entry.name,
                        "type": "folder",
                        "path": entry_rel_path.replace("\\", "/"),
                        "children": list_dir(entry.path, entry_rel_path),
                    }
                )
            else:
                stat = entry.stat()
                items.append(
                    {
                        "name": entry.name,
                        "type": "file",
                        "path": entry_rel_path.replace("\\", "/"),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    }
                )
        return sorted(items, key=lambda x: (x["type"] != "folder", x["name"].lower()))

    tree = list_dir(WORKSPACE_ROOT)
    return {"root": WORKSPACE_ROOT, "tree": tree}
