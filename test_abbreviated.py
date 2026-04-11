import sqlite3

conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

# Получаем всех техников Иванов
cursor.execute("SELECT id, name FROM users WHERE role = 'technician' AND (name LIKE 'Иванов%' OR name LIKE 'иванов%')")
ivanovs = cursor.fetchall()

print('All technicians with surname "Ivanov":')
print('=' * 80)
for ivanov in ivanovs:
    print(f"ID: {ivanov[0]}, Name: {ivanov[1]}")

conn.close()

# Теперь протестируем поиск по сокращенному имени
import sys
sys.path.append('src')
from services.user_manager import UserManager

if len(ivanovs) > 0:
    # Тестируем с полным именем первого Иванова
    test_name = ivanovs[0][1]
    print(f"\nTesting search by full name: '{test_name}'")
    result = UserManager.find_user_by_name(test_name, 'technician')
    if result:
        print(f"✅ FOUND: {result['name']}")
    else:
        print(f"❌ NOT FOUND")
    
    # Тестируем с сокращенным именем
    # Формируем инициалы из полного имени
    parts = test_name.split()
    if len(parts) >= 2:
        initials = f"{parts[0]} {parts[1][0]}."
        if len(parts) >= 3:
            initials += f"{parts[2][0]}."
        
        print(f"\nTesting search by abbreviated name: '{initials}'")
        result = UserManager.find_user_by_name(initials, 'technician')
        if result:
            print(f"✅ FOUND: {result['name']}")
        else:
            print(f"❌ NOT FOUND")
