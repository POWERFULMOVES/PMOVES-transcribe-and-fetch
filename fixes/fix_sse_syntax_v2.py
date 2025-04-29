import os
import sys
import re

def fix_sse_syntax():
    """
    Fix syntax errors in the SSE endpoint implementation in main.py
    """
    main_py_path = os.path.join('backend', 'app', 'main.py')
    
    # Create a backup of the original file
    backup_path = main_py_path + '.bak.syntax_fix_v2'
    if not os.path.exists(backup_path):
        print(f"Creating backup of {main_py_path} to {backup_path}")
        with open(main_py_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
    
    # Read the current content
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Replace the entire event_generator function in the combined-updates endpoint
    event_generator_pattern = r"async def event_generator\(\):.*?yield f\"data:.*?last_heartbeat = current_time.*?await asyncio\.sleep\(0\.1\)"
    
    event_generator_replacement = """async def event_generator():
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'status', 'content': 'SSE connection established', 'timestamp': datetime.now().isoformat()})}\n\n"
            
            # Initialize heartbeat time
            last_heartbeat = time.time()
            heartbeat_interval = 15  # seconds
            
            # Main event loop
            while True:
                # Check for status updates (non-blocking)
                try:
                    status_update = queue_manager.status_queue.get_nowait()
                    console.print(f"[yellow]Sending status update: {status_update[:50]}...[/yellow]")
                    
                    # Ensure the update is properly formatted JSON
                    try:
                        update_data = json.loads(status_update)
                        # Standardize field names if needed
                        if 'message' in update_data and 'content' not in update_data:
                            update_data['content'] = update_data.pop('message')
                        # Add timestamp if missing
                        if 'timestamp' not in update_data:
                            update_data['timestamp'] = datetime.now().isoformat()
                            
                        yield f"data: {json.dumps(update_data)}\n\n"
                    except json.JSONDecodeError:
                        # If not valid JSON, wrap in standard format
                        yield f"data: {json.dumps({'type': 'status', 'content': status_update, 'timestamp': datetime.now().isoformat()})}\n\n"
                except asyncio.QueueEmpty:
                    pass
                
                # Check for transcription updates (non-blocking)
                try:
                    transcription_update = queue_manager.transcription_queue.get_nowait()
                    console.print(f"[cyan]Sending transcription update: {transcription_update[:50]}...[/cyan]")
                    
                    # Ensure the update is properly formatted JSON
                    try:
                        update_data = json.loads(transcription_update)
                        # Standardize field names if needed
                        if 'message' in update_data and 'content' not in update_data:
                            update_data['content'] = update_data.pop('message')
                        # Add timestamp if missing
                        if 'timestamp' not in update_data:
                            update_data['timestamp'] = datetime.now().isoformat()
                            
                        yield f"data: {json.dumps(update_data)}\n\n"
                    except json.JSONDecodeError:
                        # If not valid JSON, wrap in standard format
                        yield f"data: {json.dumps({'type': 'transcription_segment', 'content': transcription_update, 'timestamp': datetime.now().isoformat()})}\n\n"
                except asyncio.QueueEmpty:
                    pass
                
                # Send heartbeat if no updates for a while
                current_time = time.time()
                if current_time - last_heartbeat > heartbeat_interval:
                    console.print(f"[dim]Sending heartbeat[/dim]")
                    yield f"data: {json.dumps({'type': 'heartbeat', 'content': 'ping', 'timestamp': datetime.now().isoformat()})}\n\n"
                    last_heartbeat = current_time
                
                # Short delay to prevent CPU spinning
                await asyncio.sleep(0.1)"""
    
    # Fix 2: Replace the error handling part in the event_generator function
    error_handling_pattern = r"except Exception as e:.*?yield f\"data:.*?error_message, 'timestamp': datetime\.now\(\)\.isoformat\(\)\}\)\\"
    
    error_handling_replacement = """except Exception as e:
            error_message = f"Error in SSE event generator: {str(e)}"
            console.print(f"[bold red]Error in event generator:[/bold red] {error_message}")
            yield f"data: {json.dumps({'type': 'error', 'content': error_message, 'timestamp': datetime.now().isoformat()})}\n\n\""""
    
    # Fix 3: Fix the download status SSE endpoint as well
    download_status_pattern = r"yield f\"data: \{json\.dumps\(update_data\)\}\\n\\n\""
    download_status_replacement = r'yield f"data: {json.dumps(update_data)}\n\n"'
    
    # Apply the fixes
    content = re.sub(event_generator_pattern, event_generator_replacement, content, flags=re.DOTALL)
    content = re.sub(error_handling_pattern, error_handling_replacement, content, flags=re.DOTALL)
    content = content.replace("\\n\\n\"", "\n\n\"")
    
    # Fix any remaining issues with newlines in f-strings
    content = re.sub(r'yield f"data: \{json\.dumps\((.*?)\)\}\\n\\n"', r'yield f"data: {json.dumps(\1)}\n\n"', content, flags=re.DOTALL)
    
    # Fix missing commas in dictionaries
    content = content.replace("'type': 'status' 'content':", "'type': 'status', 'content':")
    content = content.replace("'content': 'SSE connection established' 'timestamp':", "'content': 'SSE connection established', 'timestamp':")
    
    # Write the updated content back to the file
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Syntax fixes applied to {main_py_path}")
    print("Please restart the backend server for the changes to take effect.")

if __name__ == "__main__":
    fix_sse_syntax()
