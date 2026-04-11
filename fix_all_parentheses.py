import re

files_to_fix = [
    "src\\handlers\\registration.py",
    "src\\handlers\\change_role.py",
    "src\\utils\\reminder_background.py"
]

for file_path in files_to_fix:
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find lines with the problem
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'sys.path.append' in line:
            print(f"  Line {i}: {line}")
            # Count closing parentheses at the end
            match = re.search(r'\)+$', line)
            if match:
                parens = match.group()
                print(f"  Found {len(parens)} closing parentheses")
                
    # Replace 4 ) with 3 )
    content = re.sub(
        r'os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)\)\)\)',
        "os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
        content
    )
    
    # Also replace just )))) at end of line if pattern is different
    content = re.sub(
        r'abspath\(__file__\)\)\)\)\)',
        "abspath(__file__))))",
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Saved: {file_path}\n")
