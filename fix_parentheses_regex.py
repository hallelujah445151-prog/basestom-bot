import re

files_to_fix = [
    "src\\handlers\\registration.py",
    "src\\handlers\\change_role.py",
    "src\\utils\\reminder_background.py"
]

for file_path in files_to_fix:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace three closing parentheses with two
    content = re.sub(
        r'os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)\)\)',
        "os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed: {file_path}")
