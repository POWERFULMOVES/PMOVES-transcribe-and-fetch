"""
Fix for CORS issues with SSE connections in the PMOVES transcription backend.

This script modifies the CORS configuration in main.py to properly handle
credentials with specific origins rather than using the wildcard "*".
"""

import re
import sys
from pathlib import Path

def fix_cors_in_main_py(file_path):
    """
    Fix CORS configuration in main.py to properly handle credentials.
    
    Args:
        file_path: Path to the main.py file
    """
    print(f"Reading file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Make a backup of the original file
        backup_path = f"{file_path}.bak.cors_fix"
        with open(backup_path, 'w', encoding='utf-8') as backup_file:
            backup_file.write(content)
        print(f"Created backup at: {backup_path}")
        
        # Count the number of changes made
        changes_made = 0
        
        # Fix 1: Replace wildcard origin in CORS middleware with specific origins
        # This is a more targeted approach that just replaces the allow_origins parameter
        allow_origins_pattern = r'allow_origins=\["?\*"?\]'
        allow_origins_replacement = 'allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]'  # Make sure comma is preserved
        
        # Count matches before replacement
        matches = re.findall(allow_origins_pattern, content)
        if matches:
            print(f"Found {len(matches)} instances of wildcard allow_origins")
            # Apply the replacement
            content = re.sub(allow_origins_pattern, allow_origins_replacement, content)
            changes_made += len(matches)
        else:
            print("No wildcard allow_origins found")
        
        # Fix 2: Replace fixed_origin with actual origin from request in SSE endpoints
        # Look for patterns where fixed_origin is used for Access-Control-Allow-Origin
        fixed_origin_pattern = r'response\.headers\["Access-Control-Allow-Origin"\] = fixed_origin'
        fixed_origin_replacement = 'response.headers["Access-Control-Allow-Origin"] = origin  # Use actual request origin'
        
        # Count matches before replacement
        matches = re.findall(fixed_origin_pattern, content)
        if matches:
            print(f"Found {len(matches)} instances of fixed_origin in CORS headers")
            
            # First, ensure the origin variable is defined before it's used
            # Find all EventSourceResponse instances
            event_source_pattern = r'response = EventSourceResponse\(event_generator\(\)\)'
            
            # For each match, add the origin definition if it doesn't exist
            for match in re.finditer(event_source_pattern, content):
                # Get the position of the match
                pos = match.end()
                
                # Find the next newline to ensure we're not inserting in the middle of a line
                next_newline = content.find('\n', pos)
                if next_newline == -1:  # No newline found
                    next_newline = pos  # Just use the current position
                
                # Check if there's already an origin definition after this
                next_lines = content[next_newline:next_newline+200]  # Look at the next 200 characters
                if 'origin = request.headers.get("origin"' not in next_lines:
                    # Insert the origin definition after the newline
                    insert_text = '\n    # Get origin from request for CORS\n    origin = request.headers.get("origin", "http://localhost:3000")'  # Make sure comma is preserved
                    content = content[:next_newline] + insert_text + content[next_newline:]
                    changes_made += 1
            
            # Now replace fixed_origin with origin
            content = re.sub(fixed_origin_pattern, fixed_origin_replacement, content)
            changes_made += len(matches)
        else:
            print("No fixed_origin usage found in CORS headers")
        
        # Fix 3: Replace any direct "*" in Access-Control-Allow-Origin headers
        wildcard_cors_pattern = r'response\.headers\["Access-Control-Allow-Origin"\] = "\*"'
        wildcard_cors_replacement = 'response.headers["Access-Control-Allow-Origin"] = origin  # Use actual request origin instead of "*"'
        
        # Count matches before replacement
        matches = re.findall(wildcard_cors_pattern, content)
        if matches:
            print(f"Found {len(matches)} instances of wildcard in CORS headers")
            content = re.sub(wildcard_cors_pattern, wildcard_cors_replacement, content)
            changes_made += len(matches)
        else:
            print("No wildcard CORS headers found")
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        if changes_made > 0:
            print(f"Successfully updated CORS configuration in {file_path} ({changes_made} changes)")
        else:
            print(f"No changes were made to {file_path}")
        
        return True
    
    except Exception as e:
        print(f"Error fixing CORS in {file_path}: {str(e)}")
        return False

def main():
    """Main function to run the script."""
    if len(sys.argv) > 1:
        main_py_path = sys.argv[1]
    else:
        # Default path
        main_py_path = Path("backend/app/main.py").absolute()
    
    if not Path(main_py_path).exists():
        print(f"Error: File not found at {main_py_path}")
        return 1
    
    success = fix_cors_in_main_py(main_py_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
