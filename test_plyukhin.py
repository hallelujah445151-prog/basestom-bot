import sys
sys.path.append('src')

from services.user_manager import UserManager

print('Testing search for technician "Plyukhin":')
print('=' * 80)

# Test 1: Search by surname only
result = UserManager.find_user_by_name('Плюхин', 'technician')
if result:
    print(f"Test 1 - Search by surname 'Плюхин': FOUND - {result['name']}")
else:
    print("Test 1 - Search by surname 'Плюхin': NOT FOUND")

# Test 2: Search by full name
result = UserManager.find_user_by_name('Плюхин Владимир Александрович', 'technician')
if result:
    print(f"Test 2 - Full name 'Плюхин Владимир Александрович': FOUND - {result['name']}")
else:
    print("Test 2 - Full name 'Плюхин Владимир Александрович': NOT FOUND")

# Test 3: Search by abbreviated name
result = UserManager.find_user_by_name('Плюхин В.А.', 'technician')
if result:
    print(f"Test 3 - Abbreviated 'Плюхин В.А.': FOUND - {result['name']}")
else:
    print("Test 3 - Abbreviated 'Плюхин В.А.': NOT FOUND")

print()
print('Testing search for technician "Ivanov" (has duplicates):')
print('=' * 80)

# Test 4: Search by surname with duplicates
result = UserManager.find_user_by_name('Иванов', 'technician')
if result:
    print(f"Test 4 - Search by surname 'Иванов': FOUND - {result['name']}")
else:
    print("Test 4 - Search by surname 'Иванов': NOT FOUND (expected for duplicates)")

# Test 5: Search by full name with duplicates
result = UserManager.find_user_by_name('Иванов Иван Иванович', 'technician')
if result:
    print(f"Test 5 - Full name 'Иванов Иван Иванович': FOUND - {result['name']}")
else:
    print("Test 5 - Full name 'Иванов Иван Иванович': NOT FOUND")
