import os
import re
import asyncio
import yt_dlp as youtube_dl
import pandas as pd
import markdown2
import pdfkit
from datetime import datetime

async def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def clean_filename(title):
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'__+', '_', title)
    return title

async def download_audio(youtube_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'keepvideo': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        await asyncio.to_thread(ydl.download, [youtube_url])

async def save_segments_to_csv(segments, output_path):
    df = pd.DataFrame(segments)
    await asyncio.to_thread(df.to_csv, output_path, index=False)

async def save_segments_to_excel(segments, output_path):
    df = pd.DataFrame(segments)
    await asyncio.to_thread(df.to_excel, output_path, sheet_name='Transcription', index=False)

def format_as_hyperlink(value):
    return f'=HYPERLINK("{value}", "{value}")'

def generate_unique_filename(base_name, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"

async def save_text_to_markdown(text, output_path):
    async with asyncio.Lock():
        with open(output_path, 'w', encoding='utf-8') as file:
            await asyncio.to_thread(file.write, text)

async def convert_markdown_to_pdf(md_path, pdf_path):
    async with asyncio.Lock():
        with open(md_path, 'r', encoding='utf-8') as file:
            markdown_text = await asyncio.to_thread(file.read)
        html_text = markdown2.markdown(markdown_text)
        config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
        await asyncio.to_thread(pdfkit.from_string, html_text, pdf_path, configuration=config)
