import os
import re
import json
import shutil
import logging
import asyncio
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import time

# OpenAI imports and initialization
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# Get the app directory path
APP_DIR = Path(__file__).parent.absolute()
ENV_PATH = APP_DIR / '.env'

# Load environment variables from the specific .env file location
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    print(f"Loaded environment variables from {ENV_PATH}")
else:
    print(f"Warning: .env file not found at {ENV_PATH}")
    # Fallback to default load_dotenv behavior
    load_dotenv()

# Initialize OpenAI client (used only for analysis)
if not os.getenv("OPENAI_API_KEY"):
    logger = logging.getLogger(__name__)
    logger.warning("OPENAI_API_KEY environment variable is not set. Some analysis features may be limited.")
    openai_client = None
else:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger = logging.getLogger(__name__)
    logger.info("OpenAI client initialized for analysis")

# Initialize Groq client (used for both transcription and analysis)
if not os.getenv("GROQ_API_KEY"):
    logger = logging.getLogger(__name__)
    logger.error("GROQ_API_KEY environment variable is not set")
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it before starting the server.")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
logger.info("Groq client initialized for transcription and analysis")

# Add the missing rich import
try:
    from rich.progress import SpinnerColumn
except ImportError:
    # Define a fallback if rich is not installed
    class SpinnerColumn:
        def __init__(self, *args, **kwargs):
            pass

# FastAPI and Starlette imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, Body, Request, status, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.responses import StreamingResponse
try:
    from sse_starlette.sse import EventSourceResponse
except ImportError:
    from starlette.responses import StreamingResponse as EventSourceResponse

# Third-party imports
import torch
import aiofiles
from pydantic import BaseModel, validator, ValidationError, Field
try:
    from tiktoken import get_encoding
except ImportError:
    print("Warning: tiktoken not found. Token counting will be estimated.")
    get_encoding = None

# Local imports
from .queue_manager import QueueManager
from .monitoring.logger import CustomLogger, PerformanceMonitor, async_timer
from .monitoring.metrics import MetricsCollector, TranscriptionMetrics, router as metrics_router
from .error_handlers import TranscriptionErrorHandler, ErrorSeverity
from .transcribe1 import process_video, VideoProcessRequest, get_optimal_device
from .utils import (
    convert_markdown_to_pdf,
    save_text_to_markdown,
    clean_filename,
    format_timestamp
)
from .fetch_content import (
    fetch_content_from_url,
    generate_unique_filename,
    sanitize_filename
)
from .config import DEFAULT_OUTPUT_FOLDER
from .psearchworking import search_all, ModelSelector, search_params, SearchParameters, analyze_search_results
from .config.search_config import get_preset, validate_search_params, DEFAULT_SEARCH_PARAMS, SEARCH_PRESETS, VALIDATION_LIMITS
from .routes.content_upserter import router as content_upserter_router
from .vector_search import VectorSearcher  # Add this import
from .monitoring.sse_monitor import sse_monitoring_middleware
from .monitoring.routes import router as monitoring_router

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize monitoring components
custom_logger = CustomLogger('transcription_service')
performance_monitor = PerformanceMonitor(custom_logger)
metrics_collector = MetricsCollector()
transcription_metrics = TranscriptionMetrics()

# Initialize queue manager
queue_manager = QueueManager()

# Add download status queue
download_status_queue = asyncio.Queue()

# Add status and transcription update queues
status_updates = asyncio.Queue()
transcription_updates = asyncio.Queue()

# Add TokenCounter class before any other classes that depend on it
class TokenCounter:
    """Tracks token usage for embeddings and generations."""
    
    def __init__(self):
        self.embedding_tokens = 0
        self.generation_tokens = {
            'input': 0,
            'output': 0
        }
        try:
            if get_encoding:
                self.encoders = {
                    'cl100k_base': get_encoding('cl100k_base'),  # For text-embedding-3-small
                    'gpt-4': get_encoding('cl100k_base'),  # For GPT-4 models
                }
            else:
                self.encoders = None
                logging.warning("TokenCounter initialized without tiktoken. Token counting will be estimated.")
        except Exception as e:
            logging.warning(f"Could not initialize encoders: {str(e)}")
            logging.warning("Token counting will be disabled.")
            self.encoders = None
    
    def count_embedding_tokens(self, text: str) -> int:
        """Count tokens for embedding."""
        if not self.encoders:
            # Estimate 4 chars per token as fallback
            return len(text) // 4
            
        try:
            tokens = len(self.encoders['cl100k_base'].encode(text))
            self.embedding_tokens += tokens
            return tokens
        except Exception as e:
            logging.warning(f"Could not count embedding tokens: {str(e)}")
            return len(text) // 4  # Estimate 4 chars per token
    
    def count_generation_tokens(self, input_text: str, output_text: str = None) -> dict:
        """Count tokens for generation (input and output)."""
        result = {'input': 0, 'output': 0}
        
        if not self.encoders:
            # Estimate 4 chars per token as fallback
            result['input'] = len(input_text) // 4
            if output_text:
                result['output'] = len(output_text) // 4
            return result
            
        try:
            input_tokens = len(self.encoders['gpt-4'].encode(input_text))
            self.generation_tokens['input'] += input_tokens
            result['input'] = input_tokens
            
            if output_text:
                output_tokens = len(self.encoders['gpt-4'].encode(output_text))
                self.generation_tokens['output'] += output_tokens
                result['output'] = output_tokens
        except Exception as e:
            logging.warning(f"Could not count generation tokens: {str(e)}")
            result['input'] = len(input_text) // 4  # Estimate 4 chars per token
            if output_text:
                result['output'] = len(output_text) // 4
            
        return result
    
    def get_stats(self) -> dict:
        """Get current token usage statistics."""
        return {
            'embedding_tokens': self.embedding_tokens,
            'generation_tokens': self.generation_tokens,
            'total_tokens': self.embedding_tokens + sum(self.generation_tokens.values())
        }

# Initialize token counter
token_counter = TokenCounter()

# Function to get Supabase client
def get_client():
    """Get a Supabase client instance from psearchworking.py."""
    from .psearchworking import get_client as get_psearch_client
    
    # Use the existing client from psearchworking.py
    return get_psearch_client()

class VideoRequest(BaseModel):
    youtube_video_url: str
    obsidian_dir: str
    output_folder: str
    transcription_model: str = "faster-whisper"
    use_groq: bool = False

    @validator('youtube_video_url')
    def validate_youtube_url(cls, v):
        youtube_regex = r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$'
        if not re.match(youtube_regex, v):
            raise ValueError('Invalid YouTube URL')
        return v

    @validator('output_folder')
    def output_folder_must_not_be_empty(cls, v):
        if not v:
            v = DEFAULT_OUTPUT_FOLDER
        return v

    @validator('obsidian_dir')
    def obsidian_dir_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Obsidian directory must not be empty')
        return v

    @validator('transcription_model')
    def validate_transcription_model(cls, v):
        valid_models = ["faster-whisper", "groq"]
        if v.lower() not in valid_models:
            raise ValueError(f"Invalid transcription model. Must be one of: {', '.join(valid_models)}")
        return v.lower()

    @validator('use_groq')
    def set_use_groq_based_on_model(cls, v, values):
        # Override use_groq based on transcription_model if present
        if 'transcription_model' in values:
            return values['transcription_model'].lower() == 'groq'
        return v

class VectorSearchRequest(BaseModel):
    """Request model for vector search."""
    query: str = Field(..., description="Search query")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Search query must not be empty')
        return v.strip()

class VectorSearchResponse(BaseModel):
    """Response model for vector search results."""
    results: List[Dict[str, Any]] = Field(default_factory=list, description="List of search results")
    ai_response: Optional[str] = Field(None, description="AI-generated response based on search results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the search")
    
    class Config:
        orm_mode = True

class FolderUpdate(BaseModel):
    old_path: str
    new_path: str

class DownloadRequest(BaseModel):
    url: str
    options: dict = {}

class VideoInfoRequest(BaseModel):
    url: str

# Initialize FastAPI app
app = FastAPI(
    title="PMOVES Transcription API",
    description="API for transcribing YouTube videos and processing content",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://127.0.0.1",
    "*"  # Temporarily add wildcard for debugging
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers
    expose_headers=["Content-Type", "X-Content-Type-Options"],
)

# Add OPTIONS method handler for CORS preflight requests
@app.options("/{path:path}")
async def options_handler(path: str):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={"detail": "OK"},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-Requested-With, Authorization",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Add SSE monitoring middleware
app.middleware("http")(sse_monitoring_middleware)

# Include monitoring routes
app.include_router(monitoring_router)

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        error_details = TranscriptionErrorHandler.handle_error(
            "UNKNOWN_ERROR",
            exc,
            path=str(request.url.path)
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_details
        )

# Add HTTP request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log the request
    start_time = time.time()
    method = request.method
    url = request.url
    path = request.url.path
    
    # Create a console for colorful terminal output
    from rich.console import Console
    console = Console()
    
    # Print the request info
    console.print(f"[bold blue]>> REQUEST:[/bold blue] {method} {path}")
    
    # Process the request
    response = await call_next(request)
    
    # Calculate request processing time
    process_time = time.time() - start_time
    formatted_process_time = f"{process_time:.3f}"
    
    # Get status code with color
    status_code = response.status_code
    status_color = "green" if status_code < 400 else "red"
    
    # Print the response info
    console.print(f"[bold blue]<< RESPONSE:[/bold blue] {method} {path} [bold {status_color}]{status_code}[/bold {status_color}] - {formatted_process_time}s")
    
    return response

@app.on_event("startup")
async def startup_event():
    await queue_manager.start()
    # Start system metrics collection
    asyncio.create_task(metrics_collector.collect_system_metrics())

@app.on_event("shutdown")
async def shutdown_event():
    await queue_manager.stop()

@app.get("/")
async def root():
    """Root endpoint for health checks from the frontend."""
    # Log that we received a request using the proper logger
    custom_logger.info("Root endpoint called - health check request received")
    custom_logger.info(f"Request time: {datetime.now()}")
    
    # Add a status update to show in the UI
    try:
        await queue_manager.status_queue.put(json.dumps({
            "type": "status",
            "content": "Backend connection established"
        }))
        custom_logger.info("Status update added to queue: Backend connection established")
    except Exception as e:
        custom_logger.error(f"Error putting to status queue: {str(e)}", exc_info=e)
    
    # Return response with basic info
    return {"status": "ok", "message": "Backend server is running"}

@app.get("/combined-updates")
async def get_combined_updates(request: Request):
    """Endpoint for Server-Sent Events that combines status and transcription updates."""
    from rich.console import Console
    console = Console()
    client_host = request.client.host if request.client else "unknown"
    client_id = f"client_{time.time()}"
    origin = request.headers.get("origin", "http://localhost:3000")
    console.print(f"[bold green]SSE connection requested from {client_host} with origin {origin}[/bold green]")
    
    # Always set origin to http://localhost:3000 for this endpoint
    # This is the most common frontend origin and fixes most CORS issues
    fixed_origin = "http://localhost:3000"
    
    async def event_generator():
        heartbeat_interval = 15  # seconds
        last_heartbeat = 0
        transcription_active = True
        
        # Send immediate confirmation that connection is established
        connection_message = json.dumps({
            "type": "status",
            "content": f"SSE connection established from {client_host}",
            "timestamp": datetime.now().isoformat()
        })
        yield f"data: {connection_message}\n\n"
        
        try:
            console.print("[bold blue]Starting SSE event generator[/bold blue]")
            while transcription_active:
                # Get current time for heartbeat
                current_time = time.time()
                
                # Check for status updates (non-blocking)
                try:
                    status_update = queue_manager.status_queue.get_nowait()
                    console.print(f"[yellow]Sending status update: {status_update}[/yellow]")
                    
                    # Parse the update to check for completion
                    try:
                        update_data = json.loads(status_update)
                        if update_data.get("type") == "transcription_complete":
                            transcription_active = False
                            console.print("[bold green]Transcription complete, will close SSE connection[/bold green]")
                    except json.JSONDecodeError:
                        pass
                        
                    yield f"data: {status_update}\n\n"
                except asyncio.QueueEmpty:
                    pass
                
                # Check for transcription updates (non-blocking)
                try:
                    transcription_update = queue_manager.transcription_queue.get_nowait()
                    console.print(f"[cyan]Sending transcription update: {transcription_update[:50]}...[/cyan]")
                    
                    # Parse the update to check for completion
                    try:
                        update_data = json.loads(transcription_update)
                        if update_data.get("type") == "transcription_complete":
                            transcription_active = False
                            console.print("[bold green]Transcription complete, will close SSE connection[/bold green]")
                    except json.JSONDecodeError:
                        pass
                        
                    yield f"data: {transcription_update}\n\n"
                except asyncio.QueueEmpty:
                    pass
                
                # Send heartbeat if no updates for a while
                if current_time - last_heartbeat > heartbeat_interval:
                    heartbeat_msg = json.dumps({
                        'type': 'heartbeat', 
                        'timestamp': datetime.now().isoformat()
                    })
                    console.print(f"[dim]Sending heartbeat: {heartbeat_msg}[/dim]")
                    yield f"data: {heartbeat_msg}\n\n"
                    last_heartbeat = current_time
                
                # Short delay to prevent CPU spinning
                await asyncio.sleep(0.1)
            
            # Send final completion message before closing
            completion_message = json.dumps({
                "type": "connection_closed",
                "content": "SSE connection closed - transcription complete",
                "timestamp": datetime.now().isoformat()
            })
            console.print("[bold blue]Sending connection closed message[/bold blue]")
            yield f"data: {completion_message}\n\n"
                
        except Exception as e:
            error_message = f"Error in combined updates SSE: {str(e)}"
            console.print(f"[bold red]Error in event generator:[/bold red] {error_message}")
            error_json = json.dumps({
                'type': 'error', 
                'content': error_message,
                'timestamp': datetime.now().isoformat()
            })
            yield f"data: {error_json}\n\n"
    
    # Create the response with proper CORS headers
    response = StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
    
    # Always use the fixed origin for this endpoint
    response.headers["Access-Control-Allow-Origin"] = fixed_origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS, POST"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"  # Cache preflight for 24 hours
    
    # Set other required headers for SSE
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["Connection"] = "keep-alive"
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["X-Accel-Buffering"] = "no"  # Disable proxy buffering
    
    # Log the headers for debugging
    console.print("[bold cyan]SSE Response Headers:[/bold cyan]")
    for key, value in response.headers.items():
        console.print(f"  [blue]{key}:[/blue] {value}")
    
    return response


# Add a specific OPTIONS handler for the SSE endpoint
@app.options("/combined-updates")
async def options_combined_updates(request: Request):
    """Handle OPTIONS requests for the SSE endpoint."""
    from fastapi.responses import JSONResponse
    from rich.console import Console
    console = Console()
    
    # Always use fixed origin for this endpoint
    fixed_origin = "http://localhost:3000"
    
    console.print(f"[bold green]OPTIONS request for SSE endpoint from {request.client.host if request.client else 'unknown'}[/bold green]")
    console.print(f"[bold cyan]Request headers: {dict(request.headers)}[/bold cyan]")
    
    response = JSONResponse(
        content={"detail": "OK"},
        status_code=200
    )
    
    # Always use the fixed origin for this endpoint
    response.headers["Access-Control-Allow-Origin"] = fixed_origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS, POST"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"  # Cache preflight for 24 hours
    
    # Log the headers for debugging
    console.print("[bold cyan]OPTIONS Response Headers:[/bold cyan]")
    for key, value in response.headers.items():
        console.print(f"  [blue]{key}:[/blue] {value}")
    
    return response

@app.post("/process-video/")
@async_timer(custom_logger)
async def process_video_endpoint(request: VideoRequest):
    try:
        performance_monitor.start_timer('process_video')
        transcription_metrics.record_request(True)
        
        logger.info(f"Processing video request: {request.dict()}")
        
        if not os.path.exists(request.obsidian_dir):
            raise HTTPException(status_code=400, detail="Obsidian directory does not exist")

        if not os.path.exists(request.output_folder):
            os.makedirs(request.output_folder, exist_ok=True)
            logger.info(f"Created output folder: {request.output_folder}")

        # Configure model settings based on request
        model_config = {
            "model": request.transcription_model,
            "use_groq": request.use_groq
        }
        
        if request.use_groq and request.transcription_model in ["llama-3.3-70b", "mixtral"]:
            # Add Groq-specific configuration
            model_config.update({
                "api_key": os.getenv("GROQ_API_KEY"),
                "model_name": f"groq/{request.transcription_model}"
            })

        # Start the background task with model configuration
        task = asyncio.create_task(process_video(
            request.youtube_video_url,
            request.obsidian_dir,
            queue_manager.status_queue,
            queue_manager.transcription_queue,
            output_folder=request.output_folder,
            model_config=model_config
        ))

        duration = performance_monitor.stop_timer('process_video')
        metrics_collector.add_metric('transcription_duration', duration)

        return {
            "status": "started",
            "message": "Video processing started"
        }

    except ValidationError as e:
        transcription_metrics.record_request(False)
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        transcription_metrics.record_request(False)
        logger.error(f"Error in process_video_endpoint: {str(e)}", exc_info=True)
        error_details = TranscriptionErrorHandler.handle_error(
            "UNKNOWN_ERROR",
            e,
            video_url=request.youtube_video_url
        )
        raise HTTPException(status_code=500, detail=error_details)

async def select_directory_dialog() -> str:
    """Open a directory selection dialog and return the selected path."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Ensure dialog appears on top
    path = filedialog.askdirectory()
    return path if path else ""

@app.post("/select-directory")
async def select_directory():
    """Endpoint to open a directory selection dialog."""
    try:
        selected_path = await select_directory_dialog()
        if not selected_path:
            raise HTTPException(status_code=400, detail="No directory selected")
        return {"path": selected_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New functions for video download feature using yt-dlp

async def download_video(url: str, options: dict, status_queue: asyncio.Queue):
    """Background task for downloading videos with yt-dlp"""
    try:
        import yt_dlp
        
        # Create download directory if it doesn't exist
        download_dir = options.get('download_dir', 'downloads')
        os.makedirs(download_dir, exist_ok=True)
        
        # Add timestamp to filename to prevent overwrites
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_template = os.path.join(download_dir, f'%(title)s_{timestamp}.%(ext)s')
        
        # Configure yt-dlp options
        ydl_opts = {
            'outtmpl': filename_template,
            'progress_hooks': [lambda d: report_download_progress(d, status_queue)],
            'quiet': False,
            'no_warnings': False,
            'keepvideo': True,  # Always keep video files regardless of extraction
            'overwrites': False  # Never overwrite existing files
        }
        
        # Handle format selection
        if options.get('format') == 'best':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        elif options.get('format') in ['1080p', '720p', '480p', '360p']:
            res = options.get('format').replace('p', '')
            ydl_opts['format'] = f'bestvideo[height<={res}]+bestaudio/best[height<={res}]'
        
        # Handle audio extraction
        if options.get('extractAudio', False):
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': options.get('audioFormat', 'mp3'),
                    'preferredquality': options.get('audioQuality', '192'),
                }]
            })
            # Always keep the original video
            ydl_opts['keepvideo'] = True
        
        # Handle thumbnail embedding
        if options.get('embedThumbnail', False):
            if 'postprocessors' not in ydl_opts:
                ydl_opts['postprocessors'] = []
            ydl_opts['postprocessors'].append({
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False
            })
            # For thumbnail embedding to work
            ydl_opts['writethumbnail'] = True
        
        # Handle metadata embedding
        if options.get('embedMetadata', True):
            if 'postprocessors' not in ydl_opts:
                ydl_opts['postprocessors'] = []
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            })
        
        # Handle subtitles - enhanced to save subtitles as separate files too
        if options.get('subtitles', False):
            ydl_opts.update({
                'writesubtitles': True,
                'writeautomaticsub': options.get('autoSubtitles', False),
                'subtitleslangs': [options.get('subtitleLanguage', 'en'), 'all'][options.get('subtitleLanguage', 'en') == 'auto'],
                'subtitlesformat': 'srt',  # Save as SRT format for maximum compatibility
                'allsubtitles': options.get('subtitleLanguage', 'en') == 'auto',
            })
        
        # Handle playlist downloading
        if options.get('downloadPlaylist', False):
            ydl_opts.update({
                'noplaylist': False,
                'playlist_items': f"{options.get('playlistStart', '1')}-{options.get('playlistEnd', '')}"
            })
        else:
            ydl_opts['noplaylist'] = True
        
        # Send initial status
        await status_queue.put(
            json.dumps({
                'type': 'status',
                'message': f'Starting download for: {url}',
                'download_dir': download_dir
            })
        )
        
        # Fetch video info first to get the title
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            
            # Send status with video title
            await status_queue.put(
                json.dumps({
                    'type': 'info',
                    'message': f'Found video: {title}',
                    'title': title
                })
            )
            
            # Start actual download
            await status_queue.put(
                json.dumps({
                    'type': 'status',
                    'message': 'Download started'
                })
            )
            
            # Execute the download
            ydl.download([url])
        
        # Send completion status
        await status_queue.put(
            json.dumps({
                'type': 'complete',
                'message': f'Download completed for: {title}'
            })
        )
        
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}", exc_info=True)
        # Send error to client
        await status_queue.put(
            json.dumps({
                'type': 'error',
                'message': f'Error downloading video: {str(e)}'
            })
        )

async def report_download_progress(d, status_queue: asyncio.Queue):
    """Report download progress to the client"""
    if d['status'] == 'downloading':
        try:
            # Extract progress information
            progress_str = d.get('_percent_str', '0%').strip()
            progress = float(progress_str.replace('%', ''))
            
            speed = d.get('_speed_str', 'Unknown speed')
            eta = d.get('_eta_str', 'Unknown ETA')
            filename = d.get('filename', 'Unknown filename')
            total_bytes = d.get('total_bytes', 0)
            
            # Format total size in human-readable format
            total_size = "Unknown size"
            if total_bytes:
                # Convert bytes to MB or GB
                if total_bytes < 1024*1024*1024:  # Less than 1GB
                    total_size = f"{total_bytes/(1024*1024):.2f} MB"
                else:
                    total_size = f"{total_bytes/(1024*1024*1024):.2f} GB"
            
            # Send progress update
            await status_queue.put(
                json.dumps({
                    'type': 'progress',
                    'progress': progress,
                    'speed': speed,
                    'eta': eta,
                    'filename': os.path.basename(filename),
                    'total_size': total_size
                })
            )
        except Exception as e:
            logger.error(f"Error reporting download progress: {str(e)}", exc_info=True)
    
    elif d['status'] == 'finished':
        # Send post-processing notification
        await status_queue.put(
            json.dumps({
                'type': 'status',
                'message': 'Download finished, post-processing file...'
            })
        )

@app.post("/api/download")
async def download_video_endpoint(request: DownloadRequest):
    """Endpoint to start a video download."""
    try:
        logger.info(f"Download request received for URL: {request.url}")
        
        # Set default download directory
        if 'download_dir' not in request.options:
            request.options['download_dir'] = os.path.join(os.getcwd(), 'downloads')
        
        # Start download in background
        asyncio.create_task(download_video(request.url, request.options, download_status_queue))
        
        return {
            "status": "success",
            "message": "Download started",
            "title": "Video download"  # This will be updated with actual title during download
        }
    except Exception as e:
        logger.error(f"Error in download_video_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download-status")
async def get_download_status(request: Request):
    """Endpoint for Server-Sent Events that provides download status updates."""
    from rich.console import Console
    console = Console()
    client_host = request.client.host if request.client else "unknown"
    client_id = f"download_client_{time.time()}"
    console.print(f"[bold green]Download status SSE connection requested from {client_host}[/bold green]")
    console.print(f"[bold cyan]Headers: {dict(request.headers)}[/bold cyan]")
    
    async def event_generator():
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to download status stream'})}\n\n"
            
            # Initialize heartbeat time
            last_heartbeat = time.time()
            
            while True:
                # Check for status updates (non-blocking)
                try:
                    status_update = download_status_queue.get_nowait()
                    # Ensure the status_update is proper JSON
                    if isinstance(status_update, str):
                        try:
                            # Check if it's already a valid JSON string
                            json.loads(status_update)
                            yield f"data: {status_update}\n\n"
                        except json.JSONDecodeError:
                            # If not valid JSON string, convert it to one
                            yield f"data: {json.dumps({'type': 'status', 'message': status_update})}\n\n"
                    elif isinstance(status_update, dict):
                        # Convert dict to JSON string
                        yield f"data: {json.dumps(status_update)}\n\n"
                    else:
                        # Try to convert other types to string first
                        yield f"data: {json.dumps({'type': 'status', 'message': str(status_update)})}\n\n"
                    
                    # Force flush the event
                    await asyncio.sleep(0)
                except asyncio.QueueEmpty:
                    # If no updates, send heartbeat to keep connection alive
                    current_time = time.time()
                    if current_time - last_heartbeat > 15:  # Send heartbeat every 15 seconds
                        last_heartbeat = current_time
                        yield f"data: {json.dumps({'type': 'heartbeat', 'message': 'ping'})}\n\n"
                        # Force flush heartbeat
                        await asyncio.sleep(0)
                    
                    # Small sleep to prevent CPU spinning
                    await asyncio.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error in download status event generator: {str(e)}", exc_info=True)
            # Send error to client
            yield f"data: {json.dumps({'type': 'error', 'message': f'Stream error: {str(e)}'})}\n\n"
            await asyncio.sleep(0)
    
    try:
        # Try to use EventSourceResponse if available
        response = EventSourceResponse(event_generator())
    except Exception as e:
        console.print(f"[bold yellow]Error using EventSourceResponse: {str(e)}. Falling back to StreamingResponse.[/bold yellow]")
        # Fall back to StreamingResponse if EventSourceResponse fails
        response = StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    
    # Set CORS headers explicitly - use specific origin instead of wildcard
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS, POST"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    # Set other required headers for SSE
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["Connection"] = "keep-alive"
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["X-Accel-Buffering"] = "no"  # Disable proxy buffering
    
    # Log the headers for debugging
    console.print("[bold cyan]SSE Response Headers:[/bold cyan]")
    for key, value in response.headers.items():
        console.print(f"  [blue]{key}:[/blue] {value}")
    
    return response

@app.post("/api/video-info")
async def get_video_info(request: VideoInfoRequest):
    """Endpoint to get information about a video without downloading it."""
    try:
        import yt_dlp
        
        logger.info(f"Video info request received for URL: {request.url}")
        
        # Configure yt-dlp options for info extraction only
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'skip_download': True
        }
        
        # Extract video info
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            # Check if it's a playlist
            is_playlist = False
            playlist_count = 0
            
            if 'entries' in info:
                # It's a playlist
                is_playlist = True
                playlist_count = len(info.get('entries', []))
                
                # Get the first video info for thumbnail
                if playlist_count > 0:
                    try:
                        # Try to get the first entry's full info
                        first_video_url = info['entries'][0]['url']
                        first_video_info = ydl.extract_info(first_video_url, download=False)
                        thumbnail = first_video_info.get('thumbnail', '')
                    except Exception:
                        # If that fails, use playlist thumbnail
                        thumbnail = info.get('thumbnail', '')
                else:
                    thumbnail = info.get('thumbnail', '')
                    
                title = info.get('title', 'Unknown Playlist')
                author = info.get('uploader', '')
                duration = "Playlist"
                
            else:
                # It's a single video
                thumbnail = info.get('thumbnail', '')
                title = info.get('title', 'Unknown Video')
                author = info.get('uploader', '')
                
                # Format duration
                duration_seconds = info.get('duration', 0)
                if duration_seconds:
                    minutes, seconds = divmod(duration_seconds, 60)
                    hours, minutes = divmod(minutes, 60)
                    if hours:
                        duration = f"{hours}:{minutes:02d}:{seconds:02d}"
                    else:
                        duration = f"{minutes}:{seconds:02d}"
                else:
                    duration = "Unknown"
            
            # Return formatted response
            return {
                "title": title,
                "author": author,
                "thumbnail": thumbnail,
                "duration": duration,
                "is_playlist": is_playlist,
                "playlist_count": playlist_count,
                "available_formats": [
                    format_info.get('format_note', 'Unknown') 
                    for format_info in info.get('formats', [])
                    if 'format_note' in format_info
                ],
                "has_subtitles": len(info.get('subtitles', {})) > 0,
                "id": info.get('id', '')
            }
    
    except Exception as e:
        logger.error(f"Error fetching video info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching video info: {str(e)}")

@app.get("/api/default-directory")
async def get_default_directory():
    """Endpoint to get the default download directory."""
    try:
        # Return the downloads directory in the current working directory
        download_dir = os.path.join(os.getcwd(), 'downloads')
        
        # Create directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)
        
        return {"path": download_dir}
    except Exception as e:
        logger.error(f"Error getting default directory: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/list-downloads")
async def list_downloaded_files(directory: Optional[str] = None):
    """Endpoint to list downloaded files."""
    try:
        # Use provided directory or default downloads folder
        download_dir = directory or os.path.join(os.getcwd(), 'downloads')
        
        # Check if the directory exists
        if not os.path.exists(download_dir):
            return {"files": [], "message": "Download directory does not exist yet"}
        
        # Get list of files in the download directory
        files = []
        for filename in os.listdir(download_dir):
            file_path = os.path.join(download_dir, filename)
            if os.path.isfile(file_path):
                # Get file stats
                stats = os.stat(file_path)
                file_size = stats.st_size
                modified_time = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                # Format file size
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024*1024:
                    size_str = f"{file_size/1024:.2f} KB"
                elif file_size < 1024*1024*1024:
                    size_str = f"{file_size/(1024*1024):.2f} MB"
                else:
                    size_str = f"{file_size/(1024*1024*1024):.2f} GB"
                
                # Determine file type
                extension = os.path.splitext(filename)[1].lower()
                file_type = "Other"
                if extension in ['.mp4', '.mkv', '.avi', '.webm', '.mov']:
                    file_type = "Video"
                elif extension in ['.mp3', '.wav', '.m4a', '.aac', '.opus']:
                    file_type = "Audio"
                elif extension in ['.jpg', '.jpeg', '.png', '.webp']:
                    file_type = "Image"
                elif extension in ['.srt', '.vtt', '.ass']:
                    file_type = "Subtitle"
                
                files.append({
                    "name": filename,
                    "path": file_path,
                    "size": size_str,
                    "raw_size": file_size,
                    "type": file_type,
                    "modified": modified_time
                })
        
        # Sort files by modification time (newest first)
        files.sort(key=lambda x: x["modified"], reverse=True)
        
        return {
            "files": files,
            "directory": download_dir,
            "count": len(files)
        }
    
    except Exception as e:
        logger.error(f"Error listing downloaded files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.get("/api/download-file/{filename:path}")
async def download_file(filename: str, directory: Optional[str] = None):
    """Endpoint to download a specific file."""
    try:
        # Use provided directory or default downloads folder
        download_dir = directory or os.path.join(os.getcwd(), 'downloads')
        file_path = os.path.join(download_dir, filename)
        
        # Check if the file exists
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        return FileResponse(
            path=file_path, 
            filename=filename,
            media_type="application/octet-stream"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")

# Add the fetch-content endpoint
@app.get("/fetch-content/")
async def fetch_content(
    url: str, 
    json_response: bool = False, 
    timeout: Optional[int] = None, 
    target_selector: Optional[str] = None,
    excluded_selector: Optional[str] = None,
    clean_format: bool = True,
    browser_engine: str = "playwright",
    token_budget: int = 4000,
    remove_images: bool = False,
    extract_links: bool = True,
    image_captioning: bool = False,
    cache_ttl: int = 3600,
    markdown_flavor: str = "github",
    browser_viewport: str = "1920x1080",
    browser_locale: str = "en-US",
    extract_metadata: bool = True
):
    """
    Fetch content from a URL using Jina Reader API
    
    Args:
        url: URL to fetch content from
        json_response: Whether to return the response as JSON
        timeout: Timeout in seconds
        target_selector: CSS selector to target specific elements
        excluded_selector: CSS selector for elements to exclude
        clean_format: Whether to clean and format the content
        browser_engine: 'playwright' for better quality or 'selenium' for speed
        token_budget: Maximum number of tokens to extract
        remove_images: Whether to exclude images from the content
        extract_links: Whether to extract links from the content
        image_captioning: Whether to add captions to images
        cache_ttl: Time-to-live for cache in seconds
        markdown_flavor: 'github', 'standard', or 'obsidian'
        browser_viewport: Browser viewport size (e.g. '1920x1080')
        browser_locale: Browser locale (e.g. 'en-US')
        extract_metadata: Whether to extract page metadata
    """
    try:
        content = await fetch_content_from_url(
            url, 
            json_response, 
            timeout, 
            target_selector,
            excluded_selector,
            clean_format,
            browser_engine,
            token_budget,
            remove_images,
            extract_links,
            image_captioning,
            cache_ttl,
            markdown_flavor,
            browser_viewport,
            browser_locale,
            extract_metadata
        )
        logger.info(f"Content fetched successfully from {url}")

        # Use absolute path for saving files
        base_dir = os.path.abspath(os.path.join(os.getcwd(), 'fetched_content'))
        os.makedirs(base_dir, exist_ok=True)
        logger.info(f"Created directory: {base_dir}")

        # Generate filenames
        markdown_filename = generate_unique_filename(url, 'md')
        pdf_filename = generate_unique_filename(url, 'pdf')
        
        markdown_path = os.path.join(base_dir, markdown_filename)
        pdf_path = os.path.join(base_dir, pdf_filename)

        logger.info(f"Final markdown path: {markdown_path}")
        logger.info(f"Final PDF path: {pdf_path}")

        # Determine the content to save
        markdown_content = content
        if isinstance(content, dict):
            markdown_content = content.get('content', json.dumps(content, indent=2))
        
        # Properly await the async file operations
        await save_text_to_markdown(markdown_content, markdown_path)
        logger.info(f"Markdown saved successfully to: {markdown_path}")
        
        # Try to convert to PDF, but don't fail if it doesn't work
        pdf_success = await convert_markdown_to_pdf(markdown_path, pdf_path)
        if pdf_success:
            logger.info(f"PDF converted successfully to: {pdf_path}")
        else:
            logger.warning(f"PDF conversion failed but will continue with markdown content")
            # Set pdf_path to None if conversion failed
            pdf_path = None

        # Prepare response
        response = {
            "markdown_path": markdown_path,
            "markdown_content": markdown_content,
        }

        # Only include PDF path if conversion was successful
        if pdf_path:
            response["pdf_path"] = pdf_path
        
        # Add additional data if content is a dict
        if isinstance(content, dict):
            response.update({
                "title": content.get('title', ''),
                "url": content.get('url', url),
                "links": content.get('links', []),
                "metadata": content.get('metadata', {})
            })
            
        return response
    except Exception as e:
        logger.error(f"Error fetching content from {url}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to format JSON for SSE with event field (for vector search)
def json_to_sse_structured(data):
    """Format JSON data for server-sent events with structured event and data fields."""
    # Create a console for colorful terminal output
    from rich.console import Console
    console = Console()
    
    if not isinstance(data, dict):
        # For string data just wrap in a simple data field
        console.print(f"[yellow]SSE Message:[/yellow] {data}")
        return f"data: {json.dumps({'data': data})}\n\n"
    
    # For dict data, ensure it's properly formatted as a string
    if isinstance(data, dict) and 'type' in data and 'data' in data:
        # Already has type and data fields, format correctly
        message_type = data['type']
        message_data = data['data']
        
        # Color-coded output based on message type
        if message_type == 'error':
            console.print(f"[bold red]SSE Error:[/bold red] {message_data}")
        elif message_type == 'log':
            console.print(f"[blue]SSE Log:[/blue] {message_data}")
        elif message_type == 'results' or message_type == 'complete':
            console.print(f"[green]SSE {message_type.capitalize()}:[/green] {message_data if isinstance(message_data, str) else 'Results data'}")
        else:
            console.print(f"[yellow]SSE {message_type.capitalize()}:[/yellow] {message_data if isinstance(message_data, str) else 'Data object'}")
        
        return f"data: {json.dumps(data)}\n\n"
    else:
        # Missing proper structure, try to normalize
        console.print(f"[magenta]SSE Raw Data:[/magenta] {data}")
        return f"data: {json.dumps(data)}\n\n"

# Standardized helper function for SSE responses
async def create_sse_response(generator, request=None, client_id=None, endpoint=None):
    """
    Create a standardized SSE response with proper CORS headers and monitoring.
    
    Args:
        generator: The async generator that yields SSE events
        request: The FastAPI request object
        client_id: Optional client ID for monitoring
        endpoint: Optional endpoint name for monitoring
    
    Returns:
        A properly configured SSE response
    """
    from rich.console import Console
    console = Console()
    
    # Generate a client ID if not provided
    if not client_id and request:
        client_id = f"client_{time.time()}"
    
    # Get endpoint name if not provided
    if not endpoint and request:
        endpoint = request.url.path
    
    # Log connection attempt
    console.print(f"[bold green]SSE connection requested from {request.client.host if request else 'unknown'} to {endpoint}[/bold green]")
    
    # Wrap the generator to add monitoring
    async def monitored_generator():
        try:
            # Send initial connection message
            connection_message = json.dumps({
                "type": "connected",
                "message": "SSE connection established"
            })
            yield f"data: {connection_message}\n\n"
            
            # Track the connection in the monitor
            from .monitoring.sse_monitor import sse_monitor
            if client_id and endpoint:
                sse_monitor.track_connection(client_id, endpoint)
            
            # Process events from the original generator
            async for event in generator:
                # Track the message if it's not a heartbeat
                if client_id and not event.startswith('data: {"type":"heartbeat"'):
                    try:
                        from .monitoring.sse_monitor import monitor_sse_message
                        monitor_sse_message(client_id, event, endpoint)
                    except Exception as e:
                        console.print(f"[bold red]Error monitoring message: {str(e)}[/bold red]")
                
                yield event
                
        except Exception as e:
            error_message = f"Error in SSE generator: {str(e)}"
            console.print(f"[bold red]{error_message}[/bold red]")
            yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"
            
            # Track disconnection
            if client_id:
                from .monitoring.sse_monitor import sse_monitor
                sse_monitor.track_disconnection(client_id)
    
    # Create the response with the monitored generator
    try:
        # First try with EventSourceResponse
        response = EventSourceResponse(monitored_generator())
    except Exception as e:
        # Fall back to StreamingResponse if EventSourceResponse fails
        console.print(f"[bold yellow]Falling back to StreamingResponse due to: {str(e)}[/bold yellow]")
        response = StreamingResponse(
            monitored_generator(),
            media_type="text/event-stream"
        )
    
    # Set CORS headers explicitly
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    
    # Set other required headers for SSE
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["Connection"] = "keep-alive"
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["X-Accel-Buffering"] = "no"  # Disable proxy buffering
    
    # Log the headers for debugging
    console.print("[bold cyan]SSE Response Headers:[/bold cyan]")
    for key, value in response.headers.items():
        console.print(f"  [blue]{key}:[/blue] {value}")
    
    return response

# Backward compatibility alias for existing code
async def cors_event_source_response(generator, request=None):
    """Legacy function for backward compatibility"""
    return await create_sse_response(generator, request)

@app.get("/vector-search-stream")
async def vector_search_stream(
    request: Request,
    query: str,
    preset: str = "default",
    run_analysis: bool = True,
    fine_grained_similarity_threshold: float = 0.75,
    fine_grained_content_weight: float = 0.8,
    fine_grained_result_percentage: float = 0.4,
    fine_grained_max_results: int = 15,
    contextual_similarity_threshold: float = 0.7,
    contextual_content_weight: float = 0.7,
    contextual_result_percentage: float = 0.35,
    contextual_max_results: int = 10,
    overview_similarity_threshold: float = 0.65,
    overview_content_weight: float = 0.5,
    overview_result_percentage: float = 0.25,
    overview_max_results: int = 5,
):
    """Stream vector search results with SSE using psearchworking.py implementation."""
    from rich.console import Console
    console = Console()
    
    async def event_generator():
        try:
            # Initialize search parameters
            search_params.update_from_frontend(
                fine_grained_similarity_threshold=fine_grained_similarity_threshold,
                fine_grained_content_weight=fine_grained_content_weight,
                fine_grained_result_percentage=fine_grained_result_percentage,
                fine_grained_max_results=fine_grained_max_results,
                contextual_similarity_threshold=contextual_similarity_threshold,
                contextual_content_weight=contextual_content_weight,
                contextual_result_percentage=contextual_result_percentage,
                contextual_max_results=contextual_max_results,
                overview_similarity_threshold=overview_similarity_threshold,
                overview_content_weight=overview_content_weight,
                overview_result_percentage=overview_result_percentage,
                overview_max_results=overview_max_results,
                preset=preset
            )

            # Log search start
            console.print(f"\n[bold yellow]Starting search for:[/bold yellow] {query}")
            yield f"data: {json.dumps({'type': 'status', 'message': f'Starting search for: {query}'})}\n\n"

            # Create embedding - try OpenAI first, fallback to Groq if OpenAI not available
            try:
                if openai_client:
                    response = openai_client.embeddings.create(
                        input=query,
                        model="text-embedding-3-small",
                        dimensions=1536
                    )
                    query_embedding = response.data[0].embedding
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Generated embedding using OpenAI'})}\n\n"
                else:
                    # Use Groq for embedding
                    response = groq_client.embeddings.create(
                        input=query,
                        model="text-embedding-3-small",
                        dimensions=1536
                    )
                    query_embedding = response.data[0].embedding
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Generated embedding using Groq'})}\n\n"
            except Exception as e:
                logger.error(f"Error generating embedding: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': f'Error generating embedding: {str(e)}'})}\n\n"
                return

            # Get Supabase client
            supabase = get_client()

            # Perform searches
            try:
                # Dot product search
                dot_product_results = supabase.rpc(
                    'dot_product_search',
                    {
                        'query_embedding': query_embedding,
                        'match_count': fine_grained_max_results,
                        'content_weight': fine_grained_content_weight,
                        'summary_weight': 1.0 - fine_grained_content_weight
                    }
                ).execute()

                # Keyword search
                keyword_results = supabase.rpc(
                    'keyword_search',
                    {
                        'query_text': query,
                        'match_count': contextual_max_results
                    }
                ).execute()

                # Advanced hybrid search
                hybrid_results = supabase.rpc(
                    'advanced_hybrid_search',
                    {
                        'query_embedding': query_embedding,
                        'match_count': overview_max_results,
                        'content_weight': overview_content_weight,
                        'summary_weight': 1.0 - overview_content_weight,
                        'video_filter': None,
                        'min_similarity': overview_similarity_threshold
                    }
                ).execute()

                # Combine and process results
                all_results = []
                
                # Process dot product results
                if dot_product_results.data:
                    for result in dot_product_results.data:
                        result['search_method'] = 'dot_product'
                        all_results.append(result)
                
                # Process keyword results
                if keyword_results.data:
                    for result in keyword_results.data:
                        result['search_method'] = 'keyword'
                        all_results.append(result)
                
                # Process hybrid results
                if hybrid_results.data:
                    for result in hybrid_results.data:
                        result['search_method'] = 'hybrid'
                        all_results.append(result)

                # Send results
                yield f"data: {json.dumps({'type': 'results', 'results': all_results})}\n\n"
                yield f"data: {json.dumps({'type': 'status', 'message': f'Found {len(all_results)} results'})}\n\n"

                # Run analysis if requested
                if run_analysis and all_results:
                    # Always run Groq analysis since we know it's available
                    groq_analysis = analyze_search_results(all_results, provider='groq', max_results=10)
                    if groq_analysis:
                        yield f"data: {json.dumps({'type': 'ai_response_groq', 'analysis': groq_analysis})}\n\n"

                    # Only run OpenAI analysis if client is available
                    if openai_client:
                        openai_analysis = analyze_search_results(all_results, provider='openai')
                        if openai_analysis:
                            yield f"data: {json.dumps({'type': 'ai_response_openai', 'analysis': openai_analysis})}\n\n"

                # Send token usage
                token_stats = token_counter.get_stats()
                if token_stats:
                    yield f"data: {json.dumps({'type': 'token_usage', 'usage': token_stats})}\n\n"

            except Exception as e:
                logger.error(f"Error performing search: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': f'Error performing search: {str(e)}'})}\n\n"
                return

            # Send completion message
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Search completed'})}\n\n"

        except Exception as e:
            logger.error(f"Error in vector search stream: {str(e)}", exc_info=True)
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Search failed'})}\n\n"

    return await cors_event_source_response(
        event_generator(),
        request
    )

# Search Config Pydantic Models
class TierParameters(BaseModel):
    """Parameters for a specific search tier."""
    similarity_threshold: float = Field(..., ge=0.0, le=1.0, description="Similarity threshold for this tier")
    content_weight: float = Field(..., ge=0.0, le=1.0, description="Content weight for this tier")
    result_percentage: float = Field(..., ge=0.0, le=1.0, description="Result percentage for this tier")
    max_results: int = Field(..., ge=1, le=50, description="Maximum number of results for this tier")

class SearchParametersConfig(BaseModel):
    """Complete search parameters configuration."""
    fine_grained: TierParameters
    contextual: TierParameters
    overview: TierParameters

class PresetNameRequest(BaseModel):
    """Request model for loading a preset by name."""
    preset_name: str = Field(..., description="Name of the preset to load")

class SearchTierUpdate(BaseModel):
    """Update for a single search tier's parameters."""
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Similarity threshold for this tier")
    content_weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="Content weight for this tier")
    result_percentage: Optional[float] = Field(None, ge=0.0, le=1.0, description="Result percentage for this tier")
    max_results: Optional[int] = Field(None, ge=1, le=50, description="Maximum number of results for this tier")

class SearchParametersUpdate(BaseModel):
    """Update specific parameters across tiers."""
    fine_grained: Optional[SearchTierUpdate] = None
    contextual: Optional[SearchTierUpdate] = None
    overview: Optional[SearchTierUpdate] = None

# Search Configuration Endpoints
@app.get("/api/search-config", response_model=SearchParametersConfig)
async def get_search_config():
    """Get the current search configuration."""
    logging.info("Retrieving current search configuration")
    
    # Get current parameters
    params = search_params.get_all_params()
    
    # Convert to Pydantic model structure
    return SearchParametersConfig(
        fine_grained=TierParameters(**params["fine_grained"]),
        contextual=TierParameters(**params["contextual"]),
        overview=TierParameters(**params["overview"])
    )

@app.post("/api/search-config", response_model=SearchParametersConfig)
async def update_search_config(update: SearchParametersUpdate):
    """Update the search configuration."""
    logging.info("Updating search configuration")
    
    # Process updates for each tier
    if update.fine_grained:
        tier_updates = {k: v for k, v in update.fine_grained.dict().items() if v is not None}
        if tier_updates:
            search_params.update_params("fine_grained", **tier_updates)
    
    if update.contextual:
        tier_updates = {k: v for k, v in update.contextual.dict().items() if v is not None}
        if tier_updates:
            search_params.update_params("contextual", **tier_updates)
    
    if update.overview:
        tier_updates = {k: v for k, v in update.overview.dict().items() if v is not None}
        if tier_updates:
            search_params.update_params("overview", **tier_updates)
    
    # Return updated configuration
    params = search_params.get_all_params()
    return SearchParametersConfig(
        fine_grained=TierParameters(**params["fine_grained"]),
        contextual=TierParameters(**params["contextual"]),
        overview=TierParameters(**params["overview"])
    )

@app.get("/api/search-config/presets")
async def get_presets():
    """Get the list of available presets."""
    logging.info("Retrieving available presets")
    return {"presets": list(SEARCH_PRESETS.keys())}

@app.get("/api/search-config/preset/{preset_name}", response_model=SearchParametersConfig)
async def get_preset_config(preset_name: str):
    """Get a specific preset configuration."""
    logging.info(f"Retrieving preset configuration: {preset_name}")
    
    preset = get_preset(preset_name)
    if not preset:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found")
    
    return SearchParametersConfig(
        fine_grained=TierParameters(**preset["fine_grained"]),
        contextual=TierParameters(**preset["contextual"]),
        overview=TierParameters(**preset["overview"])
    )

@app.post("/api/search-config/preset")
async def load_preset(request: PresetNameRequest):
    """Load a preset configuration."""
    logging.info(f"Loading preset: {request.preset_name}")
    
    success = search_params.load_preset(request.preset_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Failed to load preset '{request.preset_name}'")
    
    # Return the updated configuration
    params = search_params.get_all_params()
    return {
        "success": True,
        "message": f"Preset '{request.preset_name}' loaded successfully",
        "config": SearchParametersConfig(
            fine_grained=TierParameters(**params["fine_grained"]),
            contextual=TierParameters(**params["contextual"]),
            overview=TierParameters(**params["overview"])
        )
    }

# Add the content_upserter router to the application
app.include_router(content_upserter_router, prefix="/api/content")

# Additional endpoints remain the same...

# Define SearchResult class to match expected format
class SearchResult:
    """Search result with similarity score and content."""
    def __init__(self, id=None, content="", similarity=0.0, source="", start_time=None, end_time=None,
                 watch_url=None, summary=None, search_method="unknown", video_id=None, title=None):
        self.id = id or f"result-{id(self)}"
        self.content = content
        self.similarity = similarity
        self.source = source
        self.start_time = start_time
        self.end_time = end_time
        self.watch_url = watch_url
        self.summary = summary
        self.search_method = search_method
        self.video_id = video_id
        self.title = title
    
    def to_dict(self):
        """Convert to dictionary format for JSON response."""
        return {
            "id": self.id,
            "content": self.content,
            "similarity": self.similarity,
            "source": self.source,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "watch_url": self.watch_url,
            "summary": self.summary,
            "search_method": self.search_method,
            "video_id": self.video_id,
            "title": self.title
        }

# Stub implementations for search functions
async def search_fine_grained(query, similarity_threshold, content_weight, max_results):
    """
    Stub implementation for fine-grained search.
    In a real implementation, this would search a vector database.
    """
    logger.info(f"Fine-grained search for '{query}' with threshold={similarity_threshold}, content_weight={content_weight}, max_results={max_results}")
    
    # Generate sample results for testing
    results = []
    for i in range(min(3, max_results)):
        similarity = similarity_threshold + (0.9 - similarity_threshold) * (3 - i) / 3
        results.append(SearchResult(
            id=f"fine-{i}",
            content=f"Fine-grained result {i+1} for query: {query}",
            similarity=similarity,
            source=f"Sample source {i+1}",
            search_method="fine_grained",
            video_id=f"video-{i}",
            title=f"Sample Video {i+1}"
        ))
    
    return results

async def search_contextual(query, similarity_threshold, content_weight, max_results):
    """
    Stub implementation for contextual search.
    In a real implementation, this would search with more context.
    """
    logger.info(f"Contextual search for '{query}' with threshold={similarity_threshold}, content_weight={content_weight}, max_results={max_results}")
    
    # Generate sample results for testing
    results = []
    for i in range(min(2, max_results)):
        similarity = similarity_threshold + (0.85 - similarity_threshold) * (2 - i) / 2
        results.append(SearchResult(
            id=f"context-{i}",
            content=f"Contextual result {i+1} with broader context for: {query}",
            similarity=similarity,
            source=f"Context source {i+1}",
            search_method="contextual",
            video_id=f"video-{i+3}",
            title=f"Context Video {i+1}"
        ))
    
    return results

async def search_overview(query, similarity_threshold, content_weight, max_results):
    """
    Stub implementation for overview search.
    In a real implementation, this would search for high-level overviews.
    """
    logger.info(f"Overview search for '{query}' with threshold={similarity_threshold}, content_weight={content_weight}, max_results={max_results}")
    
    # Generate sample results for testing
    results = []
    for i in range(min(1, max_results)):
        similarity = similarity_threshold + (0.8 - similarity_threshold) * (1 - i)
        results.append(SearchResult(
            id=f"overview-{i}",
            content=f"Overview result {i+1} providing high-level information about: {query}",
            similarity=similarity,
            source=f"Overview source {i+1}",
            search_method="overview",
            video_id=f"video-{i+5}",
            title=f"Overview Video {i+1}"
        ))
    
    return results

@app.get("/search-stream")
async def search_stream(
    request: Request,
    query: str = Query(..., description="Search query"),
    preset: str = Query("default", description="Search preset name"),
    run_analysis: bool = Query(True, description="Whether to run analysis on results"),
    fine_grained_similarity_threshold: float = Query(None),
    fine_grained_content_weight: float = Query(None),
    fine_grained_result_percentage: float = Query(None),
    fine_grained_max_results: int = Query(None),
    contextual_similarity_threshold: float = Query(None),
    contextual_content_weight: float = Query(None),
    contextual_result_percentage: float = Query(None),
    contextual_max_results: int = Query(None),
    overview_similarity_threshold: float = Query(None),
    overview_content_weight: float = Query(None),
    overview_result_percentage: float = Query(None),
    overview_max_results: int = Query(None),
):
    """Stream search results as Server-Sent Events."""
    
    # Add rich console output
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    
    # Create a console for terminal output
    console = Console()
    console.print(f"\n[bold yellow]Search Query:[/bold yellow] {query}")
    
    logger.info(f"Starting search stream for query: {query}")
    
    async def event_generator():
        nonlocal run_analysis
        try:
            # Initialize with defaults
            try:
                search_params = SearchParameters()
                
                # Record original parameters for logging
                original_params = {
                    'query': query,
                    'preset': preset,
                    'run_analysis': run_analysis
                }
                
                # Update with preset if provided
                if preset and preset != "default":
                    logger.info(f"Loading preset: {preset}")
                    console.print(f"[blue]Loading preset:[/blue] {preset}")
                    search_params.load_preset(preset)
                
                # Convert run_analysis to boolean if it's a string
                if isinstance(run_analysis, str):
                    run_analysis = run_analysis.lower() == 'true'
                
                # Update parameters from frontend if provided
                logger.info("Updating search parameters from frontend")
                search_params.update_from_frontend(
                    fine_grained_similarity_threshold=fine_grained_similarity_threshold,
                    fine_grained_content_weight=fine_grained_content_weight,
                    fine_grained_result_percentage=fine_grained_result_percentage,
                    fine_grained_max_results=fine_grained_max_results,
                    contextual_similarity_threshold=contextual_similarity_threshold,
                    contextual_content_weight=contextual_content_weight,
                    contextual_result_percentage=contextual_result_percentage,
                    contextual_max_results=contextual_max_results,
                    overview_similarity_threshold=overview_similarity_threshold,
                    overview_content_weight=overview_content_weight,
                    overview_result_percentage=overview_result_percentage,
                    overview_max_results=overview_max_results,
                    preset=preset
                )
                
                # Print to rich console
                console.print("[bold yellow]Search Parameters:[/bold yellow]")
                params_table = Table(show_header=True, header_style="bold magenta")
                params_table.add_column("Tier")
                params_table.add_column("Similarity Threshold")
                params_table.add_column("Content Weight")
                params_table.add_column("Max Results")
                
                # Add rows for each tier
                params_table.add_row(
                    "Fine-Grained", 
                    f"{search_params.get_params('fine_grained')['similarity_threshold']:.2f}",
                    f"{search_params.get_params('fine_grained')['content_weight']:.2f}",
                    f"{search_params.get_params('fine_grained')['max_results']}"
                )
                params_table.add_row(
                    "Contextual", 
                    f"{search_params.get_params('contextual')['similarity_threshold']:.2f}",
                    f"{search_params.get_params('contextual')['content_weight']:.2f}",
                    f"{search_params.get_params('contextual')['max_results']}"
                )
                params_table.add_row(
                    "Overview", 
                    f"{search_params.get_params('overview')['similarity_threshold']:.2f}",
                    f"{search_params.get_params('overview')['content_weight']:.2f}",
                    f"{search_params.get_params('overview')['max_results']}"
                )
                console.print(params_table)
                
                logger.info(f"Search Query: {query}")
                logger.info(f"Search Parameters:")
                logger.info(f"Fine_Grained: threshold={search_params.get_params('fine_grained')['similarity_threshold']:.2f}, "
                            f"content_weight={search_params.get_params('fine_grained')['content_weight']:.2f}, "
                            f"max_results={search_params.get_params('fine_grained')['max_results']}")
                logger.info(f"Contextual: threshold={search_params.get_params('contextual')['similarity_threshold']:.2f}, "
                            f"content_weight={search_params.get_params('contextual')['content_weight']:.2f}, "
                            f"max_results={search_params.get_params('contextual')['max_results']}")
                logger.info(f"Overview: threshold={search_params.get_params('overview')['similarity_threshold']:.2f}, "
                            f"content_weight={search_params.get_params('overview')['content_weight']:.2f}, "
                            f"max_results={search_params.get_params('overview')['max_results']}")
            except Exception as e:
                logger.error(f"Error initializing search parameters: {str(e)}")
                console.print(f"[bold red]Error initializing search parameters:[/bold red] {str(e)}")
                yield json_to_sse_structured({"type": "error", "data": f"Error initializing search parameters: {str(e)}"})
                yield json_to_sse_structured({"type": "complete", "data": "Search failed"})
                return
            
            # Start search process
            yield json_to_sse_structured({"type": "log", "data": f"Starting search for: {query}"})
            
            # Execute the search with the configured parameters
            all_results = []
            
            # Create progress tracking with rich library
            progress_steps = ["Searching fine-grained content...", 
                             "Searching contextual content...", 
                             "Searching overview content...",
                             "Formatting results..."]
            
            # Use rich for terminal progress display
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[bold]{task.percentage:.0f}%"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                search_task = progress.add_task("[bold blue]Searching...", total=4)
                
                # Fine-grained search
                progress.update(search_task, advance=0, description=progress_steps[0])
                yield json_to_sse_structured({"type": "log", "data": progress_steps[0]})
                try:
                    fine_grained_results = await search_fine_grained(
                        query, 
                        search_params.get_params('fine_grained')['similarity_threshold'],
                        search_params.get_params('fine_grained')['content_weight'],
                        search_params.get_params('fine_grained')['max_results']
                    )
                    all_results.extend(fine_grained_results)
                    progress.update(search_task, advance=1)
                    console.print(f"[green]Found {len(fine_grained_results)} fine-grained results[/green]")
                    yield json_to_sse_structured({"type": "log", "data": f"Found {len(fine_grained_results)} fine-grained results"})
                except Exception as e:
                    logger.error(f"Error in fine-grained search: {str(e)}")
                    console.print(f"[bold red]Error in fine-grained search:[/bold red] {str(e)}")
                    yield json_to_sse_structured({"type": "error", "data": f"Error in fine-grained search: {str(e)}"})
                    progress.update(search_task, advance=1)
                
                # Contextual search
                progress.update(search_task, description=progress_steps[1])
                yield json_to_sse_structured({"type": "log", "data": progress_steps[1]})
                try:
                    contextual_results = await search_contextual(
                        query,
                        search_params.get_params('contextual')['similarity_threshold'],
                        search_params.get_params('contextual')['content_weight'],
                        search_params.get_params('contextual')['max_results']
                    )
                    all_results.extend(contextual_results)
                    progress.update(search_task, advance=1)
                    console.print(f"[green]Found {len(contextual_results)} contextual results[/green]")
                    yield json_to_sse_structured({"type": "log", "data": f"Found {len(contextual_results)} contextual results"})
                except Exception as e:
                    logger.error(f"Error in contextual search: {str(e)}")
                    console.print(f"[bold red]Error in contextual search:[/bold red] {str(e)}")
                    yield json_to_sse_structured({"type": "error", "data": f"Error in contextual search: {str(e)}"})
                    progress.update(search_task, advance=1)
                
                # Overview search
                progress.update(search_task, description=progress_steps[2])
                yield json_to_sse_structured({"type": "log", "data": progress_steps[2]})
                try:
                    overview_results = await search_overview(
                        query,
                        search_params.get_params('overview')['similarity_threshold'],
                        search_params.get_params('overview')['content_weight'],
                        search_params.get_params('overview')['max_results']
                    )
                    all_results.extend(overview_results)
                    progress.update(search_task, advance=1)
                    console.print(f"[green]Found {len(overview_results)} overview results[/green]")
                    yield json_to_sse_structured({"type": "log", "data": f"Found {len(overview_results)} overview results"})
                except Exception as e:
                    logger.error(f"Error in overview search: {str(e)}")
                    console.print(f"[bold red]Error in overview search:[/bold red] {str(e)}")
                    yield json_to_sse_structured({"type": "error", "data": f"Error in overview search: {str(e)}"})
                    progress.update(search_task, advance=1)
                
                # Format results
                progress.update(search_task, description=progress_steps[3])
                yield json_to_sse_structured({"type": "log", "data": progress_steps[3]})
            
            # Remove duplicates based on content_id, start_time, end_time, and content hash
            unique_results = []
            result_keys = set()
            
            for result in all_results:
                try:
                    key = f"{result.content_id}_{result.start_time}_{result.end_time}_{hash(result.content)}"
                    if key not in result_keys:
                        result_keys.add(key)
                        unique_results.append(result)
                except Exception as e:
                    logger.error(f"Error processing result: {str(e)}")
                    console.print(f"[red]Error processing result: {str(e)}[/red]")
                    continue
            
            # Sort by similarity
            sorted_results = sorted(unique_results, key=lambda x: x.similarity, reverse=True)
            
            # Display results in terminal using rich
            console.print(f"\n[bold green]✓ Found {len(sorted_results)} results[/bold green]")
            
            # Show top results in terminal
            if sorted_results:
                console.print("\n[bold yellow]Top Results:[/bold yellow]")
                results_table = Table(show_header=True, header_style="bold magenta")
                results_table.add_column("Title")
                results_table.add_column("Similarity")
                results_table.add_column("Content Preview")
                results_table.add_column("Source")
                
                for i, result in enumerate(sorted_results[:5], 1):
                    title = result.title if result.title else "No title"
                    content_preview = result.content[:100] + "..." if len(result.content) > 100 else result.content
                    results_table.add_row(
                        title,
                        f"{result.similarity:.3f}",
                        content_preview,
                        result.source
                    )
                
                console.print(results_table)
            
            # Convert to dictionary format and send
            result_dicts = [result.to_dict() for result in sorted_results]
            yield json_to_sse_structured({"type": "results", "data": {"sections": result_dicts}})
            
            # Send operation details
            operation_details = {
                "type": "Advanced Hybrid Search",
                "parameters": {
                    "query": query,
                    "preset": preset,
                    "fine_grained": search_params.get_params('fine_grained'),
                    "contextual": search_params.get_params('contextual'),
                    "overview": search_params.get_params('overview')
                },
                "resultsCount": len(sorted_results)
            }
            yield json_to_sse_structured({"type": "operation_details", "data": operation_details})
            
            # Run analysis if requested
            if run_analysis and sorted_results:
                console.print("\n[bold yellow]Running AI analysis on results...[/bold yellow]")
                yield json_to_sse_structured({"type": "log", "data": "Running AI analysis on results..."})
                
                try:
                    # Prepare results for analysis
                    results_for_analysis = sorted_results[:min(20, len(sorted_results))]
                    total_content_length = sum(len(r.content) for r in results_for_analysis)
                    
                    # Generate token estimates
                    openai_input_tokens = token_counter.count_embedding_tokens("\n\n".join([r.content for r in results_for_analysis]))
                    groq_input_tokens = openai_input_tokens  # Similar token count for both models
                    
                    # Estimate output tokens (typically 10-20% of input)
                    openai_output_estimate = int(openai_input_tokens * 0.15)
                    groq_output_estimate = int(groq_input_tokens * 0.15)
                    
                    # Display token estimates in terminal
                    token_table = Table(show_header=True, header_style="bold magenta")
                    token_table.add_column("Model")
                    token_table.add_column("Input Tokens")
                    token_table.add_column("Output Tokens (est.)")
                    token_table.add_column("Total")
                    
                    token_table.add_row(
                        "OpenAI",
                        str(openai_input_tokens),
                        str(openai_output_estimate),
                        str(openai_input_tokens + openai_output_estimate)
                    )
                    
                    token_table.add_row(
                        "Groq",
                        str(groq_input_tokens),
                        str(groq_output_estimate),
                        str(groq_input_tokens + groq_output_estimate)
                    )
                    
                    console.print(token_table)
                    
                    # Send analysis preview
                    analysis_preview = {
                        "result_count": len(results_for_analysis),
                        "total_content_length": total_content_length,
                        "results_for_analysis": [r.to_dict() for r in results_for_analysis[:5]],  # Just preview top 5
                        "token_estimates": {
                            "openai": {
                                "input": openai_input_tokens,
                                "output": openai_output_estimate,
                                "total": openai_input_tokens + openai_output_estimate
                            },
                            "groq": {
                                "input": groq_input_tokens,
                                "output": groq_output_estimate,
                                "total": groq_input_tokens + groq_output_estimate
                            }
                        }
                    }
                    yield json_to_sse_structured({"type": "analysis_preview", "data": analysis_preview})
                    
                    # Only run OpenAI analysis to save tokens
                    console.print("\n[bold]Generating OpenAI analysis...[/bold]")
                    openai_analysis = analyze_search_results(results_for_analysis, provider='openai')
                    console.print(f"\n[bold cyan]OpenAI Analysis:[/bold cyan]\n{openai_analysis}\n")
                    yield json_to_sse_structured({"type": "analysis_openai", "data": openai_analysis})
                    
                    # Log token usage
                    token_stats = token_counter.get_stats()
                    console.print(f"\n[bold green]Token Usage:[/bold green]")
                    console.print(f"Embeddings: {token_stats.get('embedding_tokens', 0)}")
                    console.print(f"Generation: {token_stats.get('generation_tokens', 0)}")
                    console.print(f"Total: {token_stats.get('total_tokens', 0)}")
                    yield json_to_sse_structured({"type": "tokens", "data": token_stats})
                except Exception as e:
                    logger.error(f"Error running analysis: {str(e)}")
                    console.print(f"[bold red]Error running analysis:[/bold red] {str(e)}")
                    yield json_to_sse_structured({"type": "error", "data": f"Error running analysis: {str(e)}"})
            
            # Complete the stream
            console.print("\n[bold green]Search completed![/bold green]")
            yield json_to_sse_structured({"type": "complete", "data": "Search completed"})
            
        except Exception as e:
            logger.error(f"Error in search stream: {str(e)}")
            console.print(f"[bold red]Error in search stream:[/bold red] {str(e)}")
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(error_traceback)
            console.print(f"[red]{error_traceback}[/red]")
            yield json_to_sse_structured({"type": "error", "data": f"Search error: {str(e)}"})
            yield json_to_sse_structured({"type": "complete", "data": "Search failed"})
    
    # Use the cors helper to ensure proper headers
    return await cors_event_source_response(event_generator(), request)

@app.get("/health")
async def health_check():
    """Simple health check endpoint without any queue operations."""
    custom_logger.info("Health check endpoint called")
    return {"status": "healthy", "message": "Backend server is running", "timestamp": str(datetime.now())}

