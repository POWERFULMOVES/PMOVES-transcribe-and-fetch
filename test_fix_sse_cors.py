"""
Test script for CORS fix in main.py.

This script tests the regex patterns and replacements without modifying the actual file.
"""

import re
import sys
from pathlib import Path
import difflib

def test_cors_fix(file_path):
    """
    Test the CORS fix on main.py without modifying the file.
    
    Args:
        file_path: Path to the main.py file
    """
    print(f"Reading file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Store original content for comparison
        original_content = content
        modified_content = content
        
        # Count the number of changes that would be made
        changes_made = 0
        
        # Fix 1: Test replacing wildcard origin in CORS middleware with specific origins
        allow_origins_pattern = r'allow_origins=\["?\*"?\]'
        allow_origins_replacement = 'allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]'  # Make sure comma is preserved
        
        # Count matches before replacement
        matches = re.findall(allow_origins_pattern, content)
        if matches:
            print(f"\n✅ Found {len(matches)} instances of wildcard allow_origins")
            # Apply the replacement for testing
            modified_content = re.sub(allow_origins_pattern, allow_origins_replacement, modified_content)
            changes_made += len(matches)
        else:
            print("\n⚠️ No wildcard allow_origins found")
        
        # Fix 2: Test replacing fixed_origin with actual origin from request in SSE endpoints
        fixed_origin_pattern = r'response\.headers\["Access-Control-Allow-Origin"\] = fixed_origin'
        fixed_origin_replacement = 'response.headers["Access-Control-Allow-Origin"] = origin  # Use actual request origin'
        
        # Count matches before replacement
        matches = re.findall(fixed_origin_pattern, content)
        if matches:
            print(f"\n✅ Found {len(matches)} instances of fixed_origin in CORS headers")
            
            # First, test adding origin definition before it's used
            event_source_pattern = r'response = EventSourceResponse\(event_generator\(\)\)'
            event_source_matches = list(re.finditer(event_source_pattern, modified_content))
            
            if event_source_matches:
                print(f"\n✅ Found {len(event_source_matches)} EventSourceResponse instances")
                
                # For each match, check if we need to add origin definition
                for match in event_source_matches:
                    pos = match.end()
                    
                    # Find the next newline to ensure we're not inserting in the middle of a line
                    next_newline = modified_content.find('\n', pos)
                    if next_newline == -1:  # No newline found
                        next_newline = pos  # Just use the current position
                    
                    next_lines = modified_content[next_newline:next_newline+200]  # Look at the next 200 characters
                    
                    if 'origin = request.headers.get("origin"' not in next_lines:
                        print(f"\n✅ Adding origin definition after EventSourceResponse at position {next_newline}")
                        insert_text = '\n    # Get origin from request for CORS\n    origin = request.headers.get("origin", "http://localhost:3000")'  # Make sure comma is preserved
                        modified_content = modified_content[:next_newline] + insert_text + modified_content[next_newline:]
                        changes_made += 1
            
            # Now replace fixed_origin with origin
            modified_content = re.sub(fixed_origin_pattern, fixed_origin_replacement, modified_content)
            changes_made += len(matches)
        else:
            print("\n⚠️ No fixed_origin usage found in CORS headers")
        
        # Fix 3: Test replacing any direct "*" in Access-Control-Allow-Origin headers
        wildcard_cors_pattern = r'response\.headers\["Access-Control-Allow-Origin"\] = "\*"'
        wildcard_cors_replacement = 'response.headers["Access-Control-Allow-Origin"] = origin  # Use actual request origin instead of "*"'
        
        # Count matches before replacement
        matches = re.findall(wildcard_cors_pattern, content)
        if matches:
            print(f"\n✅ Found {len(matches)} instances of wildcard in CORS headers")
            modified_content = re.sub(wildcard_cors_pattern, wildcard_cors_replacement, modified_content)
            changes_made += len(matches)
        else:
            print("\n⚠️ No wildcard CORS headers found")
        
        # Show diff of changes
        if modified_content != original_content:
            print(f"\n📝 Changes that would be made ({changes_made} total):")
            diff = difflib.unified_diff(
                original_content.splitlines(),
                modified_content.splitlines(),
                fromfile='original',
                tofile='fixed',
                lineterm=''
            )
            for line in diff:
                if line.startswith('+'):
                    print(f"\033[92m{line}\033[0m")  # Green for additions
                elif line.startswith('-'):
                    print(f"\033[91m{line}\033[0m")  # Red for deletions
                else:
                    print(line)
        else:
            print("\n⚠️ No changes would be made to the file.")
        
        return True
    
    except Exception as e:
        print(f"Error testing CORS fix in {file_path}: {str(e)}")
        return False

def main():
    """Main function to run the test script."""
    if len(sys.argv) > 1:
        main_py_path = sys.argv[1]
    else:
        # Default path
        main_py_path = Path("backend/app/main.py").absolute()
    
    if not Path(main_py_path).exists():
        print(f"Error: File not found at {main_py_path}")
        return 1
    
    success = test_cors_fix(main_py_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
