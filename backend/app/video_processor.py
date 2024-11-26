import os
import yt_dlp
import asyncio
from .file_utils import ensure_directory_exists

async def extract_video_info(youtube_url):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = await asyncio.to_thread(ydl.extract_info, youtube_url, download=False)
    return {
        'title': info_dict.get('title', None),
        'watch_url': info_dict.get('webpage_url', None),
        'video_id': info_dict.get('id', None)
    }

async def download_audio(youtube_url, output_path):
    await ensure_directory_exists(os.path.dirname(output_path))
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'keepvideo': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await asyncio.to_thread(ydl.download, [youtube_url])
    
    if os.path.exists(output_path):
        return output_path
    else:
        raise FileNotFoundError(f"Downloaded audio file not found at {output_path}")