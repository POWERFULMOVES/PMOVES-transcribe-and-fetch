from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, validator
import os
import tempfile
import aiofiles
import json
from datetime import datetime
import asyncio

from ..pmoves_upserter import MarkdownUpserter
from ..db.database import get_client

router = APIRouter(tags=["Content Upserter"])

# Models for API requests
class FetchRequest(BaseModel):
    url: HttpUrl
    metadata: Optional[Dict[str, Any]] = None

class ContentMetadata(BaseModel):
    title: Optional[str] = None
    source_url: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    duration: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            try:
                # Try to parse the date and format it consistently
                datetime.fromisoformat(v.replace('Z', '+00:00'))
                return v
            except ValueError:
                pass
        return v

async def process_file_in_background(file_path: str, content_type: str, metadata: Dict[str, Any], upserter: MarkdownUpserter):
    """Process files in the background after the API has responded"""
    try:
        if content_type in ['video', 'audio']:
            if content_type == 'video':
                await upserter.process_video(file_path, metadata)
            else:
                await upserter.process_audio(file_path, metadata)
        else:
            # For text-based content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                await upserter.process_content(content, file_path=file_path, metadata=metadata)
    except Exception as e:
        print(f"Error in background processing: {str(e)}")


@router.post("/upsert/fetch", response_model=Dict[str, Any])
async def upsert_from_fetch(fetch_request: FetchRequest):
    """
    Fetch content from a URL and upsert it into the database
    """
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(str(fetch_request.url), follow_redirects=True)
            response.raise_for_status()
            
            # Create upserter
            upserter = MarkdownUpserter()
            
            # Process the content
            content = response.text
            result = await upserter.process_content(
                content=content,
                url=str(fetch_request.url),
                metadata=fetch_request.metadata
            )
            
            return {
                "status": "success",
                "message": f"Successfully processed content from {fetch_request.url}",
                "result": result
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing fetch request: {str(e)}")

@router.post("/upsert/file", response_model=Dict[str, Any])
async def upsert_from_file(
    file: UploadFile = File(...),
    content_type: Optional[str] = Form(None),
    metadata_json: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upsert content from an uploaded file
    """
    try:
        # Parse metadata if provided
        metadata = json.loads(metadata_json) if metadata_json else {}
        
        # Create upserter
        upserter = MarkdownUpserter()
        
        # Handle the file based on type
        filename = file.filename
        
        # For binary files (video/audio), save to temp location and process
        if content_type in ['video', 'audio'] or any(filename.lower().endswith(ext) for ext in [
            '.mp4', '.avi', '.mov', '.mkv', '.webm',  # video
            '.mp3', '.wav', '.ogg', '.flac', '.m4a'   # audio
        ]):
            # Create temp file
            suffix = os.path.splitext(filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                # Save uploaded file to temp location
                content = await file.read()
                temp_file.write(content)
                file_path = temp_file.name
            
            # Infer content type if not provided
            if not content_type:
                if any(filename.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
                    content_type = 'video'
                else:
                    content_type = 'audio'
            
            # Process in background and return early
            background_tasks.add_task(
                process_file_in_background, file_path, content_type, metadata, upserter
            )
            
            return {
                "status": "processing",
                "message": f"Processing {content_type} file in background",
                "file": filename,
                "content_type": content_type
            }
            
        # For text-based content, process immediately
        else:
            content = await file.read()
            try:
                # Try to decode as text
                text_content = content.decode('utf-8')
                
                # Process the content
                result = await upserter.process_content(
                    content=text_content,
                    file_path=filename,
                    metadata=metadata
                )
                
                return {
                    "status": "success",
                    "message": f"Successfully processed file {filename}",
                    "result": result
                }
            except UnicodeDecodeError:
                # If not text, treat as binary
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                    temp_file.write(content)
                    file_path = temp_file.name
                
                # Process in background
                background_tasks.add_task(
                    process_file_in_background, file_path, "binary", metadata, upserter
                )
                
                return {
                    "status": "processing",
                    "message": "Processing binary file in background",
                    "file": filename
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/upsert/transcript", response_model=Dict[str, Any])
async def upsert_transcript(
    file: UploadFile = File(...),
    force_overwrite: bool = Form(False)
):
    """
    Upsert a transcript from an uploaded markdown file
    """
    try:
        # Create upserter
        upserter = MarkdownUpserter()
        
        # Process the file
        content = await file.read()
        text_content = content.decode('utf-8')
        
        result = await upserter.upsert_transcript(
            markdown_content=text_content,
            filename=file.filename,
            force_overwrite=force_overwrite
        )
        
        return {
            "status": "success",
            "message": f"Successfully processed transcript {file.filename}",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing transcript: {str(e)}") 