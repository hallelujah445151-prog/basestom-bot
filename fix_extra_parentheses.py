files_to_fix = [
    "C:\\Users\\crush\\AppData\\Roaming\\projects\\basestom\\src\\handlers\\registration.py",
    "C:\\Users\\crush\\AppData\\Roaming\\projects\\basestom\\src\\handlers\\change_role.py",
    "C:\\Users\\crush\\AppData\\Roaming\\projects\\basestom\\src\\utils\\reminder_background.py"
]

for file_path in files_to_fix:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(
        "sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
        "sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed: {file_path}")
