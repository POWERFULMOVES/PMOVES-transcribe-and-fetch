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
import traceback

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



async def generate_pdf_from_markdown_string(markdown_content: str, output_pdf_filepath: str) -> bool:
    """
    Generates a PDF from a markdown string.

    Args:
        markdown_content: The markdown content as a string.
        output_pdf_filepath: The full path where the PDF should be saved.

    Returns:
        True if PDF generation was successful, False otherwise.
    """
    logger.info(f"Attempting to generate PDF: {output_pdf_filepath} from markdown string.")
    try:
        # 1. Find wkhtmltopdf
        wkhtmltopdf_path = os.getenv("WKHTMLTOPDF_PATH")
        if not wkhtmltopdf_path or not os.path.isfile(wkhtmltopdf_path):
            common_paths = [
                "/usr/local/bin/wkhtmltopdf",  # Common for macOS/Linux
                "/usr/bin/wkhtmltopdf",        # Common for Linux
                "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe" # Common for Windows
            ]
            for path_option in common_paths:
                if os.path.isfile(path_option):
                    wkhtmltopdf_path = path_option
                    logger.info(f"Found wkhtmltopdf at: {wkhtmltopdf_path}")
                    break
        
        if not wkhtmltopdf_path or not os.path.isfile(wkhtmltopdf_path):
            logger.error("wkhtmltopdf not found. Set WKHTMLTOPDF_PATH env var or install it in a common location.")
            logger.error("Please install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html")
            return False

        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # 2. Convert Markdown to HTML
        html_content = markdown2.markdown(
            markdown_content,
            extras=[
                "tables",
                "fenced-code-blocks",
                "code-friendly",
                "footnotes",
                "header-ids",
                "strike",
                "task_list",
                "wiki-tables"
            ]
        )

        # 3. HTML Wrapper with CSS
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
                    margin: 20mm; /* Added margin directly to body */
                    padding: 0;
                    word-wrap: break-word; /* Ensure long words break */
                }}
                pre, code {{
                    font-family: 'Courier New', Courier, monospace; /* Monospaced font */
                    background-color: #f0f0f0; /* Light grey background */
                    border: 1px solid #ccc; /* Grey border */
                    border-radius: 4px; /* Rounded corners */
                    padding: 0.1em 0.3em; /* Small padding */
                    white-space: pre-wrap; /* Wrap long lines in pre */
                    word-wrap: break-word; /* Break long words in pre/code */
                }}
                pre {{
                    padding: 10px; /* More padding for pre blocks */
                    overflow-x: auto; /* Allow horizontal scroll for wide pre blocks */
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1em 0;
                    border: 1px solid #ddd;
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
                    display: block; /* Avoid extra space below images */
                    margin: 1em 0; /* Add some margin around images */
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
                    page-break-after: avoid; /* Avoid page breaks after headers */
                }}
                ul, ol {{
                    margin-left: 20px;
                    padding-left: 0;
                }}
                li {{
                    margin-bottom: 0.5em;
                }}
                blockquote {{
                    border-left: 4px solid #ccc;
                    padding-left: 10px;
                    margin-left: 0;
                    color: #555;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # 4. Ensure output directory exists
        output_dir = os.path.dirname(output_pdf_filepath)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                logger.info(f"Created directory: {output_dir}")
            except OSError as e:
                logger.error(f"Failed to create directory {output_dir}: {e}\n{traceback.format_exc()}")
                return False
        
        # 5. PDF Generation Options
        options = {
            'encoding': "UTF-8",
            'enable-local-file-access': None, # Allow access to local files if needed for images, etc.
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'page-size': 'A4',
            'disable-smart-shrinking': None, # Helps with consistent rendering
            'load-error-handling': 'ignore', # Skip content that fails to load
            'load-media-error-handling': 'ignore',
            'quiet': '' # Suppress wkhtmltopdf output unless error
        }

        # 6. Generate PDF (asynchronously)
        success = await asyncio.to_thread(
            pdfkit.from_string,
            html_with_style,
            output_pdf_filepath,
            options=options,
            configuration=config
        )

        if success: # pdfkit.from_string returns True on success with output_path
            logger.info(f"PDF generated successfully: {output_pdf_filepath}")
            return True
        else:
            # This part might not be reached if pdfkit raises an exception on failure,
            # but included for robustness if it returns False for some errors.
            logger.error(f"pdfkit.from_string returned False for {output_pdf_filepath}")
            return False

    except ImportError as e:
        logger.error(f"Missing required package for PDF generation: {e}\n{traceback.format_exc()}")
        logger.error("Please ensure 'markdown2' and 'pdfkit' are installed.")
        return False
    except FileNotFoundError as e: # Specifically for wkhtmltopdf not found by pdfkit if path is invalid
        logger.error(f"File not found during PDF generation (likely wkhtmltopdf issue): {e}\n{traceback.format_exc()}")
        return False
    except OSError as e: # For issues like permissions, disk full, etc.
        logger.error(f"OS error during PDF generation for {output_pdf_filepath}: {e}\n{traceback.format_exc()}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during PDF generation for {output_pdf_filepath}: {e}\n{traceback.format_exc()}")
        # Attempt to create a basic error PDF if main generation fails catastrophically
        try:
            error_html_content = f"<h1>PDF Generation Failed</h1><p>Could not generate PDF from markdown.</p><p>Error: {str(e)}</p><pre>{traceback.format_exc()}</pre>"
            await asyncio.to_thread(
                pdfkit.from_string,
                error_html_content,
                output_pdf_filepath,
                options={'quiet': ''}, # Minimal options for error PDF
                configuration=config if 'config' in locals() else None # Use config if available
            )
            logger.info(f"Error PDF created at {output_pdf_filepath} due to previous failure.")
        except Exception as error_pdf_ex:
            logger.error(f"Failed to create even an error PDF for {output_pdf_filepath}: {error_pdf_ex}\n{traceback.format_exc()}")
        return False


async def convert_markdown_file_to_pdf(markdown_filepath: str, output_pdf_filepath: str) -> bool:
    """
    Converts a markdown file to a PDF file.
    Reads the markdown file and uses generate_pdf_from_markdown_string for conversion.

    Args:
        markdown_filepath: Path to the input markdown file.
        output_pdf_filepath: Path where the output PDF file should be saved.

    Returns:
        True if PDF generation was successful, False otherwise.
    """
    logger.info(f"Attempting to convert markdown file {markdown_filepath} to PDF {output_pdf_filepath}.")
    try:
        async with aiofiles.open(markdown_filepath, 'r', encoding='utf-8') as md_file:
            markdown_content = await md_file.read()
        
        logger.info(f"Successfully read markdown content from {markdown_filepath}.")
        
        return await generate_pdf_from_markdown_string(markdown_content, output_pdf_filepath)

    except FileNotFoundError:
        logger.error(f"Markdown file not found: {markdown_filepath}\n{traceback.format_exc()}")
        return False
    except IOError as e:
        logger.error(f"IOError reading markdown file {markdown_filepath}: {e}\n{traceback.format_exc()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in convert_markdown_file_to_pdf for {markdown_filepath}: {e}\n{traceback.format_exc()}")
        return False
def sanitize_filename(filename: str) -> str:
    """Removes or replaces characters invalid in filenames."""
    # Remove characters invalid in Windows/Linux/macOS filenames
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    # Optionally replace multiple spaces/underscores with a single one
    sanitized = re.sub(r'[_ ]+', '_', sanitized)
    # Optionally remove leading/trailing underscores/spaces
    sanitized = sanitized.strip('_ ')
    # Optionally limit length (example, adjust if needed)
    MAX_FILENAME_LENGTH = 100
    if len(sanitized) > MAX_FILENAME_LENGTH:
         # Ensure extension is preserved if present
         name, ext = os.path.splitext(sanitized)
         if len(ext) < MAX_FILENAME_LENGTH: # Check if ext itself isn't too long
             name = name[:MAX_FILENAME_LENGTH - len(ext) - 1] # Adjust name length
             sanitized = name + ext
         else: # Handle case where extension is very long
             sanitized = sanitized[:MAX_FILENAME_LENGTH]

    return sanitized if sanitized else "untitled" # Ensure not empty


def format_timestamp(seconds):
    """ Convert seconds to HH:MM:SS format without decimal places """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
