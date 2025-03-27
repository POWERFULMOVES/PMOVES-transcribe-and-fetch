# -*- coding: utf-8 -*-
"""
PMOVES Transcription API Backend

This FastAPI application provides endpoints for:
- Processing YouTube videos (downloading, transcribing).
- Downloading videos/audio using yt-dlp with progress updates.
- Fetching video metadata.
- Real-time status updates via Server-Sent Events (SSE).
- Content ingestion and vector search capabilities (requires related modules).
"""

# --- Standard Library Imports ---
import os
import re
import json
import shutil
import logging
import asyncio
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import time
import sys

# --- Third-Party Imports ---
from dotenv import load_dotenv
from fastapi import (
    FastAPI, HTTPException, BackgroundTasks, Body, Request,
    status, Query, Depends
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import (
    BaseModel, validator, ValidationError, Field, field_validator
)
import torch # Still imported from original, ensure necessary

# --- Optional Third-Party Imports (with fallbacks/warnings) ---
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    # logger.warning("Optional dependency 'openai' not found. AI analysis features may be limited.") # Logger not yet initialized

try:
    from groq import Groq
except ImportError:
    Groq = None
    # logger.warning("Optional dependency 'groq' not found. Groq features will be unavailable.") # Logger not yet initialized

try:
    from rich.console import Console
    # from rich.progress import SpinnerColumn # Not used directly in this final version
except ImportError:
    # logger.warning("Optional dependency 'rich' not found. Using basic console output.") # Logger not yet initialized
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    # class SpinnerColumn:
    #     def __init__(self, *args, **kwargs): pass

try:
    import yt_dlp
except ImportError:
    yt_dlp = None # Check for this before using yt-dlp features
    # logger.error("Required dependency 'yt-dlp' not found. Download and info features will fail.") # Logger not yet initialized

try:
    from tiktoken import get_encoding
except ImportError:
    get_encoding = None # Token counting will be estimated
    # logger.warning("Optional dependency 'tiktoken' not found. Token counting will be estimated.") # Logger not yet initialized

import aiofiles # Used for async file operations if needed

# --- Logging Configuration (Setup ASAP) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__) # Initialize main logger

# --- Check Critical Dependencies ---
if OpenAI is None:
    logger.warning("Optional dependency 'openai' not found. AI analysis features may be limited.")
if Groq is None:
    logger.warning("Optional dependency 'groq' not found. Groq features will be unavailable.")
if yt_dlp is None:
     logger.error("Required dependency 'yt-dlp' not found. Video download and info features will fail.")
     # Consider exiting if yt-dlp is essential
     # sys.exit("Error: yt-dlp library is required but not installed. `pip install yt-dlp`")
if get_encoding is None:
    logger.warning("Optional dependency 'tiktoken' not found. Token counting will be estimated.")

# --- Rich Console Initialization ---
console = Console()

# --- Environment Variable Loading ---
APP_DIR = Path(__file__).parent.absolute()
ENV_PATH = APP_DIR / '.env'

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    logger.info(f"Loaded environment variables from {ENV_PATH}")
else:
    logger.warning(f".env file not found at {ENV_PATH}. Relying on environment variables.")
    load_dotenv() # Attempt default load

# --- API Client Initialization ---
# OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = None
if OpenAI and openai_api_key:
    try:
        openai_client = OpenAI(api_key=openai_api_key)
        logger.info("OpenAI client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
elif OpenAI:
    logger.warning("OPENAI_API_KEY not set. OpenAI client not initialized.")

# Groq
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = None
if Groq and groq_api_key:
    try:
        groq_client = Groq(api_key=groq_api_key)
        logger.info("Groq client initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}", exc_info=True)
elif Groq:
    logger.warning("GROQ_API_KEY not set. Groq client not initialized.")


# --- Local/Project Imports ---
# NOTE: These relative imports assume this file is part of a Python package
# structure and is run using `python -m your_package.main_module`.
# If run directly (`python main_module.py`), change these to absolute imports
# (e.g., `from queue_manager import ...`) assuming files are in PYTHONPATH.
# --- Local/Project Imports ---
# (Imports remain the same)
try:
    from .queue_manager import QueueManager
    from .monitoring.logger import PerformanceMonitor, async_timer
    from .monitoring.metrics import MetricsCollector, TranscriptionMetrics, router as metrics_router
    from .error_handlers import TranscriptionErrorHandler, ErrorSeverity
    from .transcribe1 import process_video, VideoProcessRequest as TranscribeVideoRequest # Renamed Pydantic model
    from .utils import (
        convert_markdown_to_pdf, save_text_to_markdown,
        clean_filename, format_timestamp, sanitize_filename
    )
    from .fetch_content import (
        fetch_content_from_url, generate_unique_filename
    )
    from .config import DEFAULT_OUTPUT_FOLDER
    from .psearchworking_export import (
        search_all, analyze_search_results, get_client as get_supabase_client,
        SearchParameters, global_search_params, SearchResult,
        TokenCounter as PSearchTokenCounter, ModelSelector
    )
    # from .vector_search import VectorSearcher # Assuming not used now
    from .config.search_config import (
         get_preset, validate_search_params # etc.
     )
    from .routes.content_upserter import router as content_upserter_router
    from .monitoring.sse_monitor import sse_monitoring_middleware
    from .monitoring.routes import router as monitoring_router

    PROJECT_MODULES_LOADED = True
except ImportError as e:
     logger.error(f"Failed to import one or more project modules: {e}. Check installation and package structure.", exc_info=True)
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

     class PerformanceMonitor:
         """Dummy PerformanceMonitor."""
         def __init__(self, logger_instance): # Use a more descriptive name
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

     # --- Dummy Functions (already okay syntactically) ---
     def get_supabase_client(): logger.error("Dummy: Supabase client unavailable."); return None
     DEFAULT_OUTPUT_FOLDER = './output'
     async def process_video(*args, **kwargs): logger.error("Dummy: process_video unavailable.")
     async def search_all(*args, **kwargs): logger.error("Dummy: search_all unavailable."); return [], None, None
     def analyze_search_results(*args, **kwargs): logger.error("Dummy: analyze_search_results unavailable."); return "Analysis unavailable."

     # --- More Dummy Classes (ensure correct syntax) ---
     class SearchParameters:
         """Dummy SearchParameters."""
         def get_all_params(self) -> dict: return {}
         def get_params(self, tier: str) -> dict: return {}
         def load_current(self): pass
         def update_params(self, tier:str, **kwargs): pass

     global_search_params = SearchParameters()

     class SearchResult:
          """Dummy SearchResult."""
          def __init__(self, **kwargs): pass
          def to_dict(self): return {}

     class PSearchTokenCounter:
          """Dummy TokenCounter."""
          def get_stats(self) -> dict: return {'embedding_tokens':0, 'generation_tokens':{'input':0, 'output':0}, 'total_tokens':0}
          def count_embedding_tokens(self, text:str) -> int: return 0
          def count_generation_tokens(self, input_text:str, output_text:Optional[str]=None) -> dict: return {'input':0, 'output':0}

     class ModelSelector:
         """Dummy ModelSelector."""
         @staticmethod
         def generate_analysis(text: str, provider: str = 'openai') -> str: return "Dummy Analysis Unavailable."

     # --- Dummy Routers/Middleware ---
     content_upserter_router = None
     metrics_router = None
     monitoring_router = None
     sse_monitoring_middleware = None

# --- Initialize Core Components ---
# (This part should be AFTER the except block)
# ... rest of main.py ...except ImportError as e:
     logger.error(f"Failed to import one or more project modules: {e}. Check installation and package structure.", exc_info=True)
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

     class PerformanceMonitor:
         """Dummy PerformanceMonitor."""
         def __init__(self, logger_instance): # Use a more descriptive name
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

     # --- Dummy Functions (already okay syntactically) ---
     def get_supabase_client(): logger.error("Dummy: Supabase client unavailable."); return None
     DEFAULT_OUTPUT_FOLDER = './output'
     async def process_video(*args, **kwargs): logger.error("Dummy: process_video unavailable.")
     async def search_all(*args, **kwargs): logger.error("Dummy: search_all unavailable."); return [], None, None
     def analyze_search_results(*args, **kwargs): logger.error("Dummy: analyze_search_results unavailable."); return "Analysis unavailable."

     # --- More Dummy Classes (ensure correct syntax) ---
     class SearchParameters:
         """Dummy SearchParameters."""
         def get_all_params(self) -> dict: return {}
         def get_params(self, tier: str) -> dict: return {}
         # Add other methods if called elsewhere, e.g., load_current, update_params
         def load_current(self): pass
         def update_params(self, tier:str, **kwargs): pass

     global_search_params = SearchParameters() # Instantiate the dummy

     class SearchResult:
          """Dummy SearchResult."""
          # Add dummy attributes or methods if accessed by other code paths
          def __init__(self, **kwargs): pass
          def to_dict(self): return {}

     class PSearchTokenCounter:
          """Dummy TokenCounter."""
          def get_stats(self) -> dict: return {'embedding_tokens':0, 'generation_tokens':{'input':0, 'output':0}, 'total_tokens':0}
          # Add dummy count methods if needed
          def count_embedding_tokens(self, text:str) -> int: return 0
          def count_generation_tokens(self, input_text:str, output_text:Optional[str]=None) -> dict: return {'input':0, 'output':0}

     class ModelSelector:
         """Dummy ModelSelector."""
         # Add dummy static methods if called
         @staticmethod
         def generate_analysis(text: str, provider: str = 'openai') -> str: return "Dummy Analysis Unavailable."

     # --- Dummy Routers/Middleware ---
     # Assigning None is fine if they are just checked for existence before inclusion
     content_upserter_router = None
     metrics_router = None
     monitoring_router = None
     sse_monitoring_middleware = None # Cannot easily create a dummy middleware function

# --- Initialize Core Components ---
# (This part remains the same)
# ... rest of main.py ...

# --- Initialize Core Components ---
# (This part remains the same, it will use the real or dummy QueueManager)
# ... rest of main.py ...
     # Add other dummies as necessary based on errors

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
     # Use dummy instances if imports failed but we want to continue partially
     logger.warning("Using dummy components due to import errors.")
     performance_monitor = PerformanceMonitor(logger)
     metrics_collector = MetricsCollector()
     transcription_metrics = TranscriptionMetrics()
     queue_manager = QueueManager() # Dummy instance

# Download-specific queue
download_status_queue = asyncio.Queue()


# --- TokenCounter Class ---
class TokenCounter:
    """Tracks token usage for embeddings and generations."""
    def __init__(self):
        self.embedding_tokens = 0
        self.generation_tokens = {'input': 0, 'output': 0}
        self.encoders = None
        if get_encoding:
            try:
                self.encoders = {
                    'cl100k_base': get_encoding('cl100k_base'),
                    'gpt-4': get_encoding('cl100k_base'),
                }
                logger.info("TokenCounter initialized with tiktoken encoders.")
            except Exception as e:
                logger.warning(f"Could not initialize tiktoken encoders: {e}. Token counting will be estimated.")
        else:
             logger.warning("TokenCounter initialized without tiktoken. Token counting will be estimated.")

    def _estimate_tokens(self, text: str) -> int:
        """Estimate tokens based on character count."""
        return len(text) // 4

    def count_embedding_tokens(self, text: str) -> int:
        """Count or estimate tokens for embedding."""
        if not self.encoders or 'cl100k_base' not in self.encoders:
            tokens = self._estimate_tokens(text)
            self.embedding_tokens += tokens
            return tokens
        try:
            tokens = len(self.encoders['cl100k_base'].encode(text))
            self.embedding_tokens += tokens
            return tokens
        except Exception as e:
            logger.warning(f"Could not count embedding tokens using tiktoken: {e}. Estimating.")
            tokens = self._estimate_tokens(text)
            self.embedding_tokens += tokens
            return tokens

    def count_generation_tokens(self, input_text: str, output_text: Optional[str] = None) -> dict:
        """Count or estimate tokens for generation."""
        result = {'input': 0, 'output': 0}
        encoder = self.encoders.get('gpt-4') if self.encoders else None

        try:
            if encoder:
                result['input'] = len(encoder.encode(input_text))
                if output_text:
                    result['output'] = len(encoder.encode(output_text))
            else:
                result['input'] = self._estimate_tokens(input_text)
                if output_text:
                    result['output'] = self._estimate_tokens(output_text)
        except Exception as e:
            logger.warning(f"Could not count generation tokens using tiktoken: {e}. Estimating.")
            result['input'] = self._estimate_tokens(input_text)
            if output_text:
                result['output'] = self._estimate_tokens(output_text)

        self.generation_tokens['input'] += result['input']
        self.generation_tokens['output'] += result['output']
        return result

    def get_stats(self) -> dict:
        """Get current token usage statistics."""
        total = self.embedding_tokens + sum(self.generation_tokens.values())
        return {
            'embedding_tokens': self.embedding_tokens,
            'generation_tokens': self.generation_tokens,
            'total_tokens': total
        }

# Initialize token counter
token_counter = TokenCounter()


# --- Supabase Client Function ---
def get_client():
    """Get a Supabase client instance using the imported function."""
    if not PROJECT_MODULES_LOADED or get_supabase_client is None:
         logger.error("Cannot get Supabase client: psearchworking module or get_client function not loaded.")
         raise RuntimeError("Supabase client function is unavailable.")
    try:
        client = get_supabase_client()
        if client is None:
            logger.error("get_supabase_client() returned None.")
            raise RuntimeError("Failed to obtain Supabase client instance.")
        # logger.debug("Supabase client obtained successfully.")
        return client
    except Exception as e:
        logger.error(f"Error obtaining Supabase client via get_supabase_client(): {e}", exc_info=True)
        raise RuntimeError(f"Failed to obtain Supabase client: {e}")


# --- Pydantic Models ---
class ComprehensiveSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    max_results: int = Field(30, ge=10, le=100, description="Maximum TOTAL results desired across methods")
    run_analysis: bool = Field(True, description="Whether to run AI analysis on results")
    # Add other fields if your request body needs them


# ---- ADD THIS CLASS DEFINITION ----
class ComprehensiveSearchResponse(BaseModel):
    """Response model for the comprehensive search endpoint."""
    query: str
    results: List[Dict[str, Any]] # List of dictionaries matching SearchResult.to_dict()
    openai_analysis: Optional[str] = None
    groq_analysis: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Search metadata, like timing, token counts, effective params")

    class Config:
        from_attributes = True # For Pydantic v2
class VideoRequest(BaseModel):
    youtube_video_url: str
    obsidian_dir: str # Client must provide path to existing Obsidian vault/folder
    output_folder: str # Client provides desired base output path
    transcription_model: str = "faster-whisper"
    use_groq: Optional[bool] = None # Allow explicit setting, but validator overrides

    @field_validator('youtube_video_url')
    def validate_youtube_url(cls, v):
        youtube_regex = r'^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$'
        if not re.match(youtube_regex, v, re.IGNORECASE):
            raise ValueError('Invalid YouTube URL format')
        return v

    @field_validator('output_folder')
    def output_folder_must_be_valid(cls, v):
        if not v:
            v = DEFAULT_OUTPUT_FOLDER
        try:
             path = Path(v).resolve() # Resolve to absolute path
             # Check if parent exists - doesn't guarantee write permissions
             if not path.parent.exists():
                  raise ValueError(f"Parent directory does not exist: {path.parent}")
             # Further checks could include writability, but might be excessive here
             return str(path)
        except Exception as e:
             raise ValueError(f"Invalid output folder path '{v}': {e}")


    @field_validator('obsidian_dir')
    def obsidian_dir_must_exist(cls, v):
        if not v:
            raise ValueError('Obsidian directory path must be provided')
        try:
             path = Path(v).resolve()
             if not path.is_dir():
                  raise ValueError('Path is not an existing directory')
             # Check for write permissions? Might be overkill/platform dependent.
             # if not os.access(path, os.W_OK):
             #      raise ValueError('Directory is not writable')
             return str(path)
        except Exception as e:
             raise ValueError(f"Invalid Obsidian directory path '{v}': {e}")

    @field_validator('transcription_model')
    def validate_transcription_model(cls, v):
        valid_models = ["faster-whisper", "groq"] # Add specific models if needed e.g. "groq/whisper-large-v3"
        if v.lower() not in valid_models and not v.lower().startswith("groq/"):
            raise ValueError(f"Invalid transcription model. Use 'faster-whisper', 'groq', or specific 'groq/model-name'.")
        return v.lower()

    # Use model_validator (Pydantic v2) to handle dependencies between fields
    from pydantic import model_validator

    @model_validator(mode='after')
    def check_and_set_use_groq(self) -> 'VideoRequest':
        model_name = self.transcription_model
        is_groq_model = model_name == 'groq' or model_name.startswith('groq/')

        if self.use_groq is not None and self.use_groq != is_groq_model:
             logger.warning(f"Provided 'use_groq' ({self.use_groq}) contradicts model '{model_name}'. Overriding based on model.")

        self.use_groq = is_groq_model # Set use_groq based on the model selected

        # Check if Groq client is available if a Groq model is selected
        if self.use_groq and groq_client is None:
             raise ValueError("Groq transcription model selected, but Groq client is not available/configured.")

        return self


class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")

    @field_validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Search query must not be empty')
        return v.strip()


class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(default_factory=list)
    ai_response: Optional[str] = Field(None)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True # Pydantic v2


class DownloadRequest(BaseModel):
    url: str
    options: Dict[str, Any] = Field(default_factory=dict, description="yt-dlp options")


class VideoInfoRequest(BaseModel):
    url: str


# --- Initialize FastAPI app ---
app = FastAPI(
    title="PMOVES Transcription API",
    description="API for YouTube video processing, download, and search.",
    version="1.1.0", # Incremented version
    # Add OpenAPI tags metadata if desired
    openapi_tags=[
        {"name": "Processing", "description": "Video transcription and processing."},
        {"name": "Download", "description": "Video/Audio download operations."},
        {"name": "Search", "description": "Content search functionalities."},
        {"name": "Status", "description": "Real-time status updates via SSE."},
        {"name": "Utility", "description": "Helper endpoints."},
        {"name": "Health", "description": "Service health checks."},
    ]
)

# --- Configure CORS ---
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(',')
logger.info(f"Configuring CORS for origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "X-Content-Type-Options"],
)

# --- Add Custom Middlewares ---
# SSE Monitoring Middleware (if available)
if PROJECT_MODULES_LOADED and 'sse_monitoring_middleware' in locals():
    try:
        app.middleware("http")(sse_monitoring_middleware)
        logger.info("SSE monitoring middleware enabled.")
    except Exception as e:
        logger.warning(f"Failed to enable SSE monitoring middleware: {e}")

# Error Handling Middleware (should be early)
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_exc:
        # Log FastAPI's own HTTPExceptions if desired
        # logger.warning(f"HTTPException: {http_exc.status_code} - {http_exc.detail}")
        raise http_exc # Re-raise for FastAPI to handle
    except Exception as exc:
        logger.error(f"Unhandled exception during request to {request.url.path}", exc_info=exc)
        # Use custom error handler if available
        error_details = {"error_code": "UNEXPECTED_SERVER_ERROR", "message": "An internal server error occurred."}
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if PROJECT_MODULES_LOADED and 'TranscriptionErrorHandler' in locals():
             try:
                 error_details = TranscriptionErrorHandler.handle_error(
                     "UNEXPECTED_SERVER_ERROR", exc, path=str(request.url.path)
                 )
                 # You might adjust status_code based on error_details here if needed
             except Exception as handler_err:
                  logger.error(f"Error handler itself failed: {handler_err}")

        return JSONResponse(status_code=status_code, content=error_details)

# Request Logging Middleware (should be after error handling, before routes)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    client_host = request.client.host if request.client else "unknown"

    logger.info(f"--> {method} {path} from {client_host}")

    response = await call_next(request) # Process request

    process_time = time.time() - start_time
    status_code = response.status_code
    logger.info(f"<-- {method} {path} - Status={status_code} ({process_time:.3f}s)")

    return response


# --- App Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup initiated...")
    try:
        await queue_manager.start()
        if PROJECT_MODULES_LOADED:
             asyncio.create_task(metrics_collector.collect_system_metrics())
             logger.info("System metrics collection scheduled.")
        logger.info("Queue manager started.")
        # Check yt-dlp dependency again
        if yt_dlp is None:
             logger.error("yt-dlp is missing, download features will be unavailable.")
    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)
        # Decide if fatal - perhaps exit if queue manager fails?
        # sys.exit("Startup failed.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown initiated...")
    try:
        await queue_manager.stop()
        logger.info("Queue manager stopped.")
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}", exc_info=True)


# --- SSE Message Formatter ---
def format_sse_message(message_type: str, content: Any, metadata: Optional[dict] = None) -> str:
    """Formats a message dictionary into an SSE string."""
    message = {
        "type": message_type,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    if metadata:
        message["metadata"] = metadata
    try:
        json_str = json.dumps(message)
        return f"data: {json_str}\n\n"
    except TypeError as e:
         logger.error(f"Failed to serialize SSE message content of type {message_type}: {e}. Content snippet: {str(content)[:100]}")
         # Fallback: send error message or simplified content
         error_content = {"error": "Failed to serialize message content", "original_type": message_type}
         return f"data: {json.dumps({'type': 'error', 'content': error_content, 'timestamp': datetime.now().isoformat()})}\n\n"


# --- Combined SSE Updates Endpoint ---
@app.get("/combined-updates", tags=["Status"])
async def get_combined_updates(request: Request):
    """SSE endpoint for combined status and transcription updates."""
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "N/A")
    logger.info(f"SSE connection requested from {client_host} (Origin: {origin}) for /combined-updates.")

    async def event_generator():
        status_q = queue_manager.status_queue
        transcription_q = queue_manager.transcription_queue
        last_activity_time = time.time()
        heartbeat_interval = 15

        try:
            yield format_sse_message("status", "SSE connection established")
            last_activity_time = time.time()

            while True:
                update_sent = False
                now = time.time()

                # Check queues (non-blocking)
                try:
                    status_update = status_q.get_nowait()
                    logger.debug(f"SSE (Combined): Sending status: {str(status_update)[:100]}...")
                    try:
                        update_data = json.loads(status_update) # Assumes JSON string in queue
                        if 'type' not in update_data: update_data['type'] = 'status'
                        yield f"data: {json.dumps(update_data)}\n\n"
                    except (json.JSONDecodeError, TypeError):
                        yield format_sse_message('status', status_update) # Send as plain if not JSON
                    status_q.task_done()
                    update_sent = True
                except asyncio.QueueEmpty: pass

                try:
                    transcription_update = transcription_q.get_nowait()
                    logger.debug(f"SSE (Combined): Sending transcription: {str(transcription_update)[:100]}...")
                    try:
                        update_data = json.loads(transcription_update) # Assumes JSON string
                        if 'type' not in update_data: update_data['type'] = 'transcription_segment'
                        yield f"data: {json.dumps(update_data)}\n\n"
                    except (json.JSONDecodeError, TypeError):
                        yield format_sse_message('transcription_segment', transcription_update)
                    transcription_q.task_done()
                    update_sent = True
                except asyncio.QueueEmpty: pass

                # Manage heartbeat
                if update_sent:
                    last_activity_time = now
                elif now - last_activity_time > heartbeat_interval:
                    logger.debug("SSE (Combined): Sending heartbeat.")
                    yield format_sse_message('heartbeat', 'ping')
                    last_activity_time = now # Reset timer

                await asyncio.sleep(0.1) # Prevent high CPU usage if queues empty

        except asyncio.CancelledError:
            logger.info(f"SSE connection closed by client {client_host} for /combined-updates.")
        except Exception as e:
            error_message = f"Error in /combined-updates SSE generator: {e}"
            logger.error(error_message, exc_info=True)
            try: yield format_sse_message('error', error_message)
            except Exception as send_err: logger.error(f"Failed to send error to SSE client: {send_err}")
        finally:
            logger.info(f"SSE event generator finished for {client_host} (/combined-updates).")

    response = EventSourceResponse(event_generator(), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    return response

# --- OPTIONS handler for Combined SSE ---
@app.options("/combined-updates", tags=["Status"])
async def options_combined_updates(request: Request):
    """Handle OPTIONS preflight requests for /combined-updates."""
    return _handle_options_request(request, allowed_origins)


# --- Download Status SSE Endpoint ---
@app.get("/api/download-status", tags=["Status", "Download"])
async def get_download_status(request: Request):
    """SSE endpoint specifically for download status updates."""
    client_host = request.client.host if request.client else "unknown"
    origin = request.headers.get("origin", "N/A")
    logger.info(f"Download status SSE connection requested from {client_host} (Origin: {origin}).")

    async def event_generator():
        q = download_status_queue
        last_activity_time = time.time()
        heartbeat_interval = 20 # Longer interval might be ok

        try:
            yield format_sse_message("status", "Connected to download status stream")
            last_activity_time = time.time()

            while True:
                try:
                    # Wait for an item with timeout for heartbeat
                    status_update_str = await asyncio.wait_for(q.get(), timeout=heartbeat_interval)
                    logger.debug(f"SSE (Download): Sending update: {status_update_str[:100]}...")
                    try:
                        # Assume already valid JSON from download task/hooks
                        update_data = json.loads(status_update_str)
                        yield f"data: {status_update_str}\n\n" # Send raw JSON string
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"Download SSE received non-JSON: {status_update_str[:100]}... Error: {e}")
                        yield format_sse_message('status', status_update_str) # Send as plain
                    q.task_done()
                    last_activity_time = time.time() # Reset timer on activity

                except asyncio.TimeoutError:
                    # No message received, send heartbeat
                    logger.debug("SSE (Download): Sending heartbeat.")
                    yield format_sse_message('heartbeat', 'ping')
                    last_activity_time = time.time() # Reset timer after sending
                    continue # Go back to waiting

                except asyncio.QueueEmpty:
                     # Should not happen with wait_for, but handle defensively
                     await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info(f"Download SSE connection closed by client {client_host}.")
        except Exception as e:
            error_message = f"Error in download status SSE generator: {e}"
            logger.error(error_message, exc_info=True)
            try: yield format_sse_message('error', error_message)
            except Exception as send_err: logger.error(f"Failed to send error to download SSE client: {send_err}")
        finally:
            logger.info(f"Download SSE event generator finished for {client_host}.")

    response = EventSourceResponse(event_generator(), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    return response

# --- OPTIONS handler for Download Status SSE ---
@app.options("/api/download-status", tags=["Status", "Download"])
async def options_download_status(request: Request):
    """Handle OPTIONS preflight requests for /api/download-status."""
    return _handle_options_request(request, allowed_origins)

# --- Helper for OPTIONS requests ---
def _handle_options_request(request: Request, allowed_origins_list: List[str]):
    origin = request.headers.get("origin")
    method = request.headers.get("access-control-request-method")
    logger.info(f"OPTIONS request for {request.url.path} from origin: {origin}, method: {method}")

    if origin in allowed_origins_list:
        response = JSONResponse(content={"detail": "OK"}, status_code=200)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS" # Adjust as needed per endpoint
        response.headers["Access-Control-Allow-Headers"] = "*" # Or be specific: "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Max-Age"] = "86400" # Cache preflight for 1 day
        logger.debug(f"OPTIONS response headers: {response.headers}")
        return response
    else:
        logger.warning(f"OPTIONS request from disallowed origin: {origin}")
        return JSONResponse(content={"detail": "Origin not allowed"}, status_code=400)


# --- Process Video Endpoint ---
@app.post("/process-video/", tags=["Processing"])
async def process_video_endpoint(request: VideoRequest, background_tasks: BackgroundTasks):
    """Initiate background processing (download, transcribe) for a YouTube video."""
    if not PROJECT_MODULES_LOADED or process_video is None:
         raise HTTPException(status_code=501, detail="Video processing feature is unavailable due to missing modules.")

    try:
        # Validation done by Pydantic. Log validated request details.
        logger.info(f"Processing video request for URL: {request.youtube_video_url}")
        console.print(f"[cyan]Obsidian Dir:[/cyan] {request.obsidian_dir}")
        console.print(f"[cyan]Output Folder:[/cyan] {request.output_folder}")
        console.print(f"[cyan]Model:[/cyan] {request.transcription_model}, [cyan]Use Groq:[/cyan] {request.use_groq}")

        transcription_metrics.record_request(True)

        # Ensure output folder exists
        output_path = Path(request.output_folder)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured output folder exists: {output_path}")
        except OSError as e:
             logger.error(f"Failed to create output folder {output_path}: {e}", exc_info=True)
             raise HTTPException(status_code=500, detail=f"Could not create output directory: {e}")

        # Prepare model config
        model_config = {
            "model": request.transcription_model,
            "use_groq": request.use_groq
            # Pass clients if needed, e.g., if process_video uses groq_client directly
            # "groq_client": groq_client if request.use_groq else None
        }

        # Add processing task to background
        background_tasks.add_task(
            process_video, # The async function from transcribe1.py
            youtube_url=request.youtube_video_url,
            obsidian_dir=request.obsidian_dir,
            status_queue=queue_manager.status_queue,
            transcription_queue=queue_manager.transcription_queue,
            output_folder=request.output_folder,
            model_config=model_config,
            # Pass other dependencies if required by process_video
            logger=logger # Pass logger instance
        )

        logger.info(f"Background task added for processing: {request.youtube_video_url}")

        return {
            "status": "started",
            "message": "Video processing initiated in the background.",
            "details": {
                 "url": request.youtube_video_url,
                 "output_folder": request.output_folder,
                 "obsidian_dir": request.obsidian_dir
            },
            "timestamp": datetime.now().isoformat()
        }

    except ValidationError as e:
        transcription_metrics.record_request(False)
        logger.warning(f"Validation error processing video request: {e.errors()}", exc_info=False) # Log concise errors
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    except HTTPException as e:
         transcription_metrics.record_request(False)
         raise e # Re-raise exceptions from folder creation or other setup
    except Exception as e:
        transcription_metrics.record_request(False)
        logger.error(f"Unexpected error initiating video processing for {request.youtube_video_url}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start video processing task.")


# --- Video Download Feature ---

async def download_video_task(url: str, options: dict, status_queue: asyncio.Queue):
    """Background task using yt-dlp (run in thread) with progress reporting."""
    if yt_dlp is None:
        logger.error("yt-dlp library is not installed. Cannot download video.")
        await status_queue.put(format_sse_message('error','Download feature unavailable: yt-dlp library not installed.'))
        return

    download_dir = options.get('download_dir', os.path.join(os.getcwd(), 'downloads'))
    logger.info(f"Download task started for URL: {url}, saving to: {download_dir}")

    try:
        os.makedirs(download_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create download directory {download_dir}: {e}", exc_info=True)
        await status_queue.put(format_sse_message('error', f'Failed to create download directory: {e}'))
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Filename template using yt-dlp placeholders
    filename_template = os.path.join(download_dir, f'%(title)s_{timestamp}.%(ext)s')

    # --- Configure yt-dlp options ---
    # Start with defaults, merge with user options carefully
    ydl_opts = {
        'outtmpl': filename_template,
        'progress_hooks': [lambda d: report_download_progress(d, status_queue)],
        'postprocessor_hooks': [lambda d: report_postprocess_progress(d, status_queue)],
        'quiet': True,
        'no_warnings': True,
        'noprogress': True, # Rely on hooks
        'keepvideo': options.get('keepVideo', True),
        'overwrites': False,
        'ffmpeg_location': options.get('ffmpegPath'), # Allow user to specify path
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Default format
        # Playlist defaults
        'noplaylist': True, # Default to single video unless playlist options set
        'playlist_items': None,
    }

    # --- Apply User Options ---
    # Format
    video_format = options.get('format')
    if video_format == 'best': pass # Already default
    elif video_format in ['1080p', '720p', '480p', '360p']:
        res = video_format.replace('p', '')
        ydl_opts['format'] = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best[height<={res}]'
    elif video_format == 'audio_best':
         ydl_opts['format'] = 'bestaudio/best'
         options['extractAudio'] = True # Force extraction if only audio format
         options.setdefault('audioFormat', 'mp3')

    # Audio Extraction
    if options.get('extractAudio'):
        audio_format = options.get('audioFormat', 'mp3')
        audio_quality = options.get('audioQuality', '192')
        ydl_opts.setdefault('postprocessors', []).append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': audio_quality,
        })
        # If only audio wanted, maybe simplify format unless keepvideo is true
        if not ydl_opts['keepvideo'] and video_format != 'audio_best':
             ydl_opts['format'] = 'bestaudio/best'

    # Thumbnail (usually for video/m4a)
    if options.get('embedThumbnail') and video_format != 'audio_best':
        ydl_opts['writethumbnail'] = True
        ydl_opts.setdefault('postprocessors', []).append({'key': 'EmbedThumbnail'})

    # Metadata
    if options.get('embedMetadata', True): # Default True
        ydl_opts.setdefault('postprocessors', []).append({'key': 'FFmpegMetadata', 'add_metadata': True})

    # Subtitles
    if options.get('subtitles'):
        sub_lang = options.get('subtitleLanguage', 'en')
        sub_auto = options.get('autoSubtitles', False)
        sub_format = options.get('subtitleFormat', 'srt')
        ydl_opts.update({
            'writesubtitles': True,
            'writeautomaticsub': sub_auto,
            'subtitleslangs': [sub_lang] if sub_lang != 'all' else ['all'],
            'subtitlesformat': sub_format,
        })
        if options.get('embedSubtitles') and video_format != 'audio_best':
             ydl_opts.setdefault('postprocessors', []).append({'key': 'FFmpegEmbedSubtitle'})

    # Playlist Handling (only if 'downloadPlaylist' is explicitly true in options)
    # Check if URL likely contains playlist identifiers
    is_playlist_url = 'list=' in url or '/playlist?' in url
    if is_playlist_url and options.get('downloadPlaylist'):
        playlist_items = None
        items_str = options.get('playlistItems') # e.g., "1,3,5-7"
        start = options.get('playlistStart')
        end = options.get('playlistEnd')

        if items_str: playlist_items = items_str
        elif start or end:
             playlist_items = f"{start or ''}-{end or ''}"

        ydl_opts['noplaylist'] = False # Process as playlist
        ydl_opts['playlist_items'] = playlist_items
        logger.info(f"Playlist download enabled. Items: '{playlist_items or 'all'}'")
    elif is_playlist_url:
        logger.info("Playlist URL detected, but only downloading single video as 'downloadPlaylist' option is false/missing.")
        ydl_opts['noplaylist'] = True # Treat as single video


    # --- Execute Download ---
    try:
        await status_queue.put(format_sse_message('status', f'Starting download: {url}', {'download_dir': download_dir}))

        # Run yt-dlp download in a separate thread
        logger.info("Running yt-dlp download process in thread...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
             await asyncio.to_thread(ydl.download, [url])
        logger.info(f"yt-dlp download thread finished for {url}.")

        await status_queue.put(format_sse_message('complete', f'Download finished for: {url}'))

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp download error for {url}: {e}", exc_info=False) # Log concise error
        await status_queue.put(format_sse_message('error', f'Download failed: {e}'))
    except Exception as e:
        logger.error(f"Unexpected error during download task for {url}: {e}", exc_info=True)
        await status_queue.put(format_sse_message('error', f'Unexpected download error: {e}'))


# --- Progress Hooks (run in yt-dlp's thread) ---
def report_download_progress(d, status_queue: asyncio.Queue):
    """Hook for yt-dlp download progress, puts message to asyncio queue."""
    # Use run_coroutine_threadsafe for putting to queue from another thread
    loop = None
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError: # No loop running in this thread (shouldn't happen with to_thread?)
        logger.error("No running asyncio loop found in download progress hook!")
        return

    if d['status'] == 'downloading':
        try:
            progress = d.get('fraction', 0) * 100
            speed = d.get('speed_str', d.get('speed', 'N/A')) # Compatibility
            eta = d.get('eta_str', d.get('eta', 'N/A'))       # Compatibility
            filename = d.get('filename', d.get('info_dict',{}).get('filename', '...'))
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            size_str = "N/A"
            if total_bytes:
                if total_bytes < 1024*1024: size_str = f"{total_bytes/1024:.1f} KiB"
                elif total_bytes < 1024*1024*1024: size_str = f"{total_bytes/(1024*1024):.1f} MiB"
                else: size_str = f"{total_bytes/(1024*1024*1024):.2f} GiB"

            content = {
                'progress': round(progress, 1), 'speed': speed, 'eta': eta,
                'filename': os.path.basename(filename), 'total_size': size_str,
                'status': 'Downloading'
            }
            message = format_sse_message('progress', content)
            asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)
        except Exception as e:
             # print(f"Error reporting progress: {e}") # Simple print to avoid logging noise from thread
             pass

    elif d['status'] == 'finished':
        filename = d.get('filename', d.get('info_dict',{}).get('filename', 'file'))
        message = format_sse_message('status', f'Downloaded {os.path.basename(filename)}. Post-processing...')
        asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)

    elif d['status'] == 'error':
         err_msg = d.get("error", "Unknown download error")
         filename = d.get('filename', d.get('info_dict',{}).get('filename', 'N/A'))
         message = format_sse_message('error', f'Error downloading {os.path.basename(filename)}: {err_msg}')
         asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)


def report_postprocess_progress(d, status_queue: asyncio.Queue):
    """Hook for yt-dlp post-processing progress."""
    loop = None
    try: loop = asyncio.get_running_loop()
    except RuntimeError: logger.error("No running loop in postprocess hook!"); return

    status = d.get('status')
    pp_name = d.get('postprocessor')
    info = d.get('info_dict', {})
    filename = os.path.basename(info.get('filepath', info.get('filename', 'file')))

    if status == 'started' or status == 'processing':
        message = format_sse_message('status', f'Post-processing ({pp_name}): Starting on {filename}...')
    elif status == 'finished':
        message = format_sse_message('status', f'Post-processing ({pp_name}): Finished for {filename}.')
    elif status == 'error':
        message = format_sse_message('error', f'Post-processing ({pp_name}): Failed for {filename}. Check logs.')
    else:
        return # Ignore other statuses

    asyncio.run_coroutine_threadsafe(status_queue.put(message), loop)


# --- Download Endpoint ---
@app.post("/api/download", tags=["Download"])
async def download_video_endpoint(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Start a video/audio download task in the background."""
    if yt_dlp is None:
         raise HTTPException(status_code=501, detail="Download feature unavailable: yt-dlp library not installed.")
    try:
        logger.info(f"Download request received for URL: {request.url}")
        console.print(f"[yellow]Options:[/yellow] {request.options}")

        # Ensure default download dir if not specified
        request.options.setdefault('download_dir', os.path.join(os.getcwd(), 'downloads'))

        # Add download task to background
        background_tasks.add_task(
             download_video_task,
             request.url,
             request.options,
             download_status_queue # Use dedicated download queue
        )

        return {
            "status": "success",
            "message": "Download task initiated in background.",
            "url": request.url,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting download task for {request.url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start download task: {e}")


# --- Get Video Info Endpoint ---
@app.post("/api/video-info", tags=["Download", "Utility"])
async def get_video_info(request: VideoInfoRequest):
    """Get metadata for a YouTube video or playlist without downloading."""
    if yt_dlp is None:
         raise HTTPException(status_code=501, detail="Info feature unavailable: yt-dlp library not installed.")

    logger.info(f"Video info request for URL: {request.url}")

    ydl_opts = {
        'quiet': True, 'no_warnings': True, 'skip_download': True,
        'extract_flat': 'in_playlist', # Faster for playlists, gets basic entry info
        # Consider 'forcejson': True if you only want the JSON output
    }
    info = None
    try:
        logger.debug(f"Extracting info for {request.url} in thread...")
        # Run potentially blocking network IO in thread
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
             info = await asyncio.to_thread(ydl.extract_info, request.url, download=False)
        logger.debug(f"Info extraction finished.")

        if not info:
             raise HTTPException(status_code=404, detail="Could not extract information for the given URL.")

        # --- Process Extracted Info ---
        is_playlist = info.get('_type') == 'playlist'
        playlist_count = len(info.get('entries', [])) if is_playlist else 0

        # Basic info
        title = info.get('title', 'N/A')
        author = info.get('uploader', info.get('channel', 'N/A'))
        thumbnail = info.get('thumbnail') # Might be low-res with extract_flat
        video_id = info.get('id', '')
        original_url = info.get('webpage_url', request.url)

        duration_str = "N/A"
        if is_playlist:
            duration_str = f"{playlist_count} videos"
            # If you need the first video's thumbnail/duration, requires another call for that entry
        else: # Single video
            duration_sec = info.get('duration')
            if duration_sec:
                try: duration_str = str(timedelta(seconds=int(duration_sec)))
                except: pass # Ignore conversion errors
            # If thumbnail missing, maybe try 'thumbnails' list if available
            if not thumbnail and info.get('thumbnails'):
                 thumbnail = info['thumbnails'][-1]['url'] # Try highest res

        # --- More Detailed Info (May require non-flat extraction, slower) ---
        # To get detailed formats/subtitles, remove 'extract_flat': 'in_playlist'
        # This will be slower as it fetches more data.

        # Formats (simplified from available data)
        formats = info.get('formats', [])
        available_formats_notes = sorted(list(set(
             f.get('format_note', f.get('resolution', f.get('ext')))
             for f in formats if f.get('format_note') or f.get('resolution') or f.get('ext')
        ))) if formats else ["N/A (requires detailed fetch)"]

        # Subtitles (simplified)
        subs = info.get('subtitles', {})
        auto_subs = info.get('automatic_captions', {})
        available_subtitles = sorted(list(subs.keys()))
        available_auto_captions = sorted(list(auto_subs.keys()))


        return {
            "title": title, "author": author, "thumbnail": thumbnail,
            "duration": duration_str, "is_playlist": is_playlist,
            "playlist_count": playlist_count if is_playlist else 1,
            "available_formats": available_formats_notes,
            "available_subtitles": available_subtitles,
            "available_auto_captions": available_auto_captions,
            "id": video_id, "original_url": original_url,
        }

    except yt_dlp.utils.DownloadError as e:
        logger.warning(f"yt-dlp info extraction failed for {request.url}: {e}")
        status_code = 400
        detail = f"Failed to process URL"
        # Check for common, informative errors
        if "Unsupported URL" in str(e): status_code = 400; detail = "Unsupported URL"
        elif "Video unavailable" in str(e): status_code = 404; detail = "Video unavailable"
        elif "Private video" in str(e): status_code = 403; detail = "Video is private"
        elif "Sign in to confirm your age" in str(e): status_code = 403; detail = "Video requires age verification (login)"
        raise HTTPException(status_code=status_code, detail=f"{detail}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching video info for {request.url}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error fetching video info: {e}")


# --- Get Default Directory Endpoint ---
@app.get("/api/default-directory", tags=["Utility"])
async def get_default_directory():
    """Suggest a default download directory path (client can override)."""
    path_str = ""
    warning = None
    try:
        # Try user's Downloads folder first
        try:
            user_downloads = str(Path.home() / "Downloads")
            # Basic check if it seems valid (exists and is dir)
            if Path(user_downloads).is_dir():
                 path_str = user_downloads
            else: # Fallback if ~/Downloads doesn't exist
                 path_str = os.path.abspath(os.path.join(os.getcwd(), 'downloads'))
                 warning = "User 'Downloads' directory not found, suggesting relative path."
        except Exception: # Error getting home dir or creating path
             path_str = os.path.abspath(os.path.join(os.getcwd(), 'downloads'))
             warning = "Could not determine user home directory, suggesting relative path."

        logger.info(f"Providing default download directory suggestion: {path_str}")
        response = {"path": path_str}
        if warning:
             response["warning"] = warning
        return response
    except Exception as e:
        logger.error(f"Error determining default directory: {e}", exc_info=True)
        fallback_dir = os.path.abspath('./downloads') # Safest fallback
        return {"path": fallback_dir, "warning": "Could not determine default path, using relative './downloads'."}


# --- Include Other Routers ---
if PROJECT_MODULES_LOADED:
    if 'content_upserter_router' in locals():
        try: app.include_router(content_upserter_router, prefix="/api/content", tags=["Content Management"])
        except Exception as e: logger.warning(f"Failed to include content_upserter_router: {e}")

    if 'metrics_router' in locals():
        try: app.include_router(metrics_router, prefix="/monitoring", tags=["Monitoring"])
        except Exception as e: logger.warning(f"Failed to include metrics_router: {e}")

    if 'monitoring_router' in locals() and metrics_router != monitoring_router: # Avoid double inclusion if same
         try: app.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])
         except Exception as e: logger.warning(f"Failed to include monitoring_router: {e}")


# --- Vector Search Endpoint (Example Structure) ---
# Initialize VectorSearcher if modules loaded and clients available
vector_searcher_instance = None
if PROJECT_MODULES_LOADED and 'VectorSearcher' in locals() and 'get_supabase_client' in locals():
    try:
        supabase_client = get_client() # Get Supabase client instance
        if supabase_client:
            # Pass required clients to VectorSearcher constructor
            vector_searcher_instance = VectorSearcher(
                 supabase_client=supabase_client,
                 openai_client=openai_client # Pass OpenAI client (or None)
                 # Add other dependencies like table names, embedding models if needed
            )
            logger.info("VectorSearcher initialized.")
        else:
            logger.warning("VectorSearcher not initialized: Supabase client unavailable.")
    except Exception as e:
         logger.error(f"Failed to initialize VectorSearcher: {e}", exc_info=True)

if vector_searcher_instance:
    @app.post("/api/vector-search", response_model=VectorSearchResponse, tags=["Search"])
    async def vector_search_endpoint(request: VectorSearchRequest):
        """Perform vector search on stored content embeddings."""
        logger.info(f"Vector search request: Query='{request.query[:50]}...', Max={request.max_results}, Threshold={request.threshold}")
        if not vector_searcher_instance: # Double check instance
             raise HTTPException(status_code=503, detail="Vector search service is unavailable.")
        try:
            # Perform search
            results, metadata = await vector_searcher_instance.search(
                query=request.query,
                similarity_threshold=request.threshold,
                match_count=request.max_results
            )
            logger.info(f"Vector search returned {len(results)} results.")

            # Optional: Generate AI response based on results
            ai_response = None
            # if results and (openai_client or groq_client): # Check if an LLM client is available
            #     try:
            #         ai_response = await vector_searcher_instance.generate_response_from_results(request.query, results)
            #         logger.info("Generated AI response based on search results.")
            #         # Count tokens if generated
            #         # token_counter.count_generation_tokens(input_text=..., output_text=ai_response)
            #     except Exception as ai_err:
            #         logger.error(f"Failed to generate AI response for search: {ai_err}", exc_info=True)
            #         metadata['ai_response_error'] = str(ai_err)

            # Add token usage stats to metadata
            metadata['token_usage'] = token_counter.get_stats()

            return VectorSearchResponse(
                results=results,
                ai_response=ai_response,
                metadata=metadata
            )

        except Exception as e:
             logger.error(f"Error during vector search for query '{request.query[:50]}...': {e}", exc_info=True)
             raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")
else:
     logger.warning("Vector search endpoint '/api/vector-search' disabled: VectorSearcher not initialized.")

@app.post("/api/search", response_model=ComprehensiveSearchResponse, tags=["Search"])
async def comprehensive_search_endpoint(
    request: ComprehensiveSearchRequest, # Request body
    # Query parameters for overrides
    fg_similarity_threshold: Optional[float] = Query(None, alias="fine_grained_similarity_threshold"),
    fg_content_weight: Optional[float] = Query(None, alias="fine_grained_content_weight"),
    fg_result_percentage: Optional[float] = Query(None, alias="fine_grained_result_percentage"),
    fg_max_results: Optional[int] = Query(None, alias="fine_grained_max_results"),
    ctx_similarity_threshold: Optional[float] = Query(None, alias="contextual_similarity_threshold"),
    ctx_content_weight: Optional[float] = Query(None, alias="contextual_content_weight"),
    ctx_result_percentage: Optional[float] = Query(None, alias="contextual_result_percentage"),
    ctx_max_results: Optional[int] = Query(None, alias="contextual_max_results"),
    ov_similarity_threshold: Optional[float] = Query(None, alias="overview_similarity_threshold"),
    ov_content_weight: Optional[float] = Query(None, alias="overview_content_weight"),
    ov_result_percentage: Optional[float] = Query(None, alias="overview_result_percentage"),
    ov_max_results: Optional[int] = Query(None, alias="overview_max_results"),
    preset: Optional[str] = Query(None)
):
    """
    Perform comprehensive search using logic from psearchworking.
    Accepts optional query parameters to override search settings.
    """
    # Check if core search module loaded correctly
    if not PROJECT_MODULES_LOADED or search_all is None or global_search_params is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Search feature is unavailable due to import errors.")

    logger.info(f"Search request: Query='{request.query[:50]}...', MaxRes={request.max_results}, Analysis={request.run_analysis}, Preset='{preset}'")

    # --- Update global search parameters based on query params ---
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
             logger.warning("Search parameters updated from frontend might be invalid (e.g., sum > 1.0). Check psearchworking validation logic.")
        logger.debug(f"Effective search params used: {global_search_params.get_all_params()}")
    except Exception as param_err:
         logger.error(f"Error updating search parameters: {param_err}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid search parameters provided.")

    # --- Perform Search ---
    start_time = time.time()
    try:
        # Run blocking search_all in a thread
        # Ensure search_all itself handles internal errors gracefully or raises them
        results, openai_analysis, groq_analysis = await asyncio.to_thread(
            search_all,
            query=request.query,
            max_results=request.max_results, # Pass total desired results
            skip_prompts=True, # Essential for backend
            run_analysis=request.run_analysis
            # search_all uses the updated global_search_params internally
        )

        search_duration = time.time() - start_time
        logger.info(f"Search completed in {search_duration:.2f}s. Found {len(results)} results.")

        # Format results using the to_dict method of SearchResult
        formatted_results = []
        if results:
            try:
                # Try to call to_dict() on each result
                formatted_results = [res.to_dict() for res in results]
                logger.info(f"Successfully converted {len(formatted_results)} SearchResult objects to dictionaries")
            except (AttributeError, TypeError) as e:
                logger.warning(f"Error converting SearchResult objects to dictionaries: {e}")
                # Fallback: manually convert SearchResult objects to dictionaries
                formatted_results = []
                for res in results:
                    try:
                        # Create a dictionary with all the necessary fields
                        result_dict = {
                            'id': f"{res.content_id}_{res.segment_id or '0'}_{res.start_time or '0'}",
                            'content_id': res.content_id,
                            'content': res.content,
                            'similarity': res.similarity,
                            'source': res.source,
                            'title': res.title or '',
                            'start_time': res.start_time,
                            'end_time': res.end_time,
                            'url': res.url or '',
                            'watch_url': res.watch_url or '',
                            'video_id': res.video_id,
                            'segment_id': res.segment_id,
                            'summary': res.summary or '',
                            'metadata': res.metadata or {},
                            'search_method': res.search_method or 'unknown',
                            'content_type': res.content_type or 'unknown'
                        }
                        formatted_results.append(result_dict)
                    except Exception as item_err:
                        logger.error(f"Error formatting individual result: {item_err}")
                
                logger.info(f"Manually converted {len(formatted_results)} SearchResult objects to dictionaries")

        metadata = {
            "query": request.query,
            "total_results_found": len(results),
            "search_duration_seconds": round(search_duration, 2),
            "analysis_run": request.run_analysis,
            "effective_params": global_search_params.get_all_params()
        }
        # Add token counts if available
        try:
            # Try to use token_counter from psearchworking first, then fall back to local token_counter
            try:
                from .psearchworking import token_counter as psearch_token_counter
                metadata["token_usage"] = psearch_token_counter.get_stats()
            except (ImportError, AttributeError):
                # Fall back to local token_counter
                metadata["token_usage"] = token_counter.get_stats()
        except (NameError, AttributeError) as tk_err:
            logger.warning(f"Could not get token stats: {tk_err}")

        return ComprehensiveSearchResponse(
            query=request.query,
            results=formatted_results,
            openai_analysis=openai_analysis,
            groq_analysis=groq_analysis,
            metadata=metadata
        )

    except Exception as e:
        search_duration = time.time() - start_time
        logger.error(f"Error during search execution ({search_duration:.2f}s): {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Search execution failed: {e}")
# --- Root and Health Check ---
@app.get("/", tags=["Utility"])
async def root():
    """Root endpoint providing basic service status."""
    logger.info("Root endpoint '/' called.")
    return {
        "service": "PMOVES Transcription API",
        "status": "running",
        "version": app.version,
        "timestamp": datetime.now().isoformat()
        }

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    # Add more checks here if needed (e.g., DB connectivity, queue status)
    logger.debug("Health check '/health' called")
    # Example: Check if Supabase client can be obtained
    db_status = "connected"
    try:
         client = get_client()
         # Maybe perform a trivial read if necessary/safe
         # e.g., client.table('your_table').select('id', count='exact').limit(0).execute()
    except Exception as e:
         db_status = f"error: {e}"
         logger.warning(f"Health check: Supabase client unavailable: {e}")

    return {"status": "healthy", "dependencies": {"database": db_status}, "timestamp": datetime.now().isoformat()}


# --- ASGI Server Runner ---
#if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server directly...")

    # Determine host and port
    app_host = os.getenv("HOST", "127.0.0.1")
    try:
        app_port = int(os.getenv("PORT", "8000"))
    except ValueError:
        logger.warning(f"Invalid PORT environment variable '{os.getenv('PORT')}', using default 8000.")
        app_port = 8000

    # Determine reload flag (enable only for development)
    # Be careful enabling reload in production-like environments
    reload_flag = os.getenv("ENABLE_RELOAD", "false").lower() in ["true", "1", "yes"]
    if reload_flag:
         logger.warning("Auto-reload enabled. Recommended only for development.")

    uvicorn.run(
        # Important: Use the string format "module_name:app_instance"
        # If this file is main.py, it's "main:app"
        f"{Path(__file__).stem}:app",
        host=app_host,
        port=app_port,
        reload=reload_flag,
        log_level="info", # Uvicorn's own log level
        # Use loop='uvloop' for potential performance gains if installed
        # loop="uvloop",
        # http="httptools", # Use httptools if installed
    )
