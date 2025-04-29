"""
SSE Backend Connection Checker

This script checks if the backend is properly sending SSE messages
by adding debug logging to the main.py and transcribe1.py files.
"""

import asyncio
import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def add_debug_logging_to_main():
    """
    Add debug logging to the event_generator function in main.py
    """
    try:
        # Path to main.py
        main_path = Path("backend/app/main.py")
        
        # Check if the file exists
        if not main_path.exists():
            logger.error(f"Error: {main_path} not found")
            return False
        
        # Read the current content
        with open(main_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if debug logging is already added
        if "# SSE BACKEND DEBUG LOGGING" in content:
            logger.info("Debug logging already added to main.py")
            return True
        
        # Find the event_generator function in the combined-updates endpoint
        event_generator_match = re.search(r'async def event_generator\(\):(.*?)(?=\n\s*response = EventSourceResponse)', content, re.DOTALL)
        if not event_generator_match:
            logger.error("Could not find event_generator function in main.py")
            return False
        
        event_generator_function = event_generator_match.group(0)
        
        # Add debug logging to the beginning of the function
        updated_function = event_generator_function.replace(
            "async def event_generator():",
            """async def event_generator():
            # SSE BACKEND DEBUG LOGGING
            logger.info("SSE event_generator started")"""
        )
        
        # Add debug logging to the status queue section
        status_queue_section = re.search(r'try:\s+status_update = status_q\.get_nowait\(\)(.*?)except asyncio\.QueueEmpty:', updated_function, re.DOTALL)
        if status_queue_section:
            status_section = status_queue_section.group(0)
            updated_status_section = status_section.replace(
                "try:",
                """try:
                    # SSE BACKEND DEBUG LOGGING
                    logger.info("Checking status queue for updates")"""
            )
            updated_status_section = updated_status_section.replace(
                "status_update = status_q.get_nowait()",
                """status_update = status_q.get_nowait()
                        # SSE BACKEND DEBUG LOGGING
                        logger.info(f"Got status update from queue: {status_update[:100]}...")"""
            )
            updated_function = updated_function.replace(status_section, updated_status_section)
        
        # Add debug logging to the transcription queue section
        transcription_queue_section = re.search(r'try:\s+transcription_update = transcription_q\.get_nowait\(\)(.*?)except asyncio\.QueueEmpty:', updated_function, re.DOTALL)
        if transcription_queue_section:
            transcription_section = transcription_queue_section.group(0)
            updated_transcription_section = transcription_section.replace(
                "try:",
                """try:
                    # SSE BACKEND DEBUG LOGGING
                    logger.info("Checking transcription queue for updates")"""
            )
            updated_transcription_section = updated_transcription_section.replace(
                "transcription_update = transcription_q.get_nowait()",
                """transcription_update = transcription_q.get_nowait()
                        # SSE BACKEND DEBUG LOGGING
                        logger.info(f"Got transcription update from queue: {transcription_update[:100]}...")"""
            )
            updated_function = updated_function.replace(transcription_section, updated_transcription_section)
        
        # Replace the event_generator function in the content
        updated_content = content.replace(event_generator_function, updated_function)
        
        # Write the updated content back to the file
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        logger.info("Successfully added debug logging to event_generator function in main.py")
        return True
    
    except Exception as e:
        logger.error(f"Error adding debug logging to main.py: {e}")
        return False

async def add_debug_logging_to_transcribe1():
    """
    Add debug logging to the transcribe_audio function in transcribe1.py
    """
    try:
        # Path to transcribe1.py
        transcribe1_path = Path("backend/app/transcribe1.py")
        
        # Check if the file exists
        if not transcribe1_path.exists():
            logger.error(f"Error: {transcribe1_path} not found")
            return False
        
        # Read the current content
        with open(transcribe1_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if debug logging is already added
        if "# TRANSCRIBE1 DEBUG LOGGING" in content:
            logger.info("Debug logging already added to transcribe1.py")
            return True
        
        # Find the transcribe_audio function
        transcribe_audio_match = re.search(r'async def transcribe_audio\([^)]*\):(.*?)(?=\n\w)', content, re.DOTALL)
        if not transcribe_audio_match:
            logger.error("Could not find transcribe_audio function in transcribe1.py")
            return False
        
        transcribe_audio_function = transcribe_audio_match.group(0)
        
        # Add debug logging to the beginning of the function
        updated_function = transcribe_audio_function.replace(
            "async def transcribe_audio",
            """async def transcribe_audio"""
        )
        
        # Add debug logging after the function signature
        updated_function = updated_function.replace(
            "try:",
            """try:
        # TRANSCRIBE1 DEBUG LOGGING
        logger.info("transcribe_audio function started")"""
        )
        
        # Add debug logging to the segment processing section
        segment_processing_match = re.search(r'for idx, segment in enumerate\(segments_gen\):(.*?)(?=\n\s*# Create final markdown)', updated_function, re.DOTALL)
        if segment_processing_match:
            segment_processing_section = segment_processing_match.group(0)
            
            # Add debug logging to the segment processing loop
            updated_segment_section = segment_processing_section.replace(
                "for idx, segment in enumerate(segments_gen):",
                """for idx, segment in enumerate(segments_gen):
                # TRANSCRIBE1 DEBUG LOGGING
                logger.info(f"Processing segment {idx}")"""
            )
            
            # Add debug logging before sending segment to queue
            segment_queue_match = re.search(r'await transcription_queue\.put\(json\.dumps\(segment_data\)\)', updated_segment_section)
            if segment_queue_match:
                segment_queue_line = segment_queue_match.group(0)
                updated_segment_queue_line = f"""                # TRANSCRIBE1 DEBUG LOGGING
                logger.info(f"Sending segment {idx} to transcription queue")
                {segment_queue_line}
                # TRANSCRIBE1 DEBUG LOGGING
                logger.info(f"Segment {idx} sent to transcription queue")"""
                updated_segment_section = updated_segment_section.replace(segment_queue_line, updated_segment_queue_line)
            
            updated_function = updated_function.replace(segment_processing_section, updated_segment_section)
        
        # Replace the transcribe_audio function in the content
        updated_content = content.replace(transcribe_audio_function, updated_function)
        
        # Write the updated content back to the file
        with open(transcribe1_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        logger.info("Successfully added debug logging to transcribe_audio function in transcribe1.py")
        return True
    
    except Exception as e:
        logger.error(f"Error adding debug logging to transcribe1.py: {e}")
        return False

async def main():
    """
    Main function to add debug logging to backend files.
    """
    logger.info("Starting SSE backend connection checker...")
    
    # Add debug logging to main.py
    main_success = await add_debug_logging_to_main()
    
    # Add debug logging to transcribe1.py
    transcribe1_success = await add_debug_logging_to_transcribe1()
    
    if main_success and transcribe1_success:
        logger.info("Successfully added debug logging to backend files")
        
        # Print instructions
        print("\nSSE backend connection checker complete.")
        print("To test:")
        print("1. Start the backend server: cd backend && uvicorn app.main:app --reload --port 8000")
        print("2. Start the frontend server: npm run dev")
        print("3. Open the browser console and navigate to http://localhost:3000")
        print("4. Start a transcription and check the backend logs for SSE messages")
        print("5. Look for any errors or missing messages in the backend logs")
    else:
        logger.warning("Some debug logging additions failed. Check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main())
