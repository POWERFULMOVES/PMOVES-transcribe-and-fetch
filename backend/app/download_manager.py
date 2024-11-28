import os
from pathlib import Path
import yt_dlp
from fastapi import HTTPException
from typing import Dict, Any, Optional
import asyncio

class DownloadManager:
    def __init__(self, download_path: str = "downloads"):
        self.download_path = Path(download_path)
        self.download_path.mkdir(exist_ok=True)
        self.status_updates = asyncio.Queue()

    def get_ydl_opts(self, options: Dict[str, Any]) -> dict:
        ydl_opts = {
            'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'writethumbnail': options.get('embedThumbnail', False),
            'embedthumbnail': options.get('embedThumbnail', False),
            'writeinfojson': options.get('embedMetadata', True),
            'addmetadata': options.get('embedMetadata', True),
        }

        # Video format options
        if options.get('format'):
            if options['format'] in ['1080p', '720p', '480p']:
                ydl_opts['format'] = f'bestvideo[height<={options["format"][:-1]}]+bestaudio/best[height<={options["format"][:-1]}]'
            else:
                ydl_opts['format'] = options['format']

        # Audio extraction options
        if options.get('extractAudio'):
            ydl_opts.update({
                'extractaudio': True,
                'audio-format': options.get('audioFormat', 'mp3'),
                'audio-quality': options.get('audioQuality', '192'),
                'keepvideo': options.get('keepVideo', True),
            })

        # Subtitle options
        if options.get('subtitles'):
            ydl_opts.update({
                'writesubtitles': True,
                'subtitleslangs': [options.get('subtitleLanguage', 'en')],
                'writeautomaticsub': True,
            })

        # Playlist options
        if options.get('downloadPlaylist'):
            ydl_opts.update({
                'noplaylist': False,
                'playliststart': int(options.get('playlistStart', 1)),
            })
            if options.get('playlistEnd'):
                ydl_opts['playlistend'] = int(options['playlistEnd'])
        else:
            ydl_opts['noplaylist'] = True

        return ydl_opts

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes')
            downloaded = d.get('downloaded_bytes', 0)
            
            if total:
                progress = (downloaded / total) * 100
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                status = {
                    'type': 'progress',
                    'progress': round(progress, 2),
                    'speed': f"{speed/1024/1024:.1f} MB/s" if speed else "N/A",
                    'eta': f"{eta} seconds" if eta else "N/A",
                    'filename': d.get('filename', ''),
                    'total_size': f"{total/1024/1024:.1f} MB"
                }
            else:
                status = {
                    'type': 'progress',
                    'progress': 0,
                    'speed': "N/A",
                    'eta': "N/A",
                    'filename': d.get('filename', ''),
                    'total_size': "Unknown"
                }
                
            asyncio.create_task(self.status_updates.put(status))
            
        elif d['status'] == 'finished':
            status = {
                'type': 'status',
                'message': 'Download completed, now post-processing...'
            }
            asyncio.create_task(self.status_updates.put(status))

    async def download_video(self, url: str, options: Dict[str, Any] = None):
        if not options:
            options = {}

        try:
            await self.status_updates.put({
                'type': 'status',
                'message': 'Starting download...'
            })

            ydl_opts = self.get_ydl_opts(options)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'video')
                
                await self.status_updates.put({
                    'type': 'complete',
                    'title': video_title,
                    'message': f"Successfully downloaded: {video_title}"
                })
                
                return {
                    "status": "success",
                    "title": video_title,
                    "message": f"Successfully downloaded: {video_title}"
                }
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            await self.status_updates.put({
                'type': 'error',
                'message': error_msg
            })
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
