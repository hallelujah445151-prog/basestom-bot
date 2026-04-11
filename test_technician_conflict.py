# -*- coding: utf-8 -*-
import sys
import os
import difflib

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.user_manager import UserManager
from database import get_connection

def create_test_technicians():
    """Создание тестовых техников с одинаковыми фамилиями"""

    print("=" * 70)
    print(" CREATING TEST TECHNICIANS")
    print("=" * 70)
    print()

    conn = get_connection()
    cursor = conn.cursor()

    # Удаление старых тестовых техников
    print("Deleting old test technicians...")
    cursor.execute('DELETE FROM users WHERE name LIKE "%Иванов%" AND role = "technician"')
    conn.commit()
    print("Old test technicians deleted")
    print()

    # Создание тестовых техников
    print("Creating test technicians...")

    technicians = [
        ("Иванов Иван Петрович", 44444),
        ("Иванов Петр Сидорович", 55555),
        ("Иванов Сергей Андреевич", 66666),
    ]

    for name, telegram_id in technicians:
        try:
            cursor.execute('''
                INSERT INTO users (telegram_id, name, role, is_active)
                VALUES (?, ?, 'technician', 1)
            ''', (telegram_id, name))
            print(f"  Created: {name} (ID: {telegram_id})")
        except Exception as e:
            print(f"  Error creating {name}: {e}")

    conn.commit()

    print()
    print("TEST TECHNICIANS READY!")
    print()


def test_technician_search():
    """Тестирование поиска техников"""

    print("=" * 70)
    print(" TESTING TECHNICIAN SEARCH")
    print("=" * 70)
    print()

    user_manager = UserManager()

    # Тест 1: Поиск по фамилии
    print("Test 1: Searching by surname 'Иванов'")
    result = user_manager.find_user_by_name("Иванов", "technician")
    if result:
        print(f"  Result: {result['name']} (ID: {result['telegram_id']})")
        print(f"  Status: EXACT MATCH (works)")
    else:
        print(f"  Status: NOT FOUND")

    # Тест 2: Поиск по полному имени
    print()
    print("Test 2: Searching by full name 'Иванов Иван Петрович'")
    result = user_manager.find_user_by_name("Иванов Иван Петрович", "technician")
    if result:
        print(f"  Result: {result['name']} (ID: {result['telegram_id']})")
        print(f"  Status: EXACT MATCH (works)")
    else:
        print(f"  Status: NOT FOUND")

    # Тест 3: Поиск по короткому имени
    print()
    print("Test 3: Searching by short name 'Иванов'")
    result = user_manager.find_user_by_name("Иванов", "technician")
    if result:
        print(f"  Result: {result['name']} (ID: {result['telegram_id']})")
        print(f"  Status: EXACT MATCH (problem!)")
    else:
        print(f"  Status: NOT FOUND")

    # Проверка всех техников в базе
    print()
    print("All technicians in database:")
    db_conn = get_connection()
    db_cursor = db_conn.cursor()
    db_cursor.execute('SELECT id, telegram_id, name FROM users WHERE role = "technician"')
    rows = db_cursor.fetchall()

    for row in rows:
        user_id, telegram_id, name = row
        print(f"  ID: {user_id}, Telegram ID: {telegram_id}, Name: {name}")

    db_conn.close()

    print()
    print("=" * 70)
    print(" SEARCH TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    create_test_technicians()
    test_technician_search()
    input("\nPress Enter to exit...")