import os

def fix_sse_endpoint():
    """
    Fix the specific syntax error in the SSE endpoint implementation
    """
    main_py_path = os.path.join('backend', 'app', 'main.py')
    
    # Create a backup of the original file
    backup_path = main_py_path + '.bak.direct_fix_v2'
    print(f"Creating backup of {main_py_path} to {backup_path}")
    with open(main_py_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    # Fix the specific line with the syntax error
    problematic_line = "yield f\"data: {json.dumps({'type': 'status' 'content': 'SSE connection established' 'timestamp': datetime.now().isoformat()})}\n\n\""
    fixed_line = "yield f\"data: {json.dumps({'type': 'status', 'content': 'SSE connection established', 'timestamp': datetime.now().isoformat()})}\n\n\""
    
    # Replace all occurrences of the problematic line
    fixed_content = original_content.replace(
        "yield f\"data: {json.dumps({'type': 'status' 'content': 'SSE connection established' 'timestamp': datetime.now().isoformat()})}",
        "yield f\"data: {json.dumps({'type': 'status', 'content': 'SSE connection established', 'timestamp': datetime.now().isoformat()})}"
    )
    
    # Fix other similar issues with missing commas in dictionaries
    fixed_content = fixed_content.replace("'type': 'status' 'content':", "'type': 'status', 'content':")
    fixed_content = fixed_content.replace("'content': 'SSE connection established' 'timestamp':", "'content': 'SSE connection established', 'timestamp':")
    
    # Fix newline issues in f-strings
    fixed_content = fixed_content.replace("}\n\n\"", "}\\n\\n\"")
    
    # Write the fixed content back to the file
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Fixed syntax errors in {main_py_path}")
    print("Please restart the backend server for the changes to take effect.")

if __name__ == "__main__":
    fix_sse_endpoint()
