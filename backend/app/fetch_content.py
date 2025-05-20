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
from .general_utils import generate_pdf_from_markdown_string # Added import

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
    target_selector: Optional[str] = None,
    excluded_selector: Optional[str] = None,
    clean_format: bool = True,
    # Advanced Jina.ai options
    browser_engine: str = "playwright",
    token_budget: int = 4000,
    remove_images: bool = False,
    extract_links: bool = True,
    image_captioning: bool = False,
    cache_ttl: int = 3600,
    markdown_flavor: str = "github",
    browser_viewport: str = "1920x1080",
    browser_locale: str = "en-US",
    extract_metadata: bool = True
) -> Union[str, dict]:
    """
    Fetch content from a URL using Jina Reader API in LLM-friendly format.

    Advanced options:
    - browser_engine: 'playwright' for better quality or 'selenium' for speed
    - token_budget: Maximum number of tokens to extract (1,000-100,000)
    - remove_images: Whether to exclude images from the content
    - extract_links: Whether to extract links from the content
    - image_captioning: Whether to add captions to images
    - cache_ttl: Time-to-live for cache in seconds
    - markdown_flavor: 'github', 'standard', or 'obsidian'
    - browser_viewport: Browser viewport size (e.g. '1920x1080')
    - browser_locale: Browser locale (e.g. 'en-US')
    - extract_metadata: Whether to extract page metadata
    """
    api_url = f"https://r.jina.ai/{url}"

    # Set headers according to Jina Reader API docs
    headers = {
        'Accept': 'application/json' if json_response else 'text/plain',
        'Content-Type': 'application/json', # Jina seems to prefer application/json for request body if sending one
        'Content-Format': 'clean' if clean_format else 'raw',
        'Extract-Links': 'true' if extract_links else 'false',
    }

    # Add optional headers based on parameters
    if timeout is not None:
        headers['Timeout'] = str(timeout)
    
    if target_selector is not None:
        headers['Target-Selector'] = target_selector
        
    if excluded_selector is not None:
        headers['Excluded-Selector'] = excluded_selector
    
    # Add advanced Jina.ai options
    headers['Browser-Engine'] = browser_engine
    headers['Token-Budget'] = str(token_budget)
    headers['Remove-Images'] = 'true' if remove_images else 'false'
    headers['Image-Captioning'] = 'true' if image_captioning else 'false'
    headers['Cache-TTL'] = str(cache_ttl)
    headers['Markdown-Flavor'] = markdown_flavor
    headers['Browser-Viewport'] = browser_viewport
    headers['Browser-Locale'] = browser_locale
    headers['Extract-Metadata'] = 'true' if extract_metadata else 'false'

    async with aiohttp.ClientSession() as session:
        try:
            # Use a timeout for the request itself if not provided via headers
            request_timeout = aiohttp.ClientTimeout(total=timeout if timeout else 300) # Default 5 mins
            async with session.get(api_url, headers=headers, timeout=request_timeout) as response:
                if response.status == 200:
                    if json_response:
                        try:
                            json_data = await response.json(content_type=None) # Allow any content type from Jina
                            
                            if isinstance(json_data, dict):
                                data_section = json_data.get('data', {})
                                content = data_section.get('content', '')
                                links = data_section.get('links', [])
                                metadata_dict = data_section.get('metadata', {})
                                title = data_section.get('title', '')
                                response_url_from_jina = data_section.get('url', url)

                                if not content: # Check root level if not in 'data'
                                    content = json_data.get('content', '')
                                if not content and isinstance(json_data, dict): # Fallback for non-standard Jina responses
                                    content = json.dumps(json_data, indent=2) # Return raw JSON if content extraction failed
                                
                                if not isinstance(title, str) or not title.strip():
                                    title = "Untitled" # Default title
                                
                                # PDF Generation Logic
                                pdf_relative_path = None
                                markdown_content_for_pdf = content  # 'content' is the fetched markdown
                                original_url_for_pdf = url      # 'url' is the original input URL to the function
                                
                                try:
                                    PDF_STORAGE_PATH = os.getenv('PDF_STORAGE_PATH', 'backend/app/temp_pdfs/')
                                    os.makedirs(PDF_STORAGE_PATH, exist_ok=True)
                                    
                                    unique_pdf_filename = generate_unique_filename(original_url_for_pdf, "pdf") # Uses local generate_unique_filename
                                    output_pdf_filepath = os.path.join(PDF_STORAGE_PATH, unique_pdf_filename)
                                    
                                    # Call the new shared utility
                                    pdf_conversion_successful = await generate_pdf_from_markdown_string(markdown_content_for_pdf, output_pdf_filepath)
                                    
                                    if pdf_conversion_successful:
                                        # Construct relative path for client
                                        # Example: if PDF_STORAGE_PATH is "backend/app/temp_pdfs/" and unique_pdf_filename is "example_com_20230101.pdf",
                                        # pdf_relative_path should be "temp_pdfs/example_com_20230101.pdf"
                                        base_storage_dir_name = os.path.basename(os.path.normpath(PDF_STORAGE_PATH))
                                        pdf_relative_path = os.path.join(base_storage_dir_name, unique_pdf_filename).replace("\\", "/")
                                        logger.info(f"PDF generated, relative path: {pdf_relative_path}")
                                    else:
                                        logger.error(f"PDF conversion failed for URL {original_url_for_pdf} using shared utility. PDF path will be None.")
                                        # pdf_relative_path remains None
                                except Exception as e:
                                    logger.error(f"Error during PDF generation process for URL {original_url_for_pdf}: {str(e)}")
                                    # pdf_relative_path remains None
                                
                                return {
                                    "markdown": content,
                                    "pdf_path": pdf_relative_path,
                                    "url": url, # Use the original input URL
                                    "title": title,
                                    "links": links, # Maintain existing successfully returned values
                                    "metadata": metadata_dict # Maintain existing successfully returned values
                                }
                            else: # Jina response was valid JSON but not a dictionary
                                logger.warning(f"Jina response for {url} was JSON but not a dict: {type(json_data)}. Content: {str(json_data)[:200]}")
                                return {"content": str(json_data), "title": "Untitled", "url": url, "links": [], "metadata": {}}
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error for URL {url}: {e}")
                            text_content = await response.text()
                            return {"content": text_content, "title": "Untitled", "url": url, "links": [], "metadata": {}, "error": "JSONDecodeError"}
                    else: # Plain text response
                        return await response.text()
                elif response.status == 429:
                    retry_after = response.headers.get('Retry-After', '60')
                    logger.warning(f"Rate limit exceeded for URL {url}. Try again after {retry_after} seconds.")
                    raise Exception(f"Rate limit exceeded for URL {url}. Try again after {retry_after} seconds")
                else:
                    error_text = await response.text()
                    logger.error(f"Error fetching content from URL {url}: {response.status} {response.reason}. Response: {error_text[:500]}")
                    raise Exception(f"Error fetching content from URL {url}: {response.status} {response.reason}")
        except aiohttp.ClientConnectorError as e:
            logger.error(f"AIOHTTP ClientConnectorError while fetching content from URL {url}: {str(e)}")
            raise
        except aiohttp.ClientResponseError as e: # For non-200 responses not caught above
            logger.error(f"AIOHTTP ClientResponseError while fetching content from URL {url}: status={e.status}, message='{e.message}'")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Timeout error while fetching content from URL {url}")
            raise
        except Exception as e: # Generic catch-all
            logger.error(f"Unexpected error while fetching content from URL {url}: {type(e).__name__} - {str(e)}")
            raise

# Function to extract a clean title from a URL
def extract_title_from_url(url):
    # Remove the protocol (https:// or http://)
    title = re.sub(r'^(https?://)', '', url)
    title = title.split('//')[-1]
    
    title = sanitize_filename(title)
    title = re.sub(r'\s+', '_', title)
    title = re.sub(r'__+', '_', title)
    title = re.sub(r'_+', '_', title)
    
    logger.debug(f"Sanitized title: {title}")
    return title

# Function to generate a unique filename based on URL and timestamp
def generate_unique_filename(url, extension):
    title = extract_title_from_url(url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title}_{timestamp}.{extension}"
    
    logger.debug(f"Generated filename: {filename}")
    return filename

# Function to save text content to a Markdown file
async def save_text_to_markdown(text, output_path):
    try:
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

        async with aiofiles.open(output_path, 'w', encoding='utf-8') as file:
            await file.write(text)
        logger.info(f"Markdown file saved successfully: {output_path}")
    except Exception as e:
        logger.error(f"Error saving markdown file '{output_path}': {str(e)}")
        raise

# Function to convert Markdown to HTML
def convert_markdown_to_html(md_path):
    try:
        with open(md_path, 'r', encoding='utf-8') as file:
            markdown_text = file.read()
        
        html_text = markdown2.markdown(markdown_text)
        logger.debug(f"HTML content to be sent: {html_text[:200]}")
        return html_text
    except Exception as e:
        logger.error(f"Error converting markdown to HTML from '{md_path}': {str(e)}")
        return None

# Removed local convert_markdown_to_pdf function as it's now centralized in utils.py
