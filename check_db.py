import sqlite3

conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

# Получаем всех пользователей
cursor.execute('SELECT id, telegram_id, name, role, is_admin, is_active FROM users')
users = cursor.fetchall()

print('Все пользователи в базе данных:')
print('=' * 80)
for user in users:
    print(f'ID: {user[0]}, Telegram: {user[1]}, Name: {user[2]}, Role: {user[3]}, Admin: {user[4]}, Active: {user[5]}')

# Проверяем наличие фамилии Плюхин
print('\n' + '=' * 80)
print('Поиск фамилии Плюхин:')
for user in users:
    if 'Плюхин' in user[2] or 'плюхин' in user[2].lower():
        print(f'НАЙДЕН: {user}')

conn.close()
