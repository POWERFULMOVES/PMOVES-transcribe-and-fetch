"""
Wrapper for process_video that tracks active transcriptions
"""
import asyncio
from typing import Dict, Any, Optional

from .transcribe1 import process_video, extract_video_id
from .queue_manager import QueueManager

# Get the global queue manager instance
from .main import queue_manager

async def process_video_with_tracking(
    youtube_video_url: str,
    obsidian_dir: str,
    status_queue: asyncio.Queue,
    transcription_queue: asyncio.Queue,
    output_folder: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None,
    video_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Wrapper for process_video that tracks active transcriptions
    """
    # If video_id wasn't provided, try to extract it
    if not video_id:
        try:
            video_id = extract_video_id(youtube_video_url)
        except Exception:
            # Use URL as fallback if extraction fails
            video_id = youtube_video_url
    
    try:
        # Add to active transcriptions
        queue_manager.add_active_transcription(video_id)
        
        # Call the original process_video function
        result = await process_video(
            youtube_video_url=youtube_video_url,
            obsidian_dir=obsidian_dir,
            status_queue=status_queue,
            transcription_queue=transcription_queue,
            output_folder=output_folder,
            model_config=model_config
        )
        
        return result
    finally:
        # Always remove from active transcriptions, even if there was an error
        queue_manager.remove_active_transcription(video_id)
        
        # Send a transcription_complete message to the frontend
        await transcription_queue.put('{"type": "transcription_complete", "content": "Transcription process finished."}')
