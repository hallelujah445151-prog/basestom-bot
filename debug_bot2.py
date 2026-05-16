import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('src/bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Try-except structure (lines 33-85):")
for i in range(32, 85):
    line = lines[i]
    indent = len(line) - len(line.lstrip())
    print(f"{i+1:3} ({indent:2}sp): {line.rstrip()[:70]}")