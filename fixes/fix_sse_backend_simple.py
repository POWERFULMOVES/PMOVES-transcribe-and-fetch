"""
Fix for SSE backend issues with download status updates

This script modifies the download_audio function in transcribe1.py to ensure
status updates are properly sent during the download process, and fixes the
event_generator function in main.py to properly handle and format SSE messages.
"""

import asyncio
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fix_download_audio_function():
    """
    Fix the download_audio function in transcribe1.py to ensure status updates
    are properly sent during the download process.
    """
    try:
        # Path to transcribe1.py
        transcribe1_path = Path("backend/app/transcribe1.py")
        
        # Read the current content
        with open(transcribe1_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if the file already contains our fix
        if "# Enhanced download progress reporting" in content:
            logger.info("download_audio function already fixed. Skipping.")
            return
        
        # Find the download_audio function
        if "async def download_audio" not in content:
            logger.error("Could not find download_audio function in transcribe1.py")
            return
        
        # Modify the download_audio function to ensure progress updates are sent
        # Look for the sync_progress_hook function within download_audio
        if "def sync_progress_hook" in content:
            # Replace the sync_progress_hook function with our enhanced version
            old_hook = """            def sync_progress_hook(d):
                nonlocal last_progress_sent_local # Modify the variable in the outer scope
                if d['status'] == 'downloading':
                    try:
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        downloaded = d.get('downloaded_bytes', 0)
                        if total > 0:
                            current_progress = round((downloaded / total) * 100, 1)
                            # Send update if progress changed significantly
                            if should_send_progress_update(last_progress_sent_local, current_progress, threshold=5.0):
                                asyncio.run_coroutine_threadsafe(progress_callback(current_progress), loop)
                                last_progress_sent_local = current_progress # Update last sent progress
                                
                    except Exception as e:
                        logger.error(f"Error in download progress hook: {str(e)}")
                elif d['status'] == 'finished':
                     # Ensure 100% is sent on completion
                     if last_progress_sent_local < 100.0:
                          asyncio.run_coroutine_threadsafe(progress_callback(100.0), loop)"""
            
            new_hook = """            # Enhanced download progress reporting
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
            
            # Replace the old hook with the new one
            content = content.replace(old_hook, new_hook)
            
            # Write the modified content back to the file
            with open(transcribe1_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info("Successfully fixed download_audio function in transcribe1.py")
        else:
            logger.error("Could not find sync_progress_hook function in download_audio")
    
    except Exception as e:
        logger.error(f"Error fixing download_audio function: {e}")

async def fix_event_generator_function():
    """
    Fix the event_generator function in main.py to properly handle and format SSE messages.
    """
    try:
        # Path to main.py
        main_path = Path("backend/app/main.py")
        
        # Read the current content
        with open(main_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if the file already contains our fix
        if "# Enhanced SSE message handling" in content:
            logger.info("event_generator function already fixed. Skipping.")
            return
        
        # Find the event_generator function in the combined-updates endpoint
        if "async def event_generator():" not in content:
            logger.error("Could not find event_generator function in main.py")
            return
        
        # Find the section where status updates are processed
        status_update_section = """                    try:
                        status_update = status_q.get_nowait()
                        logger.debug(f"SSE (Combined): Sending status: {str(status_update)[:100]}...")
                        try:
                            update_data = json.loads(status_update) # Assumes JSON string in queue
                            if 'type' not in update_data: update_data['type'] = 'status'
                            sse_msg = f"data: {json.dumps(update_data)}\\n\\n"
                            logger.info(f"SSE SEND (Status): {json.dumps(update_data)}") # Log before yield
                            yield sse_msg
                        except (json.JSONDecodeError, TypeError):
                             sse_msg = format_sse_message('status', status_update) # Send as plain if not JSON
                             logger.info(f"SSE SEND (Status - Plain): {status_update}") # Log before yield
                             yield sse_msg
                        status_q.task_done()
                        update_sent = True
                    except asyncio.QueueEmpty: pass"""
        
        enhanced_status_update_section = """                    # Enhanced SSE message handling
                    try:
                        status_update = status_q.get_nowait()
                        logger.debug(f"SSE (Combined): Sending status: {str(status_update)[:100]}...")
                        try:
                            # Parse JSON string from queue
                            update_data = json.loads(status_update)
                            
                            # Ensure type field exists
                            if 'type' not in update_data:
                                update_data['type'] = 'status'
                                
                            # Add timestamp if missing
                            if 'timestamp' not in update_data:
                                from datetime import datetime
                                update_data['timestamp'] = datetime.now().isoformat()
                                
                            # Format as SSE message
                            sse_msg = f"data: {json.dumps(update_data)}\\n\\n"
                            
                            # Log before yielding
                            if 'content' in update_data and 'Downloading audio:' in str(update_data['content']):
                                # Special handling for download progress updates
                                logger.info(f"SSE SEND (Download Progress): {update_data['content']}")
                            else:
                                logger.info(f"SSE SEND (Status): {json.dumps(update_data)}")
                                
                            # Send to client
                            yield sse_msg
                        except (json.JSONDecodeError, TypeError):
                             # Send as plain text if not valid JSON
                             sse_msg = format_sse_message('status', status_update)
                             logger.info(f"SSE SEND (Status - Plain): {status_update}")
                             yield sse_msg
                             
                        # Mark task as done
                        status_q.task_done()
                        update_sent = True
                    except asyncio.QueueEmpty:
                        # No status updates in queue
                        pass"""
        
        # Replace the status update section with the enhanced version
        if status_update_section in content:
            content = content.replace(status_update_section, enhanced_status_update_section)
            
            # Write the modified content back to the file
            with open(main_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info("Successfully fixed event_generator function in main.py")
        else:
            logger.error("Could not find status update section in event_generator function")
    
    except Exception as e:
        logger.error(f"Error fixing event_generator function: {e}")

async def main():
    """
    Main function to apply all fixes.
    """
    logger.info("Starting SSE backend fixes...")
    
    # Fix download_audio function in transcribe1.py
    await fix_download_audio_function()
    
    # Fix event_generator function in main.py
    await fix_event_generator_function()
    
    logger.info("SSE backend fixes completed.")

if __name__ == "__main__":
    asyncio.run(main())
