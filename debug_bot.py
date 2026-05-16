import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('src/bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print(f"Lines 71-85:")
for i in range(70, 86):
    print(f"{i+1:3}: {lines[i][:70]}")