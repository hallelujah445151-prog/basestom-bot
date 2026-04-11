import sys
sys.path.append('src')

from database import get_connection
from services.user_manager import UserManager

# Проверяем поиск пользователя
print('Тестируем поиск техника по фамилии "Плюхин":')
print('=' * 80)

# Получаем всех техников
technicians = UserManager.get_users_by_role('technician')
print(f'Всего техников в базе: {len(technicians)}')
print()

print('Список техников:')
for tech in technicians:
    print(f"  - {tech['name']}")
print()

# Пробуем найти по фамилии
print('Поиск по фамилии "Плюхин":')
result = UserManager.find_user_by_name('Плюхин', 'technician')
if result:
    print(f"  ✅ НАЙДЕН: {result['name']}")
else:
    print(f"  ❌ НЕ НАЙДЕН")
print()

# Пробуем найти по полному имени
print('Поиск по полному имени "Плюхин Владимир Александрович":')
result = UserManager.find_user_by_name('Плюхин Владимир Александрович', 'technician')
if result:
    print(f"  ✅ НАЙДЕН: {result['name']}")
else:
    print(f"  ❌ НЕ НАЙДЕН")
print()

# Проверяем дубликаты фамилий
print('Проверка дубликатов фамилий:')
from collections import Counter
surnames = []
for tech in technicians:
    surname = tech['name'].split()[0] if tech['name'].split() else tech['name']
    surnames.append(surname.lower())

surname_counts = Counter(surnames)
print(f'Фамилии и количество: {dict(surname_counts)}')

duplicate_surnames = {surname for surname, count in surname_counts.items() if count > 1}
has_duplicates = len(duplicate_surnames) > 0
print(f'Дубликаты фамилий: {duplicate_surnames if has_duplicates else "Нет"}')
print(f'Есть дубликаты: {has_duplicates}')
