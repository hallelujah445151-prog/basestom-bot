import re
import os

file_path = r'C:\Users\crush\AppData\Roaming\projects\basestom\src\services\message_processor.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем все f-строки на сырые
content = content.replace(r'f\"', 'r\"', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all f-strings to raw strings")
print(f"File updated: {file_path}")
