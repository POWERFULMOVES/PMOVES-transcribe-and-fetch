import os
import sys
import re

def fix_sse_implementation(file_path):
    """
    Fix the SSE implementation in the main.py file.
    
    The issue is that the code is using StreamingResponse instead of EventSourceResponse
    for the SSE endpoint, which causes an error because StreamingResponse doesn't have
    a send attribute.
    """
    print(f"Fixing SSE implementation in {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the import statement
    content = re.sub(
        r'try:\s+from sse_starlette\.sse import EventSourceResponse\s+except ImportError:\s+from starlette\.responses import StreamingResponse as EventSourceResponse',
        'from sse_starlette.sse import EventSourceResponse',
        content
    )
    
    # Fix the combined-updates endpoint
    content = re.sub(
        r'# Create the response with proper CORS headers\s+response = StreamingResponse\(\s+event_generator\(\),\s+media_type="text/event-stream"\s+\)',
        '# Create the response with proper CORS headers\n    response = EventSourceResponse(event_generator())',
        content
    )
    
    # Fix the download-status endpoint
    content = re.sub(
        r'try:\s+# Try to use EventSourceResponse if available\s+response = EventSourceResponse\(event_generator\(\)\)\s+except Exception as e:.*?# Fall back to StreamingResponse if EventSourceResponse fails\s+response = StreamingResponse\(\s+event_generator\(\),\s+media_type="text/event-stream"\s+\)',
        '# Use EventSourceResponse for SSE\n    response = EventSourceResponse(event_generator())',
        content,
        flags=re.DOTALL
    )
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed SSE implementation in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = os.path.join('backend', 'app', 'main.py')
    
    fix_sse_implementation(file_path)
