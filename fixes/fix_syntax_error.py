"""
Fix for syntax error in main.py after applying SSE fixes

This script fixes a syntax error in main.py that was introduced
by the SSE fixes. The error is on line 862, where there's an invalid syntax:
'yield error_msgexcept asyncio.QueueEmpty: pass'
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_syntax_error():
    """
    Fix the syntax error in main.py
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
        
        # Look for the syntax error pattern
        if "yield error_msgexcept asyncio.QueueEmpty:" in content:
            # Fix the syntax error by adding a newline
            fixed_content = content.replace(
                "yield error_msgexcept asyncio.QueueEmpty:",
                "yield error_msg\n                        except asyncio.QueueEmpty:"
            )
            
            # Write the fixed content back to the file
            with open(main_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            
            logger.info("Successfully fixed syntax error in main.py")
            return True
        else:
            logger.info("Syntax error pattern not found in main.py")
            return False
    
    except Exception as e:
        logger.error(f"Error fixing syntax error in main.py: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting syntax error fix...")
    success = fix_syntax_error()
    if success:
        logger.info("Syntax error fix completed successfully.")
    else:
        logger.warning("Syntax error fix failed or was not needed.")
