import os
import sys
import re

def fix_sse_cors():
    """
    Fix CORS issues with SSE endpoints in main.py
    """
    main_py_path = os.path.join('backend', 'app', 'main.py')
    
    # Create a backup of the original file
    backup_path = main_py_path + '.bak.cors_fix'
    if not os.path.exists(backup_path):
        print(f"Creating backup of {main_py_path} to {backup_path}")
        with open(main_py_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
    
    # Read the current content
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Update the CORS middleware configuration to ensure it's applied to all routes
    cors_middleware_pattern = r"app\.add_middleware\(\s*CORSMiddleware,\s*allow_origins=\[.*?\],.*?\)"
    cors_middleware_replacement = """app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Allow specific origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["Content-Type", "X-Content-Type-Options"],
)"""
    
    # Fix 2: Modify the combined-updates endpoint to ensure CORS headers are properly set
    combined_updates_pattern = r"@app\.get\(\"/combined-updates\"\)\nasync def get_combined_updates\(request: Request\):.*?return response"
    
    # Use a function to replace the combined-updates endpoint with the fixed version
    def replace_combined_updates(match):
        # Extract the original function body
        original = match.group(0)
        
        # Replace the response creation and headers setting
        modified = re.sub(
            r"response = EventSourceResponse\(event_generator\(\)\).*?return response",
            """response = EventSourceResponse(event_generator())
    
    # Get origin from request for CORS - use the actual origin
    origin = request.headers.get("origin", "http://localhost:3000")
    
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
    
    return response""",
            original,
            flags=re.DOTALL
        )
        
        return modified
    
    # Apply the fixes
    content = re.sub(cors_middleware_pattern, cors_middleware_replacement, content, flags=re.DOTALL)
    content = re.sub(combined_updates_pattern, replace_combined_updates, content, flags=re.DOTALL)
    
    # Fix 3: Ensure the OPTIONS handler for combined-updates is also setting CORS headers correctly
    options_pattern = r"@app\.options\(\"/combined-updates\"\)\nasync def options_combined_updates\(request: Request\):.*?return response"
    
    def replace_options_handler(match):
        original = match.group(0)
        
        modified = re.sub(
            r"response\.headers\[\"Access-Control-Allow-Origin\"\] = origin.*?return response",
            """response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS, POST"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"  # Cache preflight for 24 hours
    
    # Log the headers for debugging
    console.print("[bold cyan]OPTIONS Response Headers:[/bold cyan]")
    for key, value in response.headers.items():
        console.print(f"  [blue]{key}:[/blue] {value}")
    
    return response""",
            original,
            flags=re.DOTALL
        )
        
        return modified
    
    content = re.sub(options_pattern, replace_options_handler, content, flags=re.DOTALL)
    
    # Write the updated content back to the file
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"CORS fixes applied to {main_py_path}")
    print("Please restart the backend server for the changes to take effect.")

if __name__ == "__main__":
    fix_sse_cors()
