# -*- coding: utf-8 -*-
import sys
import os
import difflib

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.user_manager import UserManager
from database import get_connection

def test_doctor_name_conflict():
    """Тестирование проблемы с одинаковыми фамилиями врачей"""

    print("=" * 70)
    print(" TESTING DOCTOR NAME CONFLICT")
    print("=" * 70)
    print()

    conn = get_connection()
    cursor = conn.cursor()

    # Создание тестовых врачей с одинаковыми фамилиями
    print("Creating test doctors with same surname...")

    cursor.execute('DELETE FROM users WHERE name LIKE "%Иванов%"')

    doctors = [
        ("Иванов Иван Петрович", 11111),
        ("Иванов Петр Сидорович", 22222),
        ("Иванов Сергей Андреевич", 33333),
    ]

    for name, telegram_id in doctors:
        try:
            cursor.execute('''
                INSERT INTO users (telegram_id, name, role, is_active)
                VALUES (?, ?, 'doctor', 1)
            ''', (telegram_id, name))
            print(f"  Created: {name} (ID: {telegram_id})")
        except Exception as e:
            print(f"  Error creating {name}: {e}")

    conn.commit()

    print()
    print("TESTING CURRENT LOGIC:")
    print("-" * 70)

    # Тест 1: Поиск по фамилии
    print("\nTest 1: Searching by surname 'Иванов'")
    result = UserManager.find_user_by_name("Иванов", "doctor")
    if result:
        print(f"  Result: {result['name']} (ID: {result['telegram_id']})")
        print(f"  Status: FIRST MATCH (current behavior)")
    else:
        print(f"  Status: NOT FOUND")

    # Тест 2: Поиск по полному имени
    print("\nTest 2: Searching by full name 'Иванов Иван Петрович'")
    result = UserManager.find_user_by_name("Иванов Иван Петрович", "doctor")
    if result:
        print(f"  Result: {result['name']} (ID: {result['telegram_id']})")
        print(f"  Status: EXACT MATCH (works)")
    else:
        print(f"  Status: NOT FOUND")

    # Тест 3: Поиск по короткому имени
    print("\nTest 3: Searching by short name 'Иванов'")
    result = UserManager.find_user_by_name("Иванов", "doctor")
    if result:
        print(f"  Result: {result['name']} (ID: {result['telegram_id']})")
        print(f"  Status: FIRST MATCH (problem!)")
    else:
        print(f"  Status: NOT FOUND")

    # Проверка всех врачей в базе
    print("\nAll doctors in database:")
    cursor.execute('SELECT id, telegram_id, name FROM users WHERE role = "doctor"')
    rows = cursor.fetchall()

    for row in rows:
        user_id, telegram_id, name = row
        print(f"  ID: {user_id}, Telegram ID: {telegram_id}, Name: {name}")

    print()
    print("=" * 70)
    print(" PROBLEM ANALYSIS")
    print("=" * 70)
    print()
    print("CURRENT ISSUE:")
    print("  - When searching 'Иванов', finds FIRST match")
    print("  - Other 'Ivanov' doctors are NEVER checked")
    print("  - Result: Always the first doctor gets assigned")
    print()
    print("RECOMMENDED FIX:")
    print("  1. Use exact match first (name.lower() == user_name.lower())")
    print("  2. If multiple exact matches, ask for clarification")
    print("  3. If no exact match, use fuzzy matching with higher cutoff (0.85)")
    print("  4. Provide user instruction to use full names")

    conn.close()


if __name__ == "__main__":
    test_doctor_name_conflict()
    input("\nPress Enter to exit...")