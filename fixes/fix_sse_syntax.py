import os
import sys
import re

def fix_sse_syntax():
    """
    Fix syntax errors in the SSE endpoint implementation in main.py
    """
    main_py_path = os.path.join('backend', 'app', 'main.py')
    
    # Create a backup of the original file
    backup_path = main_py_path + '.bak.syntax_fix'
    if not os.path.exists(backup_path):
        print(f"Creating backup of {main_py_path} to {backup_path}")
        with open(main_py_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
    
    # Read the current content
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Add missing commas in the JSON dictionary
    content = content.replace(
        "{'type': 'status' 'content': 'SSE connection established' 'timestamp': datetime.now().isoformat()}",
        "{'type': 'status', 'content': 'SSE connection established', 'timestamp': datetime.now().isoformat()}"
    )
    
    # Fix 2: Check for any other missing closing quotes or parentheses
    if "yield f\"data: {json.dumps(" in content and not "yield f\"data: {json.dumps(})\\n\\n\"" in content:
        content = re.sub(
            r'yield f"data: {json.dumps\((.*?)\)}',
            r'yield f"data: {json.dumps(\1)}\n\n"',
            content,
            flags=re.DOTALL
        )
    
    # Write the updated content back to the file
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Syntax fixes applied to {main_py_path}")
    print("Please restart the backend server for the changes to take effect.")

if __name__ == "__main__":
    fix_sse_syntax()
