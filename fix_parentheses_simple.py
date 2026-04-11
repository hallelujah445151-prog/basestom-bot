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
    
    # Find and count
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'sys.path.append' in line and line.rstrip().endswith('))))'):
            print(f"  Line {i} has ))))): {line[:60]}...")
    
    # Simple replace: )))) at end -> )))
    content = re.sub(
        r'abspath\(__file__\)\)\)\)',
        "abspath(__file__))))",
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Fixed and saved: {file_path}\n")
