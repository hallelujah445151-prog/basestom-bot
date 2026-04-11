import re

# Read file
with open('src\\handlers\\registration.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check what we're looking for
pattern = r'os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)\)\)'
matches = re.findall(pattern, content)
print(f"Found {len(matches)} matches with 3 parentheses")

# Replace
content = re.sub(
    pattern,
    "os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
    content
)

# Check again
matches_after = re.findall(r'os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)', content)
print(f"Found {len(matches_after)} matches with 2 parentheses")

# Write back
with open('src\\handlers\\registration.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
