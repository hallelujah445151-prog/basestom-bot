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
            # Count parentheses
            open_parens = line.count('(')
            close_parens = line.count(')')
            print(f"  Line {i+1}: open={open_parens}, close={close_parens}")
            print(f"  Current: {line.rstrip()}")
            
            # Should have balanced parentheses
            if close_parens < open_parens:
                needed = open_parens - close_parens
                line = line.rstrip() + ')' * needed + '\n'
                lines[i] = line
                print(f"  Fixed to: {line.rstrip()}")
            elif close_parens > open_parens:
                # Remove extra closing parentheses
                extra = close_parens - open_parens
                line = line.rstrip().rstrip(')' * extra) + '\n'
                lines[i] = line
                print(f"  Fixed to: {line.rstrip()}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"  Saved: {file_path}\n")
