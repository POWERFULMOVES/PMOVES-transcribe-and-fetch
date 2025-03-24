from typing import Optional, BinaryIO, List, Dict, Tuple, Any, Union
import os
from supabase.client import create_client
from dotenv import load_dotenv
import logging
from datetime import datetime
import glob
from tqdm import tqdm
import re
import frontmatter
import openai
import asyncio
import json
import hashlib
from pathlib import Path

class MarkdownUpserter:
    def __init__(self, console=None, logger=None, openai_api_key=None):
        # Load environment variables from the correct path
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path=env_path)
        
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(f"Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env file at {env_path}")
            
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Setup console
        self.console = console
        
        # Setup OpenAI
        self.openai_api_key = openai_api_key
        if openai_api_key:
            openai.api_key = openai_api_key
        
        # Setup logging if not provided
        if logger:
            self.logger = logger
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler(f'upserter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
                ]
            )
            self.logger = logging.getLogger(__name__)

    def extract_video_id(self, markdown_content: str) -> Optional[str]:
        """Extract video ID from markdown content"""
        lines = markdown_content.split('\n')
        
        # First try to get video ID from the header (new format)
        for line in lines:
            if line.startswith('# Transcription for Video:'):
                # Extract video ID from markdown link [ID](url)
                match = re.search(r'\[([A-Za-z0-9_-]{11})\]', line)
                if match:
                    return self.validate_video_id(match.group(1))
        
        # If not found in header, try to get from table
        for line in lines:
            # Skip header and separator lines
            if '|' not in line or 'video_id' in line.lower() or line.strip().startswith('|:'):
                continue
                
            # Split the line into columns and get the video_id column
            columns = [col.strip() for col in line.split('|') if col.strip()]
            if len(columns) >= 2:  # We expect at least watch_url and video_id columns
                video_id = columns[1]  # video_id is in the second column
                return self.validate_video_id(video_id)
        
        return None

    def extract_title(self, markdown_content: str) -> str:
        """Extract title from markdown file"""
        lines = markdown_content.split('\n')
        if lines and lines[0].startswith('# Transcription for Video:'):
            return lines[0].replace('# Transcription for Video:', '').strip()
        return "Untitled Transcript"

    def process_markdown_file(self, file: BinaryIO) -> str:
        """Process an uploaded markdown file and return its contents"""
        try:
            content = file.read().decode('utf-8')
            if not content:
                raise ValueError("File is empty")
            return content
        except UnicodeDecodeError:
            raise ValueError("File must be valid UTF-8 text")
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")

    def clean_watch_url(self, url: str) -> str:
        """Clean watch_url from various formats to a standard URL"""
        try:
            # Handle HYPERLINK formula format
            if 'HYPERLINK' in url.upper():
                # Extract URL from HYPERLINK formula - get first quoted string
                match = re.search(r'"([^"]+)"', url)
                if match:
                    url = match.group(1)
            
            # Handle markdown link format [Link](url)
            if url.startswith('['):
                match = re.search(r'\((.*?)\)', url)
                if match:
                    url = match.group(1)
            
            # If URL is just a video ID, convert it to full YouTube URL
            if not url.startswith(('http://', 'https://')):
                if '/' not in url and '.' not in url:  # Likely a video ID
                    url = f'https://www.youtube.com/watch?v={url}'
                else:
                    url = 'https://' + url.lstrip('/')
            
            # Validate it's a proper YouTube URL
            if 'youtube.com' not in url and 'youtu.be' not in url:
                raise ValueError(f"Invalid YouTube URL format: {url}")
            
            return url
            
        except Exception as e:
            self.logger.error(f"Error cleaning URL '{url}': {str(e)}")
            raise

    def format_time_string(self, time_str: str) -> str:
        """Convert various time formats to HH:MM:SS"""
        time_str = time_str.strip()
        try:
            # Split the time string by colons
            parts = time_str.split(':')
            # Handle cases with milliseconds
            seconds = parts[-1].split('.')[0]  # Remove milliseconds
            parts[-1] = seconds
            
            # Pad with zeros if needed
            while len(parts) < 3:
                parts.insert(0, '00')
            
            return ':'.join(part.zfill(2) for part in parts)
        except Exception as e:
            self.logger.error(f"Error formatting time string '{time_str}': {str(e)}")
            raise ValueError(f"Invalid time format: {time_str}")

    def validate_video_id(self, video_id: str) -> str:
        """
        Validates YouTube video ID format.
        Raises ValueError if invalid.
        """
        if not video_id:
            raise ValueError("Video ID cannot be empty")
        
        # Remove any whitespace
        video_id = video_id.strip()
        
        # YouTube video IDs are 11 characters long
        # They contain alphanumeric characters, underscores, and hyphens
        youtube_id_pattern = r'^[A-Za-z0-9_-]{11}$'
        
        if not re.match(youtube_id_pattern, video_id):
            raise ValueError(f"Invalid YouTube video ID format: {video_id}")
            
        return video_id

    def parse_segments(self, markdown_content: str, filename: str) -> list:
        """Parse markdown table into segments"""
        lines = markdown_content.split('\n')
        segments = []
        
        # Find the table header
        table_start = -1
        for i, line in enumerate(lines):
            if '|' in line and 'watch_url' in line.lower():
                table_start = i
                break

        if table_start == -1:
            self.logger.error(f"Table header not found in {filename}")
            raise ValueError("No valid transcript table found in markdown")
        
        # Skip header and separator rows
        current_line = table_start + 2
        segment_counter = 1
        
        while current_line < len(lines):
            line = lines[current_line].strip()
            if not line or '|' not in line:
                break
            
            # Split line into columns
            columns = [col.strip() for col in line.split('|') if col.strip()]
            if len(columns) >= 6:
                try:
                    # Extract details
                    watch_url = self.clean_watch_url(columns[0])
                    video_id = self.validate_video_id(columns[1])  # Validate video ID
                    segment_id = int(columns[2]) if columns[2].isdigit() else segment_counter
                    start_time = self.format_time_string(columns[3])
                    end_time = self.format_time_string(columns[4])
                    text = columns[5]

                    # Create segment dictionary
                    segment = {
                        'watch_url': watch_url,
                        'video_id': video_id,
                        'segment_id': segment_id,
                        'start_time': start_time,
                        'end_time': end_time,
                        'content': text,
                        'metadata': {
                            'source_file': filename,
                            'upload_date': datetime.now().isoformat(),
                            'line_number': current_line + 1
                        }
                    }
                    segments.append(segment)
                    segment_counter += 1
                except Exception as e:
                    self.logger.error(f"Error parsing row {current_line + 1} in {filename}: {str(e)}")
                    self.logger.error(f"Row content: {line}")
            
            current_line += 1

        if not segments:
            self.logger.warning(f"No valid segments found in {filename}")
        
        self.logger.info(f"Successfully parsed {len(segments)} segments from {filename}")
        return segments

    async def process_markdown_file_sections(self, file_path: str) -> Tuple[str, List[Dict]]:
        """
        Processes a single markdown file with section-based format, extracting metadata and segments.
        """
        with open(file_path, "r") as f:
            try:
                post = frontmatter.load(f)
            except Exception as e:
                self.logger.error(
                    f"Error reading or parsing markdown file {file_path}: {e}"
                )
                raise

        # Extract video ID from filename and validate
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        video_id = self.validate_video_id(base_name)

        # Extract segments
        segments = self.parse_sections(post.content, video_id)

        return video_id, segments

    def parse_sections(self, content: str, video_id: str) -> List[Dict]:
        """
        Parses the content of the markdown file in section format and extracts segments.
        """
        segments = []
        current_segment = {}
        lines = content.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#"):
                if current_segment:
                    segments.append(current_segment)

                # Extract segment ID
                try:
                    segment_id = int(line.split("#")[1].strip())
                except ValueError:
                    self.logger.warning(f"Skipping invalid segment line: {line}")
                    i += 1
                    continue

                current_segment = {
                    "segment_id": segment_id,
                    "video_id": video_id,
                    "start_time": None,
                    "end_time": None,
                    "content": "",
                    "metadata": {},
                }
            elif line.startswith("-"):
                if current_segment:
                    try:
                        key, value = line.split("-", 1)[1].split(":", 1)
                        key = key.strip().replace(" ", "_").lower()
                        value = value.strip()

                        if key == "start_time":
                            current_segment["start_time"] = self.format_time_string(value)
                        elif key == "end_time":
                            current_segment["end_time"] = self.format_time_string(value)
                        elif key == "watch_url":
                            current_segment["watch_url"] = self.clean_watch_url(value)
                        else:
                            current_segment["metadata"][key] = value
                    except ValueError:
                        self.logger.warning(f"Skipping invalid metadata line: {line}")
            elif line and current_segment:
                current_segment["content"] += line + " "
            i += 1

        if current_segment:
            segments.append(current_segment)

        return segments

    async def process_transcript_and_table(self, md_file_path: str, md_table_path: str):
        """
        Processes a full transcript from a .md file and metadata from a .md table.
        """
        try:
            # Extract full transcript and metadata
            with open(md_file_path, 'r') as f:
                full_transcript = f.read()
            
            with open(md_table_path, 'r') as f:
                table_content = f.read()
            
            # Parse table data
            segments = self.parse_segments(table_content, os.path.basename(md_table_path))
            
            if not segments:
                raise ValueError("No valid segments found in table")
                
            video_id = segments[0]['video_id']  # Use video_id from first segment
            
            # Store the full transcript
            await self.store_full_transcript(video_id, full_transcript, md_file_path)
            
            # Upload segments
            await self.upsert_transcript(table_content, os.path.basename(md_table_path))

        except Exception as e:
            self.logger.error(f"Error processing transcript and table: {e}")
            raise

    async def store_full_transcript(self, video_id: str, full_transcript: str, source_file: str):
        """Stores the full transcript in the database."""
        try:
            # Extract video ID from the transcript content if not provided
            if not video_id:
                extracted_id = self.extract_video_id(full_transcript)
                if not extracted_id:
                    raise ValueError("Could not extract video ID from transcript content")
                video_id = extracted_id
            
            # Validate video ID format
            video_id = self.validate_video_id(video_id)

            # Store in database
            self.supabase.table("video_transcriptions_full").upsert(
                {
                    "video_id": video_id,
                    "full_transcript": full_transcript,
                    "source_file": source_file,
                    "upload_date": datetime.now().isoformat()
                }
            ).execute()

            if self.console:
                self.console.print(f"Stored full transcript for video {video_id}")

        except Exception as e:
            self.logger.error(f"Error storing full transcript: {e}")
            raise

    async def upsert_transcript(self, markdown_content: str, filename: str, force_overwrite=False) -> dict:
        """Upsert a transcript into Supabase"""
        try:
            if not markdown_content:
                raise ValueError("Markdown content cannot be empty")

            # Extract metadata
            video_id = self.extract_video_id(markdown_content)
            if not video_id:
                raise ValueError("No video_id found in markdown")

            self.logger.info(f"Processing transcript for video_id: {video_id}")

            # Check if video_id already exists in both tables
            existing_segments = self.supabase.table('video_transcriptions')\
                .select('video_id')\
                .eq('video_id', video_id)\
                .execute()

            existing_full = self.supabase.table('video_transcriptions_full')\
                .select('video_id')\
                .eq('video_id', video_id)\
                .execute()

            if (existing_segments.data or existing_full.data) and not force_overwrite:
                self.logger.warning(f"Video ID {video_id} already exists in database")
                if self.console:
                    self.console.print(f"⚠️ Skipping {filename} - Video ID {video_id} already exists")
                    self.console.print("   Use force_overwrite=True to overwrite existing content")
                return {
                    'status': 'skipped',
                    'video_id': video_id,
                    'reason': 'already_exists'
                }

            # Parse segments
            segments = self.parse_segments(markdown_content, filename)
            if not segments:
                raise ValueError("No valid segments found in markdown")

            # Store full transcript in video_transcriptions_full
            try:
                # Extract full content by joining all segment contents
                full_transcript = "\n\n".join([
                    f"Segment {seg['segment_id']} ({seg['start_time']} - {seg['end_time']}):\n{seg['content']}"
                    for seg in segments
                ])
                
                # Delete existing full transcript if any
                if existing_full.data:
                    self.supabase.table('video_transcriptions_full')\
                        .delete()\
                        .eq('video_id', video_id)\
                        .execute()
                    self.logger.info(f"Deleted existing full transcript for video_id: {video_id}")

                await self.store_full_transcript(video_id, full_transcript, filename)
                self.logger.info(f"Stored full transcript for video_id: {video_id}")
            except Exception as e:
                self.logger.error(f"Error storing full transcript: {e}")
                raise  # Now raising the error as we want both operations to succeed
                
            # Delete existing segments if any
            if existing_segments.data:
                self.supabase.table('video_transcriptions')\
                    .delete()\
                    .eq('video_id', video_id)\
                    .execute()
                self.logger.info(f"Deleted existing segments for video_id: {video_id}")

            # Insert new segments
            self.supabase.table('video_transcriptions')\
                .insert(segments)\
                .execute()

            self.logger.info(f"Successfully upserted {len(segments)} segments for video_id: {video_id}")
            
            if self.console:
                self.console.print(f"✓ Successfully processed {filename}")
                self.console.print(f"  - Video ID: {video_id}")
                self.console.print(f"  - Segments: {len(segments)}")
                if existing_segments.data or existing_full.data:
                    self.console.print("  - Existing content was overwritten")

            return {
                'status': 'success',
                'video_id': video_id,
                'segment_count': len(segments),
                'overwritten': bool(existing_segments.data or existing_full.data)
            }

        except Exception as e:
            self.logger.error(f"Error upserting transcript: {str(e)}")
            raise

    async def process_directory(self, directory_path: str, force_overwrite=False) -> list:
        """Process all markdown files in a directory"""
        results = []
        markdown_files = glob.glob(os.path.join(directory_path, "*.md"))
        
        self.logger.info(f"Found {len(markdown_files)} markdown files in {directory_path}")
        
        for filepath in tqdm(markdown_files, desc="Processing files"):
            filename = os.path.basename(filepath)
            try:
                with open(filepath, 'rb') as file:
                    content = self.process_markdown_file(file)
                    result = await self.upsert_transcript(content, filename, force_overwrite)
                    results.append(result)
                    self.logger.info(f"Successfully processed {filename}")
            except ValueError as e:
                if "already exists" in str(e):
                    self.logger.warning(f"Skipping {filename}: {str(e)}")
                else:
                    self.logger.error(f"Error processing {filename}: {str(e)}")
                results.append({
                    'filename': filename,
                    'status': 'skipped' if "already exists" in str(e) else 'error',
                    'error': str(e)
                })
            except Exception as e:
                self.logger.error(f"Error processing {filename}: {str(e)}")
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'error': str(e)
                })
                
        return results

    async def upsert_from_file(self, file: BinaryIO, filename: str, force_overwrite=False) -> dict:
        """Process and upsert transcript from an uploaded file"""
        content = self.process_markdown_file(file)
        return await self.upsert_transcript(content, filename, force_overwrite)

    # --- Content Type Detection ---
    
    def detect_content_type(self, content: str, filename: str) -> str:
        """Detect the type of content being processed"""
        ext = os.path.splitext(filename)[1].lower() if filename else ""
        
        # Check file extension first
        if ext in ['.md', '.markdown']:
            if '|' in content and 'watch_url' in content.lower():
                return 'transcript'
            return 'markdown'
        elif ext in ['.html', '.htm']:
            return 'webpage'
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return 'video'
        elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.m4a']:
            return 'audio'
        elif ext in ['.json']:
            return 'json'
        elif ext in ['.txt']:
            return 'text'
            
        # If extension doesn't clearly indicate type, check content
        if '<html' in content.lower() or '</html>' in content.lower():
            return 'webpage'
        if '|' in content and any(header in content.lower() for header in ['watch_url', 'video_id', 'start_time']):
            return 'transcript'
            
        # Default to text if we can't determine
        return 'text'

    # --- Web Page Content Processing ---
    
    async def process_webpage(self, content: str, url: str, filename: str = None) -> Dict[str, Any]:
        """Process web page content for storage
        
        Args:
            content: The HTML or text content of the web page
            url: The source URL of the content
            filename: Optional filename if saved locally
            
        Returns:
            dict: Result of the processing operation
        """
        try:
            # Generate a unique content ID if not from a video
            content_id = self.generate_content_id(url)
            
            # Extract useful metadata
            title = self.extract_title_from_html(content) or url.split('/')[-1]
            
            # Clean content if HTML
            clean_content = self.clean_html_content(content) if '<html' in content.lower() else content
            
            # Store in webpage_content table - create this if it doesn't exist
            result = self.supabase.table("webpage_content").upsert(
                {
                    "content_id": content_id,
                    "title": title,
                    "url": url,
                    "content": clean_content,
                    "source_file": filename,
                    "upload_date": datetime.now().isoformat(),
                    "content_type": "webpage"
                }
            ).execute()
            
            if self.console:
                self.console.print(f"Stored web page content: {title}")
                
            return {
                'status': 'success',
                'content_id': content_id,
                'title': title,
                'content_type': 'webpage'
            }
            
        except Exception as e:
            self.logger.error(f"Error processing web page: {str(e)}")
            raise
    
    def extract_title_from_html(self, html_content: str) -> Optional[str]:
        """Extract title from HTML content"""
        try:
            match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
            return None
        except:
            return None
    
    def clean_html_content(self, html_content: str) -> str:
        """Basic HTML cleaning to extract text"""
        # This is a simple implementation - for production, consider using
        # a proper HTML parser like BeautifulSoup
        try:
            # Remove scripts, styles, and head
            for tag in ['script', 'style', 'head']:
                html_content = re.sub(f'<{tag}.*?</{tag}>', '', html_content, 
                                       flags=re.DOTALL | re.IGNORECASE)
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html_content)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except:
            # If cleaning fails, return the original to avoid data loss
            return html_content
    
    # --- Video and Audio Processing ---
    
    async def process_media_file(self, 
                                file_path: str, 
                                media_type: str,
                                metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a video or audio file metadata
        
        This method handles metadata about downloaded media files.
        It doesn't process the actual media content but stores information about it.
        
        Args:
            file_path: Path to the media file
            media_type: Type of media ('video' or 'audio')
            metadata: Additional metadata about the media file
            
        Returns:
            dict: Result of the processing operation
        """
        try:
            # Generate a content ID for the media file
            file_name = os.path.basename(file_path)
            content_id = self.generate_content_id(file_path)
            
            # Prepare metadata
            metadata = metadata or {}
            title = metadata.get('title', file_name)
            source_url = metadata.get('source_url', '')
            duration = metadata.get('duration', '')
            
            # Store in media_content table (need to create this table)
            result = self.supabase.table("media_content").upsert(
                {
                    "content_id": content_id,
                    "title": title,
                    "file_path": file_path,
                    "source_url": source_url,
                    "duration": duration,
                    "metadata": json.dumps(metadata),
                    "upload_date": datetime.now().isoformat(),
                    "content_type": media_type,
                    "processed": False
                }
            ).execute()
            
            if self.console:
                self.console.print(f"Stored {media_type} metadata: {title}")
                
            return {
                'status': 'success',
                'content_id': content_id,
                'title': title,
                'content_type': media_type
            }
            
        except Exception as e:
            self.logger.error(f"Error processing {media_type} file: {str(e)}")
            raise
    
    async def process_video(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process video file metadata"""
        return await self.process_media_file(file_path, 'video', metadata)
    
    async def process_audio(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process audio file metadata"""
        return await self.process_media_file(file_path, 'audio', metadata)
    
    # --- Utility Methods ---
    
    def generate_content_id(self, source: str) -> str:
        """Generate a unique ID for content based on its source"""
        # Use a hash of the source path/URL to ensure uniqueness
        return hashlib.md5(source.encode('utf-8')).hexdigest()
    
    async def check_for_duplicate(self, content_type: str, identifier: str, content: str = None, title: str = None) -> Dict[str, Any]:
        """Check if content already exists in the database
        
        Args:
            content_type: Type of content ('webpage', 'text', 'video', 'audio')
            identifier: URL, file path, or video ID to check
            content: Content to check for duplicate by hash (for text content)
            title: Title for text content checks
            
        Returns:
            Dict with exists (boolean) and id of existing content if found
        """
        try:
            if content_type == 'webpage':
                # Use the check_webpage_duplicate function
                result = self.supabase.rpc(
                    'check_webpage_duplicate', 
                    {'url_to_check': identifier}
                ).execute()
                
                if result.data and len(result.data) > 0:
                    return {
                        'exists': result.data[0]['exists'] if 'exists' in result.data[0] else result.data[0].get('"exists"', False), 
                        'content_id': result.data[0]['content_id']
                    }
                    
            elif content_type == 'text' and content and title:
                # Use the check_text_duplicate function
                result = self.supabase.rpc(
                    'check_text_duplicate', 
                    {'title_to_check': title, 'content_to_check': content}
                ).execute()
                
                if result.data and len(result.data) > 0:
                    return {
                        'exists': result.data[0]['exists'] if 'exists' in result.data[0] else result.data[0].get('"exists"', False), 
                        'content_id': result.data[0]['content_id']
                    }
                    
            elif content_type in ['video', 'audio']:
                # Use the check_media_duplicate function
                result = self.supabase.rpc(
                    'check_media_duplicate', 
                    {'file_path_to_check': identifier, 'source_url_to_check': None}
                ).execute()
                
                if result.data and len(result.data) > 0:
                    return {
                        'exists': result.data[0]['exists'] if 'exists' in result.data[0] else result.data[0].get('"exists"', False), 
                        'content_id': result.data[0]['content_id']
                    }
            
            # Default response if no duplicate found
            return {'exists': False, 'content_id': None}
            
        except Exception as e:
            self.logger.error(f"Error checking for duplicates: {str(e)}")
            # If there's an error checking, assume no duplicate exists
            return {'exists': False, 'content_id': None}
    
    # --- Fetch API Processing ---
    
    async def process_fetch_result(self, content: str, url: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process content obtained from fetch operations
        
        Args:
            content: Text content of the webpage
            url: Source URL
            metadata: Optional metadata dictionary
            
        Returns:
            Dict with status and content information
        """
        try:
            if not content:
                raise ValueError("Content cannot be empty")

            if not url:
                raise ValueError("URL cannot be empty")
                
            # Clean URL
            url = url.strip()
            
            # Check if already exists
            duplicate_check = await self.check_for_duplicate('webpage', url)
            
            # Generate a title if one doesn't exist in metadata
            title = metadata.get('title', '') if metadata else ''
            if not title:
                # Extract title from HTML or use URL as fallback
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                title = title_match.group(1) if title_match else f"Content from {url}"
            
            # Generate content ID based on URL
            content_id = duplicate_check.get('content_id', None) or self.generate_content_id(url)
            
            # Use the upsert_webpage_content function
            source_file = metadata.get('source_file', None) if metadata else None
            
            result = self.supabase.rpc(
                'upsert_webpage_content',
                {
                    'p_content_id': content_id,
                    'p_title': title,
                    'p_url': url,
                    'p_content': content,
                    'p_source_file': source_file
                }
            ).execute()
            
            # Get the returned content ID
            returned_id = result.data if result.data else content_id
            
            if duplicate_check.get('exists', False):
                status_message = "Content updated - URL already exists in database"
            else:
                status_message = "Content successfully added to database"
                
            return {
                'status': 'success',
                'message': status_message,
                'content_id': returned_id,
                'title': title,
                'url': url,
                'is_duplicate': duplicate_check.get('exists', False)
            }
                
        except Exception as e:
            self.logger.error(f"Error processing web page: {str(e)}")
            return {
                'status': 'error',
                'message': f"Error processing content: {str(e)}"
            }
            
    # --- Combined Processing Method ---
    
    async def process_content(self, 
                           content: Union[str, bytes], 
                           file_path: str = None,
                           url: str = None,
                           metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Universal content processing method
        
        This method determines the content type and routes to the appropriate processor.
        
        Args:
            content: The content to process (string for text, bytes for binary)
            file_path: Path to the file if from local storage
            url: URL if from web fetch
            metadata: Additional metadata about the content
            
        Returns:
            dict: Result of the processing operation
        """
        try:
            source = file_path or url or "unknown"
            filename = os.path.basename(file_path) if file_path else (url.split('/')[-1] if url else "unknown")
            
            # Check if this is a duplicate before processing
            duplicate_type = None
            if url:
                duplicate_type = 'webpage'
                identifier = url
            elif file_path:
                # Determine content type for duplicate check
                if any(ext in filename.lower() for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.mp3', '.wav', '.ogg', '.flac', '.m4a']):
                    duplicate_type = 'media'
                    identifier = file_path
                else:
                    # For text content, we'll need to check during specific processing since we need content hash
                    pass
                    
            # Check for duplication if applicable
            if duplicate_type and identifier:
                duplicate_check = await self.check_for_duplicate(duplicate_type, identifier)
                if duplicate_check.get('exists', False) and metadata and not metadata.get('force_overwrite', False):
                    self.logger.info(f"Duplicate content found, skipping processing: {identifier}")
                    return {
                        'status': 'success',
                        'message': 'Content already exists in database',
                        'content_id': duplicate_check.get('content_id'),
                        'is_duplicate': True
                    }
            
            # Determine content type
            if isinstance(content, bytes):
                # Save binary content to temp file for processing
                temp_path = self.save_temp_binary(content, filename)
                if any(ext in filename.lower() for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
                    return await self.process_video(temp_path, metadata)
                elif any(ext in filename.lower() for ext in ['.mp3', '.wav', '.ogg', '.flac', '.m4a']):
                    return await self.process_audio(temp_path, metadata)
                else:
                    # Unknown binary format
                    raise ValueError(f"Unsupported binary content type: {filename}")
            
            # Text content handling
            if isinstance(content, str):
                content_type = self.detect_content_type(content, filename)
                
                if content_type == 'transcript':
                    return await self.upsert_transcript(content, filename, metadata.get('force_overwrite', False) if metadata else False)
                elif content_type == 'webpage':
                    return await self.process_fetch_result(content, url or "manual_upload", metadata)
                elif content_type in ['text', 'markdown', 'json']:
                    return await self.process_fetch_result(content, url or "manual_upload", metadata)
                else:
                    # Default to text
                    return await self.process_fetch_result(content, url or "manual_upload", metadata)
                
        except Exception as e:
            self.logger.error(f"Error processing content: {str(e)}")
            raise
    
    def save_temp_binary(self, content: bytes, filename: str) -> str:
        """Save binary content to temporary file"""
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), 'temp_media')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(content)
            
        return file_path

if __name__ == "__main__":
    upserter = MarkdownUpserter()
    
    directory = "transcripts"
    try:
        results = asyncio.run(upserter.process_directory('transcripts/', force_overwrite=False))
        
        # Print summary
        success_count = sum(1 for r in results if r.get('status') == 'success')
        error_count = sum(1 for r in results if r.get('status') == 'error')
        skipped_count = sum(1 for r in results if r.get('status') == 'skipped')
        
        print(f"\nProcessing Summary:")
        print(f"Total files: {len(results)}")
        print(f"Successfully processed: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Skipped: {skipped_count}")
        
        # Print errors if any
        if error_count > 0:
            print("\nErrors:")
            for result in results:
                if result.get('status') == 'error':
                    print(f"{result['filename']}: {result['error']}")
                    
    except Exception as e:
        print(f"Error processing directory: {str(e)}")
        raise