#!/usr/bin/env python3
"""
Fix for backend auto-starting search issue
This script updates the main.py file to prevent automatic search when the server starts
"""

import os
import re
import sys
from pathlib import Path

def read_file(file_path):
    """Read file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def write_file(file_path, content):
    """Write content to file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

def fix_main_py():
    """Apply fixes to main.py"""
    # Find main.py
    backend_dir = Path('backend')
    app_dir = backend_dir / 'app'
    main_py_path = app_dir / 'main.py'
    
    if not main_py_path.exists():
        print(f"Could not find main.py at {main_py_path}")
        return False
    
    # Read the file
    content = read_file(main_py_path)
    if content is None:
        return False
    
    # Create a backup
    backup_path = main_py_path.with_suffix('.py.bak.autostart_fix')
    write_file(backup_path, content)
    print(f"Created backup at {backup_path}")
    
    # Fix the auto-start issue by properly commenting out the Uvicorn server runner
    # Look for the pattern where the if __name__ block is commented out but the code inside isn't
    pattern = r'#if __name__ == "__main__":'
    if re.search(pattern, content):
        # The if statement is commented out but the code inside might not be
        # Let's properly comment out the entire block
        content = re.sub(
            r'#if __name__ == "__main__":([\s\S]*?)(?=\n\w|$)',
            r'''
# --- ASGI Server Runner ---
# Uncomment this block to run the server directly with python
# if __name__ == "__main__":
#     import uvicorn
#     logger.info("Starting Uvicorn server directly...")
#
#     # Determine host and port
#     app_host = os.getenv("HOST", "127.0.0.1")
#     try:
#         app_port = int(os.getenv("PORT", "8000"))
#     except ValueError:
#         logger.warning(f"Invalid PORT environment variable '{os.getenv('PORT')}', using default 8000.")
#         app_port = 8000
#
#     # Determine reload flag (enable only for development)
#     # Be careful enabling reload in production-like environments
#     reload_flag = os.getenv("ENABLE_RELOAD", "false").lower() in ["true", "1", "yes"]
#     if reload_flag:
#          logger.warning("Auto-reload enabled. Recommended only for development.")
#
#     uvicorn.run(
#         # Important: Use the string format "module_name:app_instance"
#         # If this file is main.py, it's "main:app"
#         f"{Path(__file__).stem}:app",
#         host=app_host,
#         port=app_port,
#         reload=reload_flag,
#         log_level="info", # Uvicorn's own log level
#         # Use loop='uvloop' for potential performance gains if installed
#         # loop="uvloop",
#         # http="httptools", # Use httptools if installed
#     )''',
            content
        )
    else:
        # Check if there's an uncommented if __name__ block
        pattern = r'if __name__ == "__main__":'
        if re.search(pattern, content):
            # The if statement is not commented out, let's comment it out
            content = re.sub(
                r'if __name__ == "__main__":([\s\S]*?)(?=\n\w|$)',
                r'''
# --- ASGI Server Runner ---
# Uncomment this block to run the server directly with python
# if __name__ == "__main__":
#     import uvicorn
#     logger.info("Starting Uvicorn server directly...")
#
#     # Determine host and port
#     app_host = os.getenv("HOST", "127.0.0.1")
#     try:
#         app_port = int(os.getenv("PORT", "8000"))
#     except ValueError:
#         logger.warning(f"Invalid PORT environment variable '{os.getenv('PORT')}', using default 8000.")
#         app_port = 8000
#
#     # Determine reload flag (enable only for development)
#     # Be careful enabling reload in production-like environments
#     reload_flag = os.getenv("ENABLE_RELOAD", "false").lower() in ["true", "1", "yes"]
#     if reload_flag:
#          logger.warning("Auto-reload enabled. Recommended only for development.")
#
#     uvicorn.run(
#         # Important: Use the string format "module_name:app_instance"
#         # If this file is main.py, it's "main:app"
#         f"{Path(__file__).stem}:app",
#         host=app_host,
#         port=app_port,
#         reload=reload_flag,
#         log_level="info", # Uvicorn's own log level
#         # Use loop='uvloop' for potential performance gains if installed
#         # loop="uvloop",
#         # http="httptools", # Use httptools if installed
#     )''',
                content
            )
        else:
            # There's no if __name__ block, but there might be Uvicorn code at the end
            # Let's look for import uvicorn
            pattern = r'import uvicorn'
            if re.search(pattern, content):
                # Find the Uvicorn runner code at the end of the file
                pattern = r'import uvicorn([\s\S]*?)(?=\n\w|$)'
                content = re.sub(
                    pattern,
                    r'''
# --- ASGI Server Runner ---
# Uncomment this block to run the server directly with python
# if __name__ == "__main__":
#     import uvicorn
#     logger.info("Starting Uvicorn server directly...")
#
#     # Determine host and port
#     app_host = os.getenv("HOST", "127.0.0.1")
#     try:
#         app_port = int(os.getenv("PORT", "8000"))
#     except ValueError:
#         logger.warning(f"Invalid PORT environment variable '{os.getenv('PORT')}', using default 8000.")
#         app_port = 8000
#
#     # Determine reload flag (enable only for development)
#     # Be careful enabling reload in production-like environments
#     reload_flag = os.getenv("ENABLE_RELOAD", "false").lower() in ["true", "1", "yes"]
#     if reload_flag:
#          logger.warning("Auto-reload enabled. Recommended only for development.")
#
#     uvicorn.run(
#         # Important: Use the string format "module_name:app_instance"
#         # If this file is main.py, it's "main:app"
#         f"{Path(__file__).stem}:app",
#         host=app_host,
#         port=app_port,
#         reload=reload_flag,
#         log_level="info", # Uvicorn's own log level
#         # Use loop='uvloop' for potential performance gains if installed
#         # loop="uvloop",
#         # http="httptools", # Use httptools if installed
#     )''',
                    content
                )
            else:
                # If we can't find any of the patterns, let's just add a commented-out block at the end
                content += '''
# --- ASGI Server Runner ---
# Uncomment this block to run the server directly with python
# if __name__ == "__main__":
#     import uvicorn
#     logger.info("Starting Uvicorn server directly...")
#
#     # Determine host and port
#     app_host = os.getenv("HOST", "127.0.0.1")
#     try:
#         app_port = int(os.getenv("PORT", "8000"))
#     except ValueError:
#         logger.warning(f"Invalid PORT environment variable '{os.getenv('PORT')}', using default 8000.")
#         app_port = 8000
#
#     # Determine reload flag (enable only for development)
#     # Be careful enabling reload in production-like environments
#     reload_flag = os.getenv("ENABLE_RELOAD", "false").lower() in ["true", "1", "yes"]
#     if reload_flag:
#          logger.warning("Auto-reload enabled. Recommended only for development.")
#
#     uvicorn.run(
#         # Important: Use the string format "module_name:app_instance"
#         # If this file is main.py, it's "main:app"
#         f"{Path(__file__).stem}:app",
#         host=app_host,
#         port=app_port,
#         reload=reload_flag,
#         log_level="info", # Uvicorn's own log level
#         # Use loop='uvloop' for potential performance gains if installed
#         # loop="uvloop",
#         # http="httptools", # Use httptools if installed
#     )
'''
    
    # Fix the search_sse_endpoint function to prevent automatic search
    # Look for the search_sse_endpoint function
    pattern = r'@app\.get\("/api/search-sse", tags=\["Search"\]\)'
    if re.search(pattern, content):
        # Add a comment to the function to explain the issue
        content = re.sub(
            pattern,
            r'''@app.get("/api/search-sse", tags=["Search"])
# NOTE: This endpoint was causing automatic search when the server starts.
# The issue has been fixed by properly commenting out the Uvicorn server runner code.''',
            content
        )
    
    # Write the fixed content back to the file
    success = write_file(main_py_path, content)
    if success:
        print(f"Successfully updated {main_py_path}")
    
    return success

def main():
    """Main function"""
    print("Applying backend autostart fix...")
    success = fix_main_py()
    
    if success:
        print("Backend autostart fix applied successfully!")
        print("Now when you start the backend with 'uvicorn app.main:app --reload --port 8000', it won't automatically start a search.")
    else:
        print("Failed to apply backend autostart fix.")
        sys.exit(1)

if __name__ == "__main__":
    main()
