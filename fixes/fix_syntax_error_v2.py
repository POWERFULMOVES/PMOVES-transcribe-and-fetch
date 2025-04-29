"""
Fix for syntax errors in main.py after applying SSE fixes

This script fixes multiple syntax errors in main.py that were introduced
by the SSE fixes:
1. The error on line 862: 'yield error_msgexcept asyncio.QueueEmpty: pass'
2. The error on line 866: missing except or finally block for a try statement
"""

import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_syntax_errors():
    """
    Fix the syntax errors in main.py
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
        
        # Fix 1: The error on line 862
        if "yield error_msgexcept asyncio.QueueEmpty:" in content:
            content = content.replace(
                "yield error_msgexcept asyncio.QueueEmpty:",
                "yield error_msg\n                        except asyncio.QueueEmpty:"
            )
            logger.info("Fixed syntax error 1: Added newline between 'yield error_msg' and 'except'")
        
        # Fix 2: Find the try block without except or finally
        # Look for the pattern in the event_generator function
        event_generator_match = re.search(r'async def event_generator\(\):(.*?)(?=\n\s*response = EventSourceResponse)', content, re.DOTALL)
        if event_generator_match:
            event_generator_content = event_generator_match.group(1)
            
            # Find the problematic try block
            try_block_pattern = r'try:\s+transcription_update = transcription_q\.get_nowait\(\)(.*?)if update_sent:'
            try_block_match = re.search(try_block_pattern, event_generator_content, re.DOTALL)
            
            if try_block_match:
                try_block = try_block_match.group(0)
                
                # Check if it's missing the except block
                if "except asyncio.QueueEmpty:" not in try_block:
                    # Add the missing except block
                    fixed_try_block = try_block.replace(
                        "if update_sent:",
                        "                        except asyncio.QueueEmpty:\n                            pass\n\n                    if update_sent:"
                    )
                    
                    # Replace in the content
                    content = content.replace(try_block, fixed_try_block)
                    logger.info("Fixed syntax error 2: Added missing 'except asyncio.QueueEmpty:' block")
        
        # Write the fixed content back to the file
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info("Successfully fixed syntax errors in main.py")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing syntax errors in main.py: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting syntax error fixes...")
    success = fix_syntax_errors()
    if success:
        logger.info("Syntax error fixes completed successfully.")
    else:
        logger.warning("Syntax error fixes failed or were not needed.")
