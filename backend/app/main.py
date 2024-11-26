import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse, JSONResponse
try:
    from sse_starlette.sse import EventSourceResponse
except ImportError:
    from starlette.responses import StreamingResponse as EventSourceResponse
    print("Warning: sse_starlette not found. Using StreamingResponse as a fallback.")
from pydantic import BaseModel, validator, ValidationError
from .fetch_content import (
    fetch_content_from_url, 
    generate_unique_filename, 
    save_text_to_markdown, 
    sanitize_filename
)
from .transcribe import process_video, VideoProcessRequest, get_optimal_device
import re
from .config import DEFAULT_OUTPUT_FOLDER
import shutil
from .folder_manager import folder_manager
from .utils import (
    convert_markdown_to_pdf, 
    save_text_to_markdown, 
    clean_filename
)
import json
from .video_processor import extract_video_info
import torch
import urllib.parse
import aiofiles
from fastapi.responses import FileResponse
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class FolderUpdate(BaseModel):
    old_path: str
    new_path: str

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Sent response: {response.status_code}")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Be specific about the frontend origin
    allow_credentials=False,  # Change this to False since we're not using credentials
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize the queues
status_updates = asyncio.Queue()
transcription_updates = asyncio.Queue()

@app.get("/")
async def root():
    return {"message": "Backend is running"}

@app.get("/fetch-content/")
async def fetch_content(url: str, json_response: bool = False, timeout: Optional[int] = None, target_selector: Optional[str] = None):
    try:
        content = await fetch_content_from_url(url, json_response, timeout, target_selector)
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

        # Properly await the async file operations
        await save_text_to_markdown(content, markdown_path)
        logger.info(f"Markdown saved successfully to: {markdown_path}")
        
        await convert_markdown_to_pdf(markdown_path, pdf_path)
        logger.info(f"PDF converted successfully to: {pdf_path}")

        return {
            "markdown_path": markdown_path,
            "pdf_path": pdf_path,
            "markdown_content": content
        }

    except Exception as e:
        logger.error(f"Error in fetch_content: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching or saving content: {str(e)}")

@app.get("/get-audio-file")
async def get_audio_file(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path)

@app.post("/process-video/")
async def process_video_endpoint(request: VideoRequest):
    try:
        # Log the request data
        logger.info(f"Processing video request: {request.dict()}")
        
        if not hasattr(app.state, 'processing_lock'):
            app.state.processing_lock = asyncio.Lock()
        
        async with app.state.processing_lock:
            try:
                # Validate the YouTube URL
                if not re.match(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$', request.youtube_video_url):
                    raise HTTPException(status_code=400, detail="Invalid YouTube URL")

                # Validate directories exist
                if not os.path.exists(request.obsidian_dir):
                    raise HTTPException(status_code=400, detail="Obsidian directory does not exist")

                if not os.path.exists(request.output_folder):
                    os.makedirs(request.output_folder, exist_ok=True)
                    logger.info(f"Created output folder: {request.output_folder}")

                # Start the background task
                task = asyncio.create_task(process_video_task(
                    youtube_video_url=request.youtube_video_url,
                    obsidian_dir=request.obsidian_dir,
                    output_folder=request.output_folder,
                    status_updates=status_updates,
                    transcription_updates=transcription_updates,
                    use_groq=request.use_groq,
                    transcription_model=request.transcription_model
                ))

                return {
                    "status": "started",
                    "message": "Video processing started"
                }

            except Exception as e:
                error_msg = f"Error processing video: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise HTTPException(status_code=500, detail=error_msg)

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-sse")
async def test_sse():
    async def event_generator():
        try:
            # Simple text message
            yield "data: {\"type\": \"status\", \"content\": \"SSE connection test started\"}\n\n"
            await asyncio.sleep(0.5)
            yield "data: {\"type\": \"status\", \"content\": \"SSE connection successful\"}\n\n"
        except Exception as e:
            logger.error(f"Error in test SSE: {str(e)}")
            yield f"data: {{\"type\": \"error\", \"content\": \"{str(e)}\"}}\n\n"
    
    return EventSourceResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@app.get("/combined-updates")
async def get_combined_updates():
    async def event_generator():
        try:
            yield f"data: {json.dumps({'type': 'status', 'content': 'Starting transcription updates'})}\n\n"
            
            while True:
                try:
                    # Process both queues simultaneously
                    status_update = None
                    transcription_update = None
                    
                    if not status_updates.empty():
                        status_update = await status_updates.get()
                    if not transcription_updates.empty():
                        transcription_update = await transcription_updates.get()
                    
                    # Send updates immediately if available
                    if status_update:
                        if isinstance(status_update, str):
                            try:
                                parsed = json.loads(status_update)
                                yield f"data: {json.dumps(parsed)}\n\n"
                            except json.JSONDecodeError:
                                yield f"data: {json.dumps({'type': 'status', 'content': status_update})}\n\n"
                        else:
                            yield f"data: {json.dumps(status_update)}\n\n"
                    
                    if transcription_update:
                        if isinstance(transcription_update, str):
                            try:
                                parsed = json.loads(transcription_update)
                                yield f"data: {json.dumps(parsed)}\n\n"
                            except json.JSONDecodeError:
                                yield f"data: {json.dumps({'type': 'transcription_segment', 'content': transcription_update})}\n\n"
                        else:
                            yield f"data: {json.dumps(transcription_update)}\n\n"
                    
                    # Only sleep if both queues were empty
                    if not status_update and not transcription_update:
                        await asyncio.sleep(0.01)  # Reduced from 0.1 to 0.01 seconds
                    
                except Exception as e:
                    logger.error(f"Error processing update: {str(e)}")
                    yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
                    
        except Exception as e:
            logger.error(f"Error in event stream: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            
    return EventSourceResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no"
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    # Close any open connections or perform cleanup
    if 'eventSource' in globals():
        eventSource.close()

async def process_video_task(youtube_video_url: str, obsidian_dir: str, output_folder: str,
                              status_updates: asyncio.Queue, transcription_updates: asyncio.Queue,
                              use_groq: bool = False, transcription_model: str = "faster-whisper"):
    try:
        logger.info("Starting video processing task")
        await status_updates.put(json.dumps({
            "type": "status",
            "content": "Starting video processing..."
        }))

        # Call process_video with positional arguments in the correct order
        result = await process_video(
            youtube_video_url,
            obsidian_dir,
            status_updates,
            transcription_updates,
            output_folder,
            use_groq,
            transcription_model
        )
        
        logger.info("Video processing completed successfully")
        return result
            
    except Exception as e:
        error_msg = f"Error processing video: {str(e)}"
        logger.error(error_msg)
        await status_updates.put(json.dumps({
            "type": "status",
            "content": error_msg
        }))
        raise

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )

@app.get("/device-info")
async def get_device_info():
    device, compute_type = get_optimal_device()
    return {
        "device": device,
        "compute_type": compute_type,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "groq_api_key_configured": bool(os.getenv('GROQ_API_KEY'))
    }

# Define clean_filename function here temporarily
def clean_filename(title):
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'__+', '_', title)
    return title

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "queues": {
            "status_updates": not status_updates.empty(),
            "transcription_updates": not transcription_updates.empty()
        }
    }

@app.get("/fetch-markdown")
async def fetch_markdown(path: str):
    try:
        # URL decode the path if needed
        decoded_path = urllib.parse.unquote(path)
        logger.info(f"Attempting to read markdown from: {decoded_path}")
        
        if not os.path.exists(decoded_path):
            logger.error(f"File not found: {decoded_path}")
            raise HTTPException(status_code=404, detail="File not found")
            
        # Use aiofiles for async file reading
        async with aiofiles.open(decoded_path, 'r', encoding='utf-8') as file:
            content = await file.read()
            logger.info(f"Successfully read markdown file: {decoded_path}")
            return {"content": content}
            
    except Exception as e:
        logger.error(f"Error reading markdown file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reading markdown file: {str(e)}")

@app.get("/view-pdf")
async def view_pdf(path: str):
    """Serve PDF file for viewing"""
    try:
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="PDF file not found")
            
        return FileResponse(
            path,
            media_type="application/pdf",
            filename=os.path.basename(path)
        )
    except Exception as e:
        logger.error(f"Error serving PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-pdf")
async def download_pdf(path: str):
    """Download PDF file"""
    try:
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="PDF file not found")
            
        return FileResponse(
            path,
            media_type="application/pdf",
            filename=os.path.basename(path),
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(path)}"}
        )
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


