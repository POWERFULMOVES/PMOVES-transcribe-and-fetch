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

from typing import Union, Optional, List
from pathlib import Path


logger = logging.getLogger(__name__)


async def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def clean_filename(title):
    title = re.sub(r'[\\/*?:"<>|]', "", title)

    title = re.sub(r"\s+", "_", title)

    title = re.sub(r"__+", "_", title)

    return title


async def download_audio(youtube_url, output_path):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "keepvideo": True,
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

    await asyncio.to_thread(
        df.to_excel, output_path, sheet_name="Transcription", index=False
    )


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

            if content.get("title"):
                text_parts.append(f"# {content['title']}\n")

            # Add main content

            if "content" in content:
                text_parts.append(content["content"])

            # Add links section if available

            if content.get("links"):
                text_parts.append("\n## Links Found\n")

                for link in content["links"]:
                    text_parts.append(
                        f"- [{link.get('text', link['url'])}]({link['url']})"
                    )

            text_content = "\n".join(text_parts)

        else:
            text_content = str(content)

        # Ensure the directory exists

        directory = os.path.dirname(output_path)

        if not os.path.exists(directory):
            os.makedirs(directory)

            logger.info(f"Created directory: {directory}")

        # Use async file writing

        async with aiofiles.open(output_path, "w", encoding="utf-8") as file:
            await file.write(text_content)

        logger.info(f"Markdown file saved successfully: {output_path}")

    except Exception as e:
        logger.error(f"Error saving markdown file: {str(e)}")

        raise


async def generate_pdf_from_markdown_string(
    markdown_content: str,
    url: Optional[str] = None,
    title: Optional[str] = None,
    output_pdf_filepath: Optional[str] = None,
) -> Optional[str]:
    """
    Generates a PDF from a markdown string.
    Can dynamically create a filepath if one isn't provided.

    Args:
        markdown_content: The markdown content as a string.
        url: The source URL, used for filename generation if title is absent.
        title: The document title, used for filename generation.
        output_pdf_filepath: The full path where the PDF should be saved. If None,
                             a path is generated in PDF_STORAGE_PATH.

    Returns:
        The relative path to the generated PDF if successful, otherwise None.
    """
    pdf_storage_base_dir = Path(os.getenv("PDF_STORAGE_PATH", "./temp_pdfs")).resolve()
    pdf_storage_base_dir.mkdir(parents=True, exist_ok=True)

    if not output_pdf_filepath:
        if not title and not url:
            logger.error("Cannot generate PDF filename without a title or URL.")
            return None
        # Sanitize filename and create a unique path
        base_name = sanitize_filename(title if title else url)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"{base_name}_{timestamp}.pdf"
        output_pdf_filepath = str(pdf_storage_base_dir / pdf_filename)

    logger.info(
        f"Attempting to generate PDF: {output_pdf_filepath} from markdown string."
    )
    try:
        # 1. Find wkhtmltopdf
        wkhtmltopdf_path = os.getenv("WKHTMLTOPDF_PATH")
        if not wkhtmltopdf_path or not os.path.isfile(wkhtmltopdf_path):
            common_paths = [
                "/usr/local/bin/wkhtmltopdf",  # Common for macOS/Linux
                "/usr/bin/wkhtmltopdf",  # Common for Linux
                "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe",  # Common for Windows
            ]
            for path_option in common_paths:
                if os.path.isfile(path_option):
                    wkhtmltopdf_path = path_option
                    logger.info(f"Found wkhtmltopdf at: {wkhtmltopdf_path}")
                    break

        if not wkhtmltopdf_path or not os.path.isfile(wkhtmltopdf_path):
            logger.error(
                "wkhtmltopdf not found. Set WKHTMLTOPDF_PATH env var or install it in a common location."
            )
            logger.error(
                "Please install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html"
            )
            return None

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
                "wiki-tables",
            ],
        )

        # Custom CSS for better styling of code blocks and other elements
        custom_css_path = Path(__file__).parent / "pdf_style.css"
        if custom_css_path.exists():
            css = custom_css_path.read_text()
            html_content = f"<style>{css}</style>" + html_content

        # 3. Generate PDF from HTML
        await asyncio.to_thread(
            pdfkit.from_string,
            html_content,
            output_pdf_filepath,
            configuration=config,
            options={"enable-local-file-access": None},
        )

        if os.path.exists(output_pdf_filepath):
            logger.info(f"Successfully generated PDF: {output_pdf_filepath}")
            # Return a relative path for use in the frontend/database
            relative_path = str(
                Path(output_pdf_filepath).relative_to(pdf_storage_base_dir.parent)
            )
            return relative_path
        else:
            logger.error(
                f"PDF file not found after generation attempt at {output_pdf_filepath}"
            )
            return None
    except Exception as e:
        logger.error(
            f"Failed to generate PDF at {output_pdf_filepath}: {e}", exc_info=True
        )
        return None


async def convert_markdown_file_to_pdf(
    markdown_filepath: str, output_pdf_filepath: str
) -> bool:
    """
    Converts a markdown file to a PDF file.
    Reads the markdown file and uses generate_pdf_from_markdown_string for conversion.

    Args:
        markdown_filepath: Path to the input markdown file.
        output_pdf_filepath: Path where the output PDF file should be saved.

    Returns:
        True if PDF generation was successful, False otherwise.
    """
    logger.info(
        f"Attempting to convert markdown file {markdown_filepath} to PDF {output_pdf_filepath}."
    )
    try:
        async with aiofiles.open(markdown_filepath, "r", encoding="utf-8") as md_file:
            markdown_content = await md_file.read()

        logger.info(f"Successfully read markdown content from {markdown_filepath}.")

        return await generate_pdf_from_markdown_string(
            markdown_content, output_pdf_filepath=output_pdf_filepath
        )

    except FileNotFoundError:
        logger.error(
            f"Markdown file not found: {markdown_filepath}\n{traceback.format_exc()}"
        )
        return False
    except IOError as e:
        logger.error(
            f"IOError reading markdown file {markdown_filepath}: {e}\n{traceback.format_exc()}"
        )
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error in convert_markdown_file_to_pdf for {markdown_filepath}: {e}\n{traceback.format_exc()}"
        )
        return False


def sanitize_filename(filename: str) -> str:
    """Removes or replaces characters invalid in filenames."""
    # Remove characters invalid in Windows/Linux/macOS filenames
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
    # Optionally replace multiple spaces/underscores with a single one
    sanitized = re.sub(r"[_ ]+", "_", sanitized)
    # Optionally remove leading/trailing underscores/spaces
    sanitized = sanitized.strip("_ ")
    # Optionally limit length (example, adjust if needed)
    MAX_FILENAME_LENGTH = 100
    if len(sanitized) > MAX_FILENAME_LENGTH:
        # Ensure extension is preserved if present
        name, ext = os.path.splitext(sanitized)
        if len(ext) < MAX_FILENAME_LENGTH:  # Check if ext itself isn't too long
            name = name[: MAX_FILENAME_LENGTH - len(ext) - 1]  # Adjust name length
            sanitized = name + ext
        else:  # Handle case where extension is very long
            sanitized = sanitized[:MAX_FILENAME_LENGTH]

    return sanitized if sanitized else "untitled"  # Ensure not empty


def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format without decimal places"""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
