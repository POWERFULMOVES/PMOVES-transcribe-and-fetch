import asyncio
from typing import Dict, Any

class QueueManager:
    def __init__(self):
        self.status_queue = asyncio.Queue()
        self.transcription_queue = asyncio.Queue()
        self.active_transcriptions = set()  # Track active transcription processes
        self._running = False

    async def start(self):
        """Start the queue manager"""
        self._running = True

    async def stop(self):
        """Stop the queue manager"""
        self._running = False
        # Clear queues
        while not self.status_queue.empty():
            await self.status_queue.get()
        while not self.transcription_queue.empty():
            await self.transcription_queue.get()

    async def add_status_update(self, update: Dict[str, Any]):
        """Add a status update to the status queue"""
        if self._running:
            await self.status_queue.put(update)

    async def add_transcription_update(self, update: Dict[str, Any]):
        """Add a transcription update to the transcription queue"""
        if self._running:
            await self.transcription_queue.put(update)

    async def get_status_update(self):
        """Get a status update from the status queue"""
        if self._running:
            return await self.status_queue.get()
        return None

    async def get_transcription_update(self):
        """Get a transcription update from the transcription queue"""
        if self._running:
            return await self.transcription_queue.get()
        return None

    def add_active_transcription(self, video_id: str):
        """Add a video ID to the active transcriptions set"""
        self.active_transcriptions.add(video_id)

    def remove_active_transcription(self, video_id: str):
        """Remove a video ID from the active transcriptions set"""
        if video_id in self.active_transcriptions:
            self.active_transcriptions.remove(video_id)

    def has_active_transcriptions(self) -> bool:
        """Check if there are any active transcriptions"""
        return len(self.active_transcriptions) > 0