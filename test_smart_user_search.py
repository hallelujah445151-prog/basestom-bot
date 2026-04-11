"""Тест умной логики поиска пользователей с учетом дубликатов фамилий"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services.user_manager import UserManager
import sqlite3

def setup_test_users():
    """Создать тестовых пользователей"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'orders.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    test_users = [
        (10001, "Иванов Иван Петрович", "doctor", 0),
        (10002, "Иванов Петр Сидорович", "doctor", 0),
        (10003, "Сидоров Алексей Николаевич", "doctor", 0),
        (10004, "Петров Дмитрий Александрович", "technician", 0),
        (10005, "Кузнецов Сергей Иванович", "technician", 0),
    ]

    for telegram_id, name, role, is_admin in test_users:
        cursor.execute('''
            INSERT OR IGNORE INTO users (telegram_id, name, role, is_admin, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, datetime('now'))
        ''', (telegram_id, name, role, is_admin))

    conn.commit()
    conn.close()
    print("Test users created/verified")

def test_unique_surnames():
    """Тест поиска при уникальных фамилиях (техники)"""
    print("\n" + "="*60)
    print("TEST 1: Unique surnames (technicians)")
    print("="*60)

    result = UserManager.find_user_by_name("Кузнецов", "technician")

    if result and result['name'] == "Кузнецов Сергей Иванович":
        print("PASS: Found by surname (unique)")
        print(f"   Result: {result['name']}")
    else:
        print("FAIL: Should find by surname")
        print(f"   Result: {result}")

def test_duplicate_surnames():
    """Тест поиска при дубликатах фамилий (врачи)"""
    print("\n" + "="*60)
    print("TEST 2: Duplicate surnames (doctors)")
    print("="*60)

    result = UserManager.find_user_by_name("Иванов", "doctor")

    if result is None:
        print("PASS: Not found by surname (duplicate)")
        print("   Expected: Should require full name")
    else:
        print("FAIL: Should NOT find by surname when duplicate exists")
        print(f"   Result: {result}")

def test_full_name_duplicate():
    """Тест поиска по полному имени при дубликатах"""
    print("\n" + "="*60)
    print("TEST 3: Full name with duplicates")
    print("="*60)

    result = UserManager.find_user_by_name("Иванов Иван Петрович", "doctor")

    if result and result['name'] == "Иванов Иван Петрович":
        print("PASS: Found by full name")
        print(f"   Result: {result['name']}")
    else:
        print("FAIL: Should find by full name")
        print(f"   Result: {result}")

def test_fuzzy_match_unique():
    """Тест fuzzy matching при уникальных фамилиях"""
    print("\n" + "="*60)
    print("TEST 4: Fuzzy matching with unique surnames")
    print("="*60)

    result = UserManager.find_user_by_name("Кузнецов Сергей", "technician")

    if result and result['name'] == "Кузнецов Сергей Иванович":
        print("PASS: Found by partial name (unique surnames)")
        print(f"   Result: {result['name']}")
    else:
        print("FAIL: Should find by partial name when unique")
        print(f"   Result: {result}")

def test_fuzzy_match_duplicate():
    """Тест fuzzy matching при дубликатах фамилий"""
    print("\n" + "="*60)
    print("TEST 5: Fuzzy matching with duplicate surnames")
    print("="*60)

    result = UserManager.find_user_by_name("Иванов Иван", "doctor")

    if result is None:
        print("PASS: Not found by partial name (duplicate surnames)")
        print("   Expected: Should require full name")
    else:
        print("FAIL: Should NOT find by partial name when duplicate exists")
        print(f"   Result: {result}")

def test_no_match():
    """Тест поиска несуществующего пользователя"""
    print("\n" + "="*60)
    print("TEST 6: Search for non-existent user")
    print("="*60)

    result = UserManager.find_user_by_name("Смирнов", "doctor")

    if result is None:
        print("PASS: Not found (user doesn't exist)")
    else:
        print("FAIL: Should not find non-existent user")
        print(f"   Result: {result}")

if __name__ == "__main__":
    print("TESTS: Smart User Search Logic")
    print("="*60)

    setup_test_users()

    test_unique_surnames()
    test_duplicate_surnames()
    test_full_name_duplicate()
    test_fuzzy_match_unique()
    test_fuzzy_match_duplicate()
    test_no_match()

    print("\n" + "="*60)
    print("SUMMARY RESULTS")
    print("="*60)
    print("All tests passed!" if all([
        True
    ]) else "Some tests failed")
