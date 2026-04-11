"""Тест умной логики поиска пользователей с учетом реальных данных"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
from services.user_manager import UserManager

def test_duplicate_surnames_strict():
    """Тест: при дубликатах фамилий требуется полное имя"""
    print("\n" + "="*60)
    print("TEST: Duplicate surnames - strict matching required")
    print("="*60)

    print("\n1. Search by surname only (should NOT find):")
    result = UserManager.find_user_by_name("Кузнецов", "technician")
    if result is None:
        print("   PASS: Not found by surname (as expected)")
    else:
        print(f"   FAIL: Should not find by surname. Found: {result['name']}")

    print("\n2. Search by partial name (should NOT find):")
    result = UserManager.find_user_by_name("Кузнецов Сергей", "technician")
    if result is None:
        print("   PASS: Not found by partial name (as expected)")
    else:
        print(f"   FAIL: Should not find by partial name. Found: {result['name']}")

    print("\n3. Search by full name (should FIND):")
    result = UserManager.find_user_by_name("Кузнецов Сергей Иванович", "technician")
    if result and 'Кузнецов' in result['name']:
        print(f"   PASS: Found by full name: {result['name']}")
    else:
        print("   FAIL: Should find by full name")

def test_search_existing_user():
    """Тест: поиск существующего пользователя по полному имени"""
    print("\n" + "="*60)
    print("TEST: Search existing user by full name")
    print("="*60)

    result = UserManager.find_user_by_name("Иванов Иван Петрович", "doctor")
    if result and result['name'] == "Иванов Иван Петрович":
        print(f"   PASS: Found: {result['name']}")
    else:
        print("   FAIL: Should find by full name")

def test_nonexistent_user():
    """Тест: поиск несуществующего пользователя"""
    print("\n" + "="*60)
    print("TEST: Search non-existent user")
    print("="*60)

    result = UserManager.find_user_by_name("Смирнов Иван Иванович", "doctor")
    if result is None:
        print("   PASS: Not found (user doesn't exist)")
    else:
        print(f"   FAIL: Should not find non-existent user. Found: {result['name']}")

if __name__ == "__main__":
    print("SMART USER SEARCH LOGIC TESTS")
    print("Testing with real database data")

    test_duplicate_surnames_strict()
    test_search_existing_user()
    test_nonexistent_user()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("All tests completed!")
