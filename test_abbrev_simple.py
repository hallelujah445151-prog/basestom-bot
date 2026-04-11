import sys
sys.path.append('src')
from services.user_manager import UserManager

print('Testing abbreviated name search for duplicate surnames:')
print('=' * 80)

# Тестируем сокращенное имя для Иванова
test_names = [
    'Иванов И.И.',
    'Иванов И.П.',
    'Иванов И.С.'
]

for test_name in test_names:
    print(f"\nSearching for: '{test_name}'")
    result = UserManager.find_user_by_name(test_name, 'technician')
    if result:
        print(f"FOUND: {result['name']}")
    else:
        print("NOT FOUND")
