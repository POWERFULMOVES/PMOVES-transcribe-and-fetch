"""
Fix for specific syntax error in main.py

This script only fixes the specific syntax error in the event_generator function
without making widespread changes to the codebase.
"""

import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_specific_syntax_error():
    """
    Fix only the specific syntax error in main.py
    """
    try:
        # Path to main.py
        main_path = Path("backend/app/main.py")
        
        # Check if the file exists
        if not main_path.exists():
            logger.error(f"Error: {main_path} not found")
            return False
        
        logger.info(f"Reading file: {main_path}")
        
        # Read the current content
        with open(main_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        logger.info(f"File size: {len(content)} bytes")
        
        # Create a backup of the original file
        backup_path = main_path.with_suffix(".py.bak")
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Created backup at: {backup_path}")
        
        # Fix the specific error in the event_generator function
        event_generator_match = re.search(r'async def event_generator\(\):(.*?)(?=\n\s*response = EventSourceResponse)', content, re.DOTALL)
        if not event_generator_match:
            logger.error("Could not find event_generator function")
            return False
        
        event_generator_content = event_generator_match.group(0)
        
        # Look for the specific error pattern
        error_pattern = r'yield error_msgexcept asyncio\.QueueEmpty:'
        if re.search(error_pattern, event_generator_content):
            logger.info("Found syntax error: 'yield error_msgexcept asyncio.QueueEmpty:'")
            
            # Fix the error by adding a newline
            fixed_content = content.replace(
                'yield error_msgexcept asyncio.QueueEmpty:',
                'yield error_msg\n                        except asyncio.QueueEmpty:'
            )
            
            # Write the fixed content back to the file
            with open(main_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            
            logger.info("Successfully fixed specific syntax error in main.py")
            return True
        else:
            logger.info("Specific syntax error not found or already fixed")
            
            # Check for the missing except block in the try block
            try_block_pattern = r'try:\s+transcription_update = transcription_q\.get_nowait\(\)(.*?)(?=\n\s+if update_sent:)'
            try_block_match = re.search(try_block_pattern, event_generator_content, re.DOTALL)
            
            if try_block_match and "except" not in try_block_match.group(0):
                logger.info("Found try block without except in event_generator function")
                
                # Fix the error by adding the missing except block
                fixed_content = content.replace(
                    try_block_match.group(0),
                    try_block_match.group(0) + "\n                        except asyncio.QueueEmpty:\n                            pass"
                )
                
                # Write the fixed content back to the file
                with open(main_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                
                logger.info("Successfully fixed missing except block in main.py")
                return True
            else:
                logger.info("No specific syntax errors found that need fixing")
                return False
    
    except Exception as e:
        logger.error(f"Error fixing syntax error in main.py: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting specific syntax error fix...")
    success = fix_specific_syntax_error()
    if success:
        logger.info("Specific syntax error fix completed successfully.")
    else:
        logger.warning("Specific syntax error fix failed or was not needed.")
