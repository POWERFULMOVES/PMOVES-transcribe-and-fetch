import os
import logging
import asyncio
from typing import List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from pydantic import BaseModel, validator
from .fetch_content import fetch_content_from_url, generate_unique_filename, save_text_to_markdown, convert_markdown_to_pdf
from .transcribe import process_video
import re

class VideoRequest(BaseModel):
    youtube_video_url: str
    obsidian_dir: str

    @validator('youtube_video_url')
    def validate_youtube_url(cls, v):
        youtube_regex = r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$'
        if not re.match(youtube_regex, v):
            raise ValueError('Invalid YouTube URL')
        return v

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

status_updates = asyncio.Queue()
transcription_updates = asyncio.Queue()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the YouTube Transcriber & Content Fetcher API!"}

@app.get("/fetch-content/")
async def fetch_content(url: str):
    try:
        content = await asyncio.to_thread(fetch_content_from_url, url)
        markdown_filename = generate_unique_filename(url, 'md')
        pdf_filename = generate_unique_filename(url, 'pdf')
        markdown_path = os.path.join(os.getcwd(), markdown_filename)
        pdf_path = os.path.join(os.getcwd(), pdf_filename)
        await asyncio.to_thread(save_text_to_markdown, content, markdown_path)
        await asyncio.to_thread(convert_markdown_to_pdf, markdown_path, pdf_path)
        return {"markdown_path": markdown_path, "pdf_path": pdf_path, "markdown_content": content}
    except Exception as e:
        logger.error(f"Error fetching content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-video/")
async def transcribe_video(request: VideoRequest, background_tasks: BackgroundTasks):
    await status_updates.put("Video processing started")
    background_tasks.add_task(process_video_task, request.youtube_video_url, request.obsidian_dir)
    return {"message": "Video processing started"}

@app.get("/status/")
async def get_status():
    async def event_generator():
        while True:
            update = await status_updates.get()
            yield f"data: {update}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/transcription-updates/")
async def get_transcription_updates():
    async def event_generator():
        while True:
            update = await transcription_updates.get()
            yield f"data: {update}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def process_video_task(youtube_video_url: str, obsidian_dir: str):
    try:
        result = await process_video(youtube_video_url, obsidian_dir, status_updates, transcription_updates)
        await status_updates.put("Video processed successfully.")
        await transcription_updates.put(result['transcription_text'])
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await status_updates.put(f"Error processing video: {str(e)}")
        await transcription_updates.put(f"Error processing video: {str(e)}")