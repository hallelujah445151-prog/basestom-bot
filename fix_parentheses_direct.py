files_to_fix = [
    "src\\handlers\\registration.py",
    "src\\handlers\\change_role.py",
    "src\\utils\\reminder_background.py"
]

for file_path in files_to_fix:
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and fix the line with sys.path.append
    for i, line in enumerate(lines):
        if 'sys.path.append' in line:
            if line.rstrip().endswith('))))'):
                print(f"  Line {i+1}: Found )))))")
                # Replace )))))) with )))))
                line = line.rstrip().rstrip(')') + ')))\n'
                lines[i] = line
                print(f"  Fixed to: {line.rstrip()}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"  Saved: {file_path}\n")
