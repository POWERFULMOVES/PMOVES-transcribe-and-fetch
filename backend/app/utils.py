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
        
        # Check if wkhtmltopdf is installed
        if not os.path.isfile(WKHTMLTOPDF_PATH):
            logger.error(f"Missing wkhtmltopdf at {WKHTMLTOPDF_PATH}")
            logger.error("Please install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html")
            return  # Skip PDF generation but don't raise an exception
            
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
            'margin-left': '20mm'
        }

        # Create HTML wrapper with proper styling
        html_with_style = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Converted Document</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    font-size: 12pt; 
                    line-height: 1.5;
                    margin: 0;
                    padding: 0;
                }}
                pre {{ 
                    background-color: #f5f5f5; 
                    border: 1px solid #ddd; 
                    border-radius: 3px; 
                    padding: 10px; 
                    overflow: auto;
                    font-family: monospace;
                    font-size: 10pt;
                }}
                code {{ 
                    font-family: monospace; 
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 3px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                a {{
                    color: #0066cc;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    margin-top: 1.5em;
                    margin-bottom: 0.5em;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # Run conversion in a thread pool since pdfkit is synchronous
        try:
            await asyncio.to_thread(
                pdfkit.from_string,
                html_with_style,
                pdf_path,
                options=options,
                configuration=config
            )
            logger.info(f"PDF file created successfully: {pdf_path}")
            return True
        except Exception as conversion_error:
            logger.error(f"Error during PDF conversion: {str(conversion_error)}")
            # Create a basic PDF with the error message
            try:
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Error Converting PDF</title></head>
                <body>
                    <h1>Error Converting to PDF</h1>
                    <p>There was an error converting the markdown to PDF. You can still view the markdown content.</p>
                    <p>Error: {str(conversion_error)}</p>
                </body>
                </html>
                """
                await asyncio.to_thread(
                    pdfkit.from_string,
                    error_html,
                    pdf_path,
                    options={'quiet': ''},
                    configuration=config
                )
                logger.info(f"Created error PDF: {pdf_path}")
            except Exception:
                logger.error("Failed to create even an error PDF")
            return False

    except ImportError as e:
        logger.error(f"Missing required package: {str(e)}")
        logger.error("Please install required packages: pip install markdown2 pdfkit")
        return False
    except Exception as e:
        logger.error(f"Critical error converting markdown to PDF: {str(e)}")
        return False



def format_timestamp(seconds):

    minutes, seconds = divmod(seconds, 60)

    hours, minutes = divmod(minutes, 60)

    return f"{int(hours):02d}:{int(minutes):02d}:{seconds:.2f}"
