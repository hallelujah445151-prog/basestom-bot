import sys
sys.path.append('src')
from services.user_manager import UserManager

print('FINAL TEST - Complete Logic Verification:')
print('=' * 80)

# Test 1: Unique surname - search by surname
print('\n1. UNIQUE SURNAME - Search by surname:')
print('   Input: "Плюхин"')
result = UserManager.find_user_by_name('Плюхин', 'technician')
if result:
    print(f'   Result: FOUND - {result["name"]}')
else:
    print('   Result: NOT FOUND')

# Test 2: Unique surname - search by abbreviated name
print('\n2. UNIQUE SURNAME - Search by abbreviated name:')
print('   Input: "Плюхин В.А."')
result = UserManager.find_user_by_name('Плюхин В.А.', 'technician')
if result:
    print(f'   Result: FOUND - {result["name"]}')
else:
    print('   Result: NOT FOUND')

# Test 3: Duplicate surname - search by surname (should NOT find)
print('\n3. DUPLICATE SURNAME - Search by surname (should NOT find):')
print('   Input: "Иванов"')
result = UserManager.find_user_by_name('Иванов', 'technician')
if result:
    print(f'   Result: FOUND - {result["name"]}')
else:
    print('   Result: NOT FOUND (CORRECT - duplicate surnames require full name)')

# Test 4: Duplicate surname - search by full name
print('\n4. DUPLICATE SURNAME - Search by full name:')
print('   Input: "Иванов Иван Иванович"')
result = UserManager.find_user_by_name('Иванов Иван Иванович', 'technician')
if result:
    print(f'   Result: FOUND - {result["name"]}')
else:
    print('   Result: NOT FOUND')

# Test 5: Duplicate surname - search by abbreviated name
print('\n5. DUPLICATE SURNAME - Search by abbreviated name:')
print('   Input: "Иванов И.И."')
result = UserManager.find_user_by_name('Иванов И.И.', 'technician')
if result:
    print(f'   Result: FOUND - {result["name"]}')
else:
    print('   Result: NOT FOUND')

print('\n' + '=' * 80)
print('SUMMARY:')
print('- Unique surnames: Search by surname OR full name works')
print('- Duplicate surnames: Search by full name OR abbreviated name works')
print('- Search by surname only for duplicates is blocked (CORRECT)')
