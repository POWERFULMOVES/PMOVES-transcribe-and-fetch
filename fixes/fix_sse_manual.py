import os
import re

def fix_sse_manually():
    """
    Manually fix the specific problematic line in main.py
    """
    main_py_path = os.path.join('backend', 'app', 'main.py')
    
    # Create a backup of the original file
    backup_path = main_py_path + '.bak.manual_fix'
    print(f"Creating backup of {main_py_path} to {backup_path}")
    with open(main_py_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    # Find the problematic line
    problematic_line = "yield f\"data: {json.dumps({'type': 'status' 'content': 'SSE connection established' 'timestamp': datetime.now().isoformat()})}"
    fixed_line = "yield f\"data: {json.dumps({'type': 'status', 'content': 'SSE connection established', 'timestamp': datetime.now().isoformat()})}\\n\\n\""
    
    # Replace the problematic line
    fixed_content = original_content.replace(problematic_line, fixed_line)
    
    # Write the fixed content back to the file
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Manually fixed the problematic line in {main_py_path}")
    print("Please restart the backend server for the changes to take effect.")

if __name__ == "__main__":
    fix_sse_manually()
