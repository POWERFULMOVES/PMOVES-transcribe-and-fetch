"""
Force update for SSE transcription segment updates

This script forces updates to the transcribe_audio function in transcribe1.py
and the event_generator function in main.py to ensure transcription segments
are properly sent to the frontend in real-time.

Unlike the previous fix scripts, this script will force the updates even if
the files appear to already have been fixed.
"""

import asyncio
import json
import logging
import re
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def force_fix_transcribe_audio_function():
    """
    Force fix the transcribe_audio function in transcribe1.py to ensure transcription
    segments are properly sent to the frontend in real-time.
    """
    try:
        # Path to transcribe1.py
        transcribe1_path = Path("backend/app/transcribe1.py")
        
        # Read the current content
        with open(transcribe1_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the transcribe_audio function
        transcribe_audio_match = re.search(r'async def transcribe_audio\([^)]*\):(.*?)(?=\n\w)', content, re.DOTALL)
        if not transcribe_audio_match:
            logger.error("Could not find transcribe_audio function in transcribe1.py")
            return False
        
        transcribe_audio_function = transcribe_audio_match.group(0)
        
        # Check if the function contains the segment processing section
        segment_processing_match = re.search(r'for idx, segment in enumerate\(segments_gen\):(.*?)(?=\n\s*# Create final markdown)', transcribe_audio_function, re.DOTALL)
        if not segment_processing_match:
            logger.error("Could not find segment processing section in transcribe_audio function")
            return False
        
        segment_processing_section = segment_processing_match.group(1)
        
        # Check if the section already contains our status update code
        if "# Send status update for EVERY segment" in segment_processing_section:
            # Replace the existing status update code with our enhanced version
            enhanced_status_update = """                # Send status update for EVERY segment to ensure continuous updates
                status_msg = {
                    "type": "status", 
                    "content": f"Transcribing segment {idx + 1}...",
                    "timestamp": datetime.now().isoformat()
                }
                await status_queue.put(json.dumps(status_msg))
                logger.info(f"📢 STATUS UPDATE: Transcribing segment {idx + 1}")
                
                # Add a small delay to prevent overwhelming the event loop
                await asyncio.sleep(0.01)"""
            
            # Use regex to replace the existing status update code
            updated_section = re.sub(
                r'# Send status update for EVERY segment.*?await asyncio\.sleep\(0\.01\)',
                enhanced_status_update,
                segment_processing_section,
                flags=re.DOTALL
            )
        else:
            # Look for any existing status update code
            status_update_match = re.search(r'# Send status updates.*?status_queue\.put\(.*?\)', segment_processing_section, re.DOTALL)
            if status_update_match:
                # Replace the existing status update code with our enhanced version
                enhanced_status_update = """                # Send status update for EVERY segment to ensure continuous updates
                status_msg = {
                    "type": "status", 
                    "content": f"Transcribing segment {idx + 1}...",
                    "timestamp": datetime.now().isoformat()
                }
                await status_queue.put(json.dumps(status_msg))
                logger.info(f"📢 STATUS UPDATE: Transcribing segment {idx + 1}")
                
                # Add a small delay to prevent overwhelming the event loop
                await asyncio.sleep(0.01)"""
                
                updated_section = segment_processing_section.replace(status_update_match.group(0), enhanced_status_update)
            else:
                # If no status update code is found, add it after the segment_panel code
                segment_panel_match = re.search(r'segment_panel = Panel\(.*?\)', segment_processing_section, re.DOTALL)
                if segment_panel_match:
                    panel_end_pos = segment_processing_section.find(segment_panel_match.group(0)) + len(segment_panel_match.group(0))
                    updated_section = (
                        segment_processing_section[:panel_end_pos] + 
                        "\n\n                # Send status update for EVERY segment to ensure continuous updates\n" +
                        "                status_msg = {\n" +
                        '                    "type": "status", \n' +
                        '                    "content": f"Transcribing segment {idx + 1}...",\n' +
                        '                    "timestamp": datetime.now().isoformat()\n' +
                        "                }\n" +
                        "                await status_queue.put(json.dumps(status_msg))\n" +
                        '                logger.info(f"📢 STATUS UPDATE: Transcribing segment {idx + 1}")\n' +
                        "                \n" +
                        "                # Add a small delay to prevent overwhelming the event loop\n" +
                        "                await asyncio.sleep(0.01)" +
                        segment_processing_section[panel_end_pos:]
                    )
                else:
                    logger.error("Could not find appropriate location to add status update code")
                    return False
        
        # Replace the segment processing section in the transcribe_audio function
        updated_function = transcribe_audio_function.replace(segment_processing_section, updated_section)
        
        # Replace the transcribe_audio function in the content
        updated_content = content.replace(transcribe_audio_function, updated_function)
        
        # Write the updated content back to the file
        with open(transcribe1_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        logger.info("Successfully forced fix for transcribe_audio function in transcribe1.py")
        return True
    
    except Exception as e:
        logger.error(f"Error forcing fix for transcribe_audio function: {e}")
        return False

async def force_fix_event_generator_function():
    """
    Force fix the event_generator function in main.py to properly handle and format SSE messages.
    """
    try:
        # Path to main.py
        main_path = Path("backend/app/main.py")
        
        # Read the current content
        with open(main_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the event_generator function in the combined-updates endpoint
        event_generator_match = re.search(r'async def event_generator\(\):(.*?)(?=\n\s*response = EventSourceResponse)', content, re.DOTALL)
        if not event_generator_match:
            logger.error("Could not find event_generator function in main.py")
            return False
        
        event_generator_function = event_generator_match.group(0)
        
        # Find the section where transcription updates are processed
        transcription_update_match = re.search(r'try:\s+transcription_update = transcription_q\.get_nowait\(\)(.*?)except asyncio\.QueueEmpty:', event_generator_function, re.DOTALL)
        if not transcription_update_match:
            logger.error("Could not find transcription update section in event_generator function")
            return False
        
        transcription_update_section = transcription_update_match.group(1)
        
        # Enhanced transcription update section
        enhanced_transcription_update = """
                        logger.debug(f"SSE (Combined): Sending transcription: {str(transcription_update)[:100]}...")
                        try:
                             # First try to parse as JSON
                             try:
                                 update_data = json.loads(transcription_update) # Assumes JSON string
                                 
                                 # Ensure it has a type field
                                 if 'type' not in update_data: 
                                     update_data['type'] = 'transcription_segment'
                                 
                                 # Ensure content is an object, not a string
                                 if 'content' in update_data and isinstance(update_data['content'], str):
                                     try:
                                         # Try to parse content as JSON if it's a string
                                         content_obj = json.loads(update_data['content'])
                                         update_data['content'] = content_obj
                                     except (json.JSONDecodeError, TypeError):
                                         # If parsing fails, keep as is but wrap in an object
                                         update_data['content'] = {'text': update_data['content']}
                                 
                                 # Format as SSE message
                                 sse_msg = f"data: {json.dumps(update_data)}\\n\\n"
                                 
                                 # Enhanced logging with more details
                                 if update_data['type'] == 'transcription_segment':
                                     content_obj = update_data.get('content', {})
                                     if isinstance(content_obj, dict):
                                         segment_text = content_obj.get('text', 'No text')[:50]
                                         segment_id = content_obj.get('id', 'No ID')
                                         logger.info(f"SSE SEND (Transcription): ID={segment_id}, Text=\\"{segment_text}...\\"")
                                     else:
                                         logger.info(f"SSE SEND (Transcription): Content is not a dict: {type(content_obj)}")
                                 else:
                                     logger.info(f"SSE SEND (Other): Type={update_data['type']}")
                                 
                                 yield sse_msg
                                 
                             except (json.JSONDecodeError, TypeError) as e:
                                 # If JSON parsing fails, format as a plain message
                                 logger.info(f"SSE SEND (Transcription - Plain): {transcription_update[:100]}... (Error: {e})")
                                 sse_msg = format_sse_message('transcription_segment', {'text': transcription_update})
                                 yield sse_msg
                        except Exception as e:
                             # Catch any other errors to prevent the SSE stream from breaking
                             logger.error(f"Error formatting SSE message: {e}")
                             error_msg = format_sse_message('error', f"Error formatting message: {str(e)}")
                             yield error_msg"""
        
        # Replace the transcription update section
        updated_function = event_generator_function.replace(transcription_update_section, enhanced_transcription_update)
        
        # Replace the event_generator function in the content
        updated_content = content.replace(event_generator_function, updated_function)
        
        # Write the updated content back to the file
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        logger.info("Successfully forced fix for event_generator function in main.py")
        return True
    
    except Exception as e:
        logger.error(f"Error forcing fix for event_generator function: {e}")
        return False

async def force_fix_download_audio_function():
    """
    Force fix the download_audio function in transcribe1.py to ensure status updates
    are properly sent during the download process.
    """
    try:
        # Path to transcribe1.py
        transcribe1_path = Path("backend/app/transcribe1.py")
        
        # Read the current content
        with open(transcribe1_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the download_audio function
        download_audio_match = re.search(r'async def download_audio\([^)]*\):(.*?)(?=\n\w)', content, re.DOTALL)
        if not download_audio_match:
            logger.error("Could not find download_audio function in transcribe1.py")
            return False
        
        download_audio_function = download_audio_match.group(0)
        
        # Find the sync_progress_hook function within download_audio
        sync_progress_hook_match = re.search(r'def sync_progress_hook\(d\):(.*?)(?=\n\s+ydl_opts\[\'progress_hooks\'])', download_audio_function, re.DOTALL)
        if not sync_progress_hook_match:
            logger.error("Could not find sync_progress_hook function in download_audio")
            return False
        
        sync_progress_hook_function = sync_progress_hook_match.group(0)
        
        # Enhanced sync_progress_hook function
        enhanced_sync_progress_hook = """            # Enhanced download progress reporting
            def sync_progress_hook(d):
                nonlocal last_progress_sent_local # Modify the variable in the outer scope
                if d['status'] == 'downloading':
                    try:
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        downloaded = d.get('downloaded_bytes', 0)
                        if total > 0:
                            current_progress = round((downloaded / total) * 100, 1)
                            
                            # Send more frequent updates during download (every 2%)
                            if abs(current_progress - last_progress_sent_local) >= 2.0:
                                # Log the progress update
                                logger.info(f"Download progress: {current_progress:.1f}% ({downloaded/(1024*1024):.1f}MB/{total/(1024*1024):.1f}MB)")
                                
                                # Send update to frontend
                                asyncio.run_coroutine_threadsafe(progress_callback(current_progress), loop)
                                last_progress_sent_local = current_progress # Update last sent progress
                                
                    except Exception as e:
                        logger.error(f"Error in download progress hook: {str(e)}")
                elif d['status'] == 'finished':
                     # Ensure 100% is sent on completion
                     if last_progress_sent_local < 100.0:
                          logger.info(f"Download complete: 100%")
                          asyncio.run_coroutine_threadsafe(progress_callback(100.0), loop)"""
        
        # Replace the sync_progress_hook function
        updated_function = download_audio_function.replace(sync_progress_hook_function, enhanced_sync_progress_hook)
        
        # Replace the download_audio function in the content
        updated_content = content.replace(download_audio_function, updated_function)
        
        # Write the updated content back to the file
        with open(transcribe1_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        logger.info("Successfully forced fix for download_audio function in transcribe1.py")
        return True
    
    except Exception as e:
        logger.error(f"Error forcing fix for download_audio function: {e}")
        return False

async def main():
    """
    Main function to apply all forced fixes.
    """
    logger.info("Starting forced SSE fixes...")
    
    # Force fix download_audio function in transcribe1.py
    download_audio_fixed = await force_fix_download_audio_function()
    
    # Force fix transcribe_audio function in transcribe1.py
    transcribe_audio_fixed = await force_fix_transcribe_audio_function()
    
    # Force fix event_generator function in main.py
    event_generator_fixed = await force_fix_event_generator_function()
    
    if download_audio_fixed and transcribe_audio_fixed and event_generator_fixed:
        logger.info("All forced SSE fixes completed successfully.")
    else:
        logger.warning("Some forced SSE fixes failed. Check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main())
