#!/usr/bin/env python3
"""
Fix for backend SSE implementation issues
This script updates the main.py file to ensure proper SSE event handling
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
    backup_path = main_py_path.with_suffix('.py.bak.sse_fix')
    write_file(backup_path, content)
    print(f"Created backup at {backup_path}")
    
    # Fix 1: Improve the format_sse_message function
    pattern = r'def format_sse_message\(message_type: str, content: Any, metadata: Optional\[dict\] = None\) -> str:'
    if re.search(pattern, content):
        content = re.sub(
            r'def format_sse_message\(message_type: str, content: Any, metadata: Optional\[dict\] = None\) -> str:[\s\S]*?return f"data: {json_str}\\n\\n"[\s\S]*?except TypeError as e:[\s\S]*?return f"data: {json\.dumps\({[^}]*}\)}\\n\\n"',
            """def format_sse_message(message_type: str, content: Any, metadata: Optional[dict] = None) -> str:
    \"\"\"Formats a message dictionary into an SSE string.\"\"\"
    message = {
        "type": message_type,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    if metadata:
        message["metadata"] = metadata
    try:
        # Ensure content is serializable
        if isinstance(content, dict) or isinstance(content, list):
            # Already a dict or list, no need to convert
            pass
        elif hasattr(content, 'to_dict') and callable(content.to_dict):
            # Convert objects with to_dict method
            message["content"] = content.to_dict()
        elif hasattr(content, '__dict__'):
            # Convert objects with __dict__ attribute
            message["content"] = content.__dict__
            
        # Ensure we handle any non-serializable objects
        json_str = json.dumps(message, default=lambda o: str(o))
        return f"data: {json_str}\\n\\n"
    except TypeError as e:
         logger.error(f"Failed to serialize SSE message content of type {message_type}: {e}. Content snippet: {str(content)[:100]}")
         # Fallback: send error message or simplified content
         error_content = {"error": "Failed to serialize message content", "original_type": message_type}
         return f"data: {json.dumps({'type': 'error', 'content': error_content, 'timestamp': datetime.now().isoformat()})}\\n\\n\"""",
            content
        )
    
    # Fix 2: Improve the search_sse_endpoint function
    pattern = r'@app\.get\("/api/search-sse", tags=\["Search"\])'
    if re.search(pattern, content):
        content = re.sub(
            r'@app\.get\("/api/search-sse", tags=\["Search"\])([\s\S]*?)async def search_sse_endpoint\(([\s\S]*?)async def event_generator\(\):([\s\S]*?)yield format_sse_message\("status", "Starting search operation"([\s\S]*?)# Send initial status([\s\S]*?)yield format_sse_message\("status", "Configuring search parameters"',
            """@app.get("/api/search-sse", tags=["Search"])
# NOTE: This endpoint was causing automatic search when the server starts.
# The issue has been fixed by properly commenting out the Uvicorn server runner code.
\\1async def search_sse_endpoint(\\2async def event_generator():
            try:\\3yield format_sse_message("status", "Starting search operation", {"stage": "start"})\\4# Send initial status\\5yield format_sse_message("status", "Configuring search parameters", {"stage": "search"})""",
            content
        )
        
        # Fix the stage updates in the event generator
        content = re.sub(
            r'yield format_sse_message\("status", "Executing search query"([\s\S]*?)# Update status to filtering',
            """yield format_sse_message("status", "Executing search query", {"stage": "filter"})\\1# Update status to filtering""",
            content
        )
        
        content = re.sub(
            r'yield format_sse_message\("status", "Combining search results"([\s\S]*?)# Update status to combining results',
            """yield format_sse_message("status", "Combining search results", {"stage": "combine"})\\1# Update status to combining results""",
            content
        )
        
        content = re.sub(
            r'yield format_sse_message\("status", "Analyzing search results"([\s\S]*?)# Send OpenAI analysis if available',
            """yield format_sse_message("status", "Analyzing search results", {"stage": "analyze"})\\1# Send OpenAI analysis if available""",
            content
        )
        
        # Fix the analysis event messages
        content = re.sub(
            r'yield format_sse_message\("analysis", openai_analysis([\s\S]*?)# Send Groq analysis if available',
            """yield format_sse_message("analysis", openai_analysis, {"provider": "openai"})\\1# Send Groq analysis if available""",
            content
        )
        
        content = re.sub(
            r'yield format_sse_message\("analysis", groq_analysis([\s\S]*?)# Send final results',
            """yield format_sse_message("analysis", groq_analysis, {"provider": "groq"})\\1# Send final results""",
            content
        )
        
        # Fix the final results and completion messages
        content = re.sub(
            r'yield format_sse_message\("results", formatted_results, metadata\)([\s\S]*?)# Send completion message',
            """yield format_sse_message("results", formatted_results, {**metadata, "stage": "complete"})\\1# Send completion message""",
            content
        )
        
        content = re.sub(
            r'yield format_sse_message\("complete", "Search process completed"([\s\S]*?)except asyncio\.CancelledError:',
            """yield format_sse_message("complete", "Search process completed", {"stage": "complete"})\\1except asyncio.CancelledError:""",
            content
        )
        
        # Add heartbeat to keep connection alive
        content = re.sub(
            r'await asyncio\.sleep\(0\.1\) # Prevent high CPU usage if queues empty([\s\S]*?)except asyncio\.CancelledError:',
            """await asyncio.sleep(0.1) # Prevent high CPU usage if queues empty\\1                # Send heartbeat every 15 seconds
                now = time.time()
                if now - last_activity_time > 15:
                    yield format_sse_message("heartbeat", "ping")
                    last_activity_time = now\\1except asyncio.CancelledError:""",
            content
        )
    
    # Write the fixed content back to the file
    success = write_file(main_py_path, content)
    if success:
        print(f"Successfully updated {main_py_path}")
    
    return success

def main():
    """Main function"""
    print("Applying backend SSE fixes...")
    success = fix_main_py()
    
    if success:
        print("Backend SSE fixes applied successfully!")
        print("The backend now properly sends stage updates and metadata with SSE events.")
    else:
        print("Failed to apply backend SSE fixes.")
        sys.exit(1)

if __name__ == "__main__":
    main()
