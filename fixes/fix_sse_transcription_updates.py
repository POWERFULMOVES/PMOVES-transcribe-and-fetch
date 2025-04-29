"""
Fix for SSE transcription segment updates not showing during transcription

This script modifies the transcribe_audio function in transcribe1.py to ensure
transcription segments are properly sent to the frontend in real-time during
the transcription process.
"""

import asyncio
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fix_transcribe_audio_function():
    """
    Fix the transcribe_audio function in transcribe1.py to ensure transcription
    segments are properly sent to the frontend in real-time.
    """
    try:
        # Path to transcribe1.py
        transcribe1_path = Path("backend/app/transcribe1.py")
        
        # Read the current content
        with open(transcribe1_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if the file already contains our fix
        if "# Send status update for EVERY segment" in content:
            logger.info("transcribe_audio function already fixed. Skipping.")
            return
        
        # Find the section where status updates are sent
        status_update_section = """                # Send status updates less frequently (e.g., every 10 segments or based on time)
                if idx % 10 == 0: # Example: Update every 10 segments
                    status_msg = {"type": "status", "content": f"Transcribed segment {idx + 1}..."}
                    await status_queue.put(json.dumps(status_msg))
                    logger.info(f"📢 STATUS UPDATE: {status_msg['content']}") # Enhanced status logging"""
        
        enhanced_status_update_section = """                # Send status update for EVERY segment to ensure continuous updates
                status_msg = {
                    "type": "status", 
                    "content": f"Transcribing segment {idx + 1}...",
                    "timestamp": datetime.now().isoformat()
                }
                await status_queue.put(json.dumps(status_msg))
                logger.info(f"📢 STATUS UPDATE: Transcribing segment {idx + 1}")
                
                # Add a small delay to prevent overwhelming the event loop
                await asyncio.sleep(0.01)"""
        
        # Replace the status update section with the enhanced version
        if status_update_section in content:
            content = content.replace(status_update_section, enhanced_status_update_section)
            
            # Write the modified content back to the file
            with open(transcribe1_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info("Successfully fixed transcribe_audio function in transcribe1.py")
        else:
            logger.error("Could not find status update section in transcribe_audio function")
    
    except Exception as e:
        logger.error(f"Error fixing transcribe_audio function: {e}")

async def main():
    """
    Main function to apply all fixes.
    """
    logger.info("Starting SSE transcription segment fixes...")
    
    # Fix transcribe_audio function in transcribe1.py
    await fix_transcribe_audio_function()
    
    logger.info("SSE transcription segment fixes completed.")

if __name__ == "__main__":
    asyncio.run(main())
