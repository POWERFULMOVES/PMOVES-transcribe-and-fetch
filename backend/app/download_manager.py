import asyncio
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class DownloadManager:
    def __init__(self):
        self.downloads: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()

    async def start_download(self, url: str) -> str:
        """Start a new download and return its ID"""
        async with self._lock:
            download_id = url  # Using URL as ID for simplicity
            self.downloads[download_id] = {
                "url": url,
                "status": "pending",
                "progress": 0,
                "error": None
            }
            return download_id

    async def update_status(self, download_id: str, status: str, progress: Optional[float] = None, error: Optional[str] = None):
        """Update the status of a download"""
        async with self._lock:
            if download_id in self.downloads:
                self.downloads[download_id].update({
                    "status": status,
                    **({"progress": progress} if progress is not None else {}),
                    **({"error": error} if error is not None else {})
                })
                logger.info(f"Download {download_id} updated: status={status}, progress={progress}, error={error}")

    async def get_status(self, download_id: str) -> Optional[Dict]:
        """Get the status of a download"""
        async with self._lock:
            return self.downloads.get(download_id)

    async def get_all_statuses(self) -> Dict[str, Dict]:
        """Get status of all downloads"""
        async with self._lock:
            return self.downloads.copy()

    async def remove_download(self, download_id: str):
        """Remove a download from tracking"""
        async with self._lock:
            self.downloads.pop(download_id, None)
