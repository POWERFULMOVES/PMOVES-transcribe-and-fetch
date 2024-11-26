import os

import re

import logging

import aiohttp

import markdown2

import pdfkit

from datetime import datetime

from typing import Union, Optional

import json

import aiofiles

import asyncio



logger = logging.getLogger("app.fetch_content")



# Function to sanitize filenames

def sanitize_filename(title):

    # Replace invalid characters with an underscore

    return re.sub(r'[<>:"/\\|?*]', '_', title)



# Function to fetch content from a URL

async def fetch_content_from_url(

    url: str, 

    json_response: bool = False, 

    timeout: Optional[int] = None, 

    target_selector: Optional[str] = None

) -> Union[str, dict]:

    """

    Fetch content from a URL using Jina Reader API in LLM-friendly format.

    """

    api_url = f"https://r.jina.ai/{url}"

    

    # Set headers according to Jina Reader API docs

    headers = {

        'Accept': 'application/json' if json_response else 'text/plain',

        'Content-Type': 'application/json' if json_response else 'text/plain',

        'Content-Format': 'clean',

        'Extract-Links': 'true',

        'Excluded-Selector': 'header,footer,nav,aside,script,style'

    }

    

    if timeout is not None:

        headers['Timeout'] = str(timeout)

    

    if target_selector is not None:

        headers['Target-Selector'] = target_selector



    async with aiohttp.ClientSession() as session:

        try:

            async with session.get(api_url, headers=headers) as response:

                if response.status == 200:

                    if json_response:

                        try:

                            json_data = await response.json(content_type=None)

                            # Extract content and links from JSON response

                            if isinstance(json_data, dict):

                                content = json_data.get('data', {}).get('content', '')

                                links = json_data.get('data', {}).get('links', [])

                                if not content:

                                    content = json_data.get('content', '')

                                if not content:

                                    content = json.dumps(json_data, indent=2)

                                

                                return {

                                    'content': content,

                                    'title': json_data.get('data', {}).get('title', ''),

                                    'url': json_data.get('data', {}).get('url', url),

                                    'links': links

                                }

                            return {"content": str(json_data)}

                        except json.JSONDecodeError as e:

                            logger.error(f"JSON decode error: {e}")

                            text_content = await response.text()

                            return {"content": text_content}

                    else:

                        # For plain text, return cleaned content

                        return await response.text()

                elif response.status == 429:

                    retry_after = response.headers.get('Retry-After', '60')

                    raise Exception(f"Rate limit exceeded. Try again after {retry_after} seconds")

                else:

                    error_text = await response.text()

                    logger.error(f"Error response: {error_text}")

                    raise Exception(f"Error fetching content: {response.status} {response.reason}")

        except aiohttp.ClientError as e:

            logger.error(f"Network error while fetching content: {str(e)}")

            raise



# Function to extract a clean title from a URL

def extract_title_from_url(url):

    # Remove the protocol (https:// or http://)

    title = re.sub(r'^(https?://)', '', url)  # Remove the protocol

    title = title.split('//')[-1]  # Get the part after 'https://'

    

    # Sanitize the title to ensure it's a valid filename

    title = sanitize_filename(title)  # Use the sanitize function

    title = re.sub(r'\s+', '_', title)  # Replace spaces with underscores

    title = re.sub(r'__+', '_', title)  # Avoid double underscores

    title = re.sub(r'_+', '_', title)  # Remove multiple underscores

    

    logger.debug(f"Sanitized title: {title}")  # Log the sanitized title

    return title



# Function to generate a unique filename based on URL and timestamp

def generate_unique_filename(url, extension):

    title = extract_title_from_url(url)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{title}_{timestamp}.{extension}"

    

    logger.debug(f"Generated filename: {filename}")  # Log the generated filename

    return filename



# Function to save text content to a Markdown file

async def save_text_to_markdown(text, output_path):

    try:

        # Ensure the directory exists

        directory = os.path.dirname(output_path)

        if not os.path.exists(directory):

            os.makedirs(directory)

            logger.info(f"Created directory: {directory}")



        # Use async file writing

        async with aiofiles.open(output_path, 'w', encoding='utf-8') as file:

            await file.write(text)

        logger.info(f"Markdown file saved successfully: {output_path}")

    except Exception as e:

        logger.error(f"Error saving markdown file: {str(e)}")

        raise



# Function to convert Markdown to HTML

def convert_markdown_to_html(md_path):

    try:

        # Reading the markdown file

        with open(md_path, 'r', encoding='utf-8') as file:

            markdown_text = file.read()

        

        # Converting markdown to HTML

        html_text = markdown2.markdown(markdown_text)



        logger.debug(f"HTML content to be sent: {html_text}")

        

        return html_text



    except Exception as e:

        logger.error(f"Error converting markdown to HTML: {str(e)}")

        return None



# Function to convert Markdown to PDF

async def convert_markdown_to_pdf(md_path, pdf_path):

    try:

        # Reading the markdown file asynchronously

        async with aiofiles.open(md_path, 'r', encoding='utf-8') as file:

            markdown_text = await file.read()

        

        # Converting markdown to HTML

        html_text = markdown2.markdown(markdown_text)



        logger.debug(f"HTML content to be converted: {html_text}")



        # Setting up wkhtmltopdf configuration

        config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

        

        options = {

            'quiet': '',

            'enable-local-file-access': ''

        }



        # Run PDF conversion in a thread pool since pdfkit is synchronous

        await asyncio.to_thread(

            pdfkit.from_string,

            html_text,

            pdf_path,

            options=options,

            configuration=config

        )

        

        logger.info(f"PDF file created successfully: {pdf_path}")

        return True



    except Exception as e:

        logger.error(f"Critical error converting markdown to PDF: {str(e)}")

        return False
