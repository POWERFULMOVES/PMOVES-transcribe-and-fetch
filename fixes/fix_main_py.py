import os

def fix_main_py():
    """
    Fix the main.py file by directly replacing the problematic SSE endpoint
    """
    main_py_path = os.path.join('backend', 'app', 'main.py')
    
    # Create a backup of the original file
    backup_path = main_py_path + '.bak.manual_fix'
    print(f"Creating backup of {main_py_path} to {backup_path}")
    with open(main_py_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    # Define the correct implementation for the combined-updates endpoint
    correct_implementation = '''
@app.get("/combined-updates")
async def get_combined_updates(request: Request):
    """Endpoint for Server-Sent Events that combines status and transcription updates."""
    from rich.console import Console
    console = Console()
    client_host = request.client.host if request.client else "unknown"
    client_id = f"client_{time.time()}"
    origin = request.headers.get("origin", "http://localhost:3000")
    console.print(f"[bold green]SSE connection requested from {client_host} with origin {origin}[/bold green]")
    
    async def event_generator():
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
                await asyncio.sleep(0.1)
                
        except Exception as e:
            error_message = f"Error in SSE event generator: {str(e)}"
            console.print(f"[bold red]Error in event generator:[/bold red] {error_message}")
            yield f"data: {json.dumps({'type': 'error', 'content': error_message, 'timestamp': datetime.now().isoformat()})}\n\n"
    
    # Create the response with proper CORS headers
    response = EventSourceResponse(event_generator())
    
    # Set CORS headers explicitly for SSE
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS, POST"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"  # Cache preflight for 24 hours
    
    # Set other required headers for SSE
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["Connection"] = "keep-alive"
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["X-Accel-Buffering"] = "no"  # Disable proxy buffering
    
    # Log the headers for debugging
    console.print("[bold cyan]SSE Response Headers:[/bold cyan]")
    for key, value in response.headers.items():
        console.print(f"  [blue]{key}:[/blue] {value}")
    
    return response
'''
    
    # Find the problematic sections and replace them
    # First, let's remove the duplicate format_sse_message function
    duplicate_function_start = "# Standardized SSE message formatter\ndef format_sse_message"
    duplicate_function_end = "return f\"data: {json.dumps(message)}\\n\\n\""
    
    if duplicate_function_start in original_content and duplicate_function_end in original_content:
        start_idx = original_content.find(duplicate_function_start)
        end_idx = original_content.find(duplicate_function_end) + len(duplicate_function_end)
        
        # Remove the duplicate function
        content_without_duplicate = original_content[:start_idx] + original_content[end_idx:]
    else:
        content_without_duplicate = original_content
    
    # Now find and replace the combined-updates endpoint
    combined_updates_start = "@app.get(\"/combined-updates\")"
    combined_updates_end = "@app.options(\"/combined-updates\")"
    
    if combined_updates_start in content_without_duplicate and combined_updates_end in content_without_duplicate:
        start_idx = content_without_duplicate.find(combined_updates_start)
        end_idx = content_without_duplicate.find(combined_updates_end)
        
        # Replace the endpoint
        new_content = content_without_duplicate[:start_idx] + correct_implementation + "\n\n" + content_without_duplicate[end_idx:]
        
        # Write the fixed content back to the file
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Successfully fixed {main_py_path}")
        print("Please restart the backend server for the changes to take effect.")
    else:
        print(f"Could not find the combined-updates endpoint in {main_py_path}")

if __name__ == "__main__":
    fix_main_py()
