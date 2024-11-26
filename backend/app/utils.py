import os

import re

import asyncio

import yt_dlp

import pandas as pd

from datetime import datetime

import markdown2

import pdfkit

import aiofiles

import logging

import json

from typing import Union



logger = logging.getLogger(__name__)



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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        await asyncio.to_thread(ydl.download, [youtube_url])

    

    if os.path.exists(output_path):

        return output_path

    else:

        raise FileNotFoundError(f"Downloaded audio file not found at {output_path}")



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



async def save_text_to_markdown(content: Union[str, dict], output_path: str) -> None:

    """

    Save content to a markdown file, handling both string and JSON responses.

    

    Args:

        content: Either a string of markdown text or a JSON response from Jina Reader

        output_path: Path where to save the markdown file

    """

    try:

        # Convert content to markdown string

        if isinstance(content, dict):

            # Start with the main content

            text_parts = []

            

            # Add title if available

            if content.get('title'):

                text_parts.append(f"# {content['title']}\n")

            

            # Add main content

            if 'content' in content:

                text_parts.append(content['content'])

            

            # Add links section if available

            if content.get('links'):

                text_parts.append("\n## Links Found\n")

                for link in content['links']:

                    text_parts.append(f"- [{link.get('text', link['url'])}]({link['url']})")

            

            text_content = "\n".join(text_parts)

        else:

            text_content = str(content)

        

        # Ensure the directory exists

        directory = os.path.dirname(output_path)

        if not os.path.exists(directory):

            os.makedirs(directory)

            logger.info(f"Created directory: {directory}")



        # Use async file writing

        async with aiofiles.open(output_path, 'w', encoding='utf-8') as file:

            await file.write(text_content)

            

        logger.info(f"Markdown file saved successfully: {output_path}")

    except Exception as e:

        logger.error(f"Error saving markdown file: {str(e)}")

        raise



async def convert_markdown_to_pdf(markdown_path: str, pdf_path: str) -> None:

    """

    Convert markdown to PDF with proper wkhtmltopdf configuration

    """

    try:

        # Configure pdfkit with wkhtmltopdf path

        from .config import WKHTMLTOPDF_PATH

        config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

        

        # Read markdown content

        async with aiofiles.open(markdown_path, 'r', encoding='utf-8') as file:

            markdown_content = await file.read()



        # Convert markdown to HTML using markdown2

        html_content = markdown2.markdown(

            markdown_content,

            extras=['tables', 'fenced-code-blocks']

        )



        # Configure PDF options

        options = {

            'encoding': 'UTF-8',

            'enable-local-file-access': None,

            'margin-top': '20mm',

            'margin-right': '20mm',

            'margin-bottom': '20mm',

            'margin-left': '20mm',

            'quiet': '',

            'disable-smart-shrinking': '',

            'no-background': '',

            'dpi': '300'

        }



        # Add HTML styling

        html_doc = f"""

        <!DOCTYPE html>

        <html>

        <head>

            <meta charset="UTF-8">

            <style>

                body {{

                    font-family: Arial, sans-serif;

                    line-height: 1.6;

                    margin: 20px;

                }}

                table {{

                    border-collapse: collapse;

                    width: 100%;

                    margin: 15px 0;

                    font-size: 14px;

                }}

                th, td {{

                    border: 1px solid #ddd;

                    padding: 8px;

                    text-align: left;

                    word-wrap: break-word;

                }}

                th {{

                    background-color: #f4f4f4;

                }}

                a {{

                    color: #0066cc;

                    text-decoration: none;

                }}

                pre {{

                    background-color: #f8f8f8;

                    padding: 12px;

                    border-radius: 4px;

                    overflow-x: auto;

                }}

                code {{

                    font-family: 'Courier New', Courier, monospace;

                }}

                h1, h2, h3 {{

                    color: #333;

                    margin-top: 20px;

                }}

            </style>

        </head>

        <body>

            {html_content}

        </body>

        </html>

        """



        # Use pdfkit to convert HTML to PDF with configuration

        logger.info(f"Converting markdown to PDF: {markdown_path} -> {pdf_path}")

        await asyncio.to_thread(

            pdfkit.from_string,

            html_doc,

            pdf_path,

            options=options,

            configuration=config

        )

        logger.info(f"Successfully created PDF: {pdf_path}")

    except ImportError as e:

        logger.error(f"Missing required package: {str(e)}")

        logger.error("Please install required packages: pip install markdown2 pdfkit")

        raise

    except Exception as e:

        logger.error(f"Error converting markdown to PDF: {str(e)}")

        raise



def format_timestamp(seconds):

    minutes, seconds = divmod(seconds, 60)

    hours, minutes = divmod(minutes, 60)

    return f"{int(hours):02d}:{int(minutes):02d}:{seconds:.2f}"
