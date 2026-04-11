import re

# Read file
with open('src\\handlers\\registration.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Get line 5
lines = content.split('\n')
line5 = lines[4]
print(f"Line 5: {line5}")
print(f"Length: {len(line5)}")

# Check for different patterns
patterns = [
    ('3 ) at end', r'\)\)\)$'),
    ('4 ) at end', r'\)\)\)\)$'),
    ('dirname...dirname...abspath(__file__)))', r'os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)\)$'),
]

for desc, pattern in patterns:
    matches = re.findall(pattern, content)
    print(f"{desc}: {len(matches)} matches")
