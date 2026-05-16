import re

text = "циркон 3 шт на 13.04.2026 врач Гаспарянидзе пациент Писькова"

print("Testing regex for quantity extraction")
print(f"Text: '{text}'")
print("-" * 80)

# Текущий regex
quantity_match = re.search(r'(\d+)\s*шт', text)
print(f"Current regex: r'(\\d+)\\s*шт'")
print(f"Match: {quantity_match}")
if quantity_match:
    print(f"Extracted: {quantity_match.group(1)}")
else:
    print("NO MATCH!")

# Попробуем другие варианты
print("\nTrying alternative regex patterns:")

pattern1 = r'(\d+)\s*шт'
match1 = re.search(pattern1, text)
print(f"Pattern 1: {pattern1} -> {match1.group(1) if match1 else 'None'}")

pattern2 = r'(\d+)\s*шт'
match2 = re.search(pattern2, text.lower())
print(f"Pattern 2 (lowercase): {pattern2} -> {match2.group(1) if match2 else 'None'}")

pattern3 = r'(\d+)\s*шт'
match3 = re.search(pattern3, text, re.IGNORECASE)
print(f"Pattern 3 (ignorecase): {pattern3} -> {match3.group(1) if match3 else 'None'}")
