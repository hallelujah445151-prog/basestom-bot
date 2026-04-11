import sqlite3

conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

# Получаем всех техников
cursor.execute("SELECT id, name FROM users WHERE role = 'technician'")
technicians = cursor.fetchall()

print('All technicians in database:')
print('=' * 80)
for tech in technicians:
    print(f"ID: {tech[0]}, Name: {tech[1]}")

# Теперь протестируем с реальным именем из базы
if len(technicians) > 0:
    # Предполагаем, что техника с ID=5 это Плюхин
    test_name = technicians[2][1]  # Индекс может быть разным
    print(f"\nTesting with real name from database: '{test_name}'")
    
    conn.close()
    
    # Теперь тестируем UserManager с реальным именем
    import sys
    sys.path.append('src')
    from services.user_manager import UserManager
    
    result = UserManager.find_user_by_name(test_name, 'technician')
    if result:
        print(f"✅ FOUND: {result['name']}")
    else:
        print(f"❌ NOT FOUND")
