import sqlite3
from datetime import datetime
import sys
import os
import difflib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class UserManager:
    """Управление пользователями"""

    @staticmethod
    def register_user(telegram_id: int, name: str, role: str, is_admin: bool = False, reference_id: int = None) -> bool:
        """Регистрация нового пользователя"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (telegram_id, name, role, is_admin, reference_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, name, role, 1 if is_admin else 0, reference_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    @staticmethod
    def get_user_by_telegram_id(telegram_id: int) -> dict:
        """Получить пользователя по telegram_id"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, telegram_id, name, role, is_admin, reference_id, is_active, created_at
            FROM users WHERE telegram_id = ?
        ''', (telegram_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'telegram_id': row[1],
                'name': row[2],
                'role': row[3],
                'is_admin': bool(row[4]),
                'reference_id': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7]
            }
        return None

    @staticmethod
    def get_all_users() -> list:
        """Получить всех пользователей"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, telegram_id, name, role, is_admin, reference_id, is_active, created_at
            FROM users ORDER BY created_at DESC
        ''')

        rows = cursor.fetchall()
        conn.close()

        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'telegram_id': row[1],
                'name': row[2],
                'role': row[3],
                'is_admin': bool(row[4]),
                'reference_id': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7]
            })

        return users

    @staticmethod
    def get_users_by_role(role: str) -> list:
        """Получить пользователей по роли"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, telegram_id, name, role, is_admin, reference_id, is_active, created_at
            FROM users WHERE role = ? AND is_active = 1
        ''', (role,))

        rows = cursor.fetchall()
        conn.close()

        users = []
        for row in rows:
            users.append({
                'id': row[0],
                'telegram_id': row[1],
                'name': row[2],
                'role': row[3],
                'is_admin': bool(row[4]),
                'reference_id': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7]
            })

        return users

    @staticmethod
    def get_all_admins() -> list:
        """Получить всех администраторов"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, telegram_id, name, role, is_admin, reference_id, is_active, created_at
            FROM users WHERE is_admin = 1 AND is_active = 1
        ''')

        rows = cursor.fetchall()
        conn.close()

        admins = []
        for row in rows:
            admins.append({
                'id': row[0],
                'telegram_id': row[1],
                'name': row[2],
                'role': row[3],
                'is_admin': bool(row[4]),
                'reference_id': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7]
            })

        return admins

    @staticmethod
    def update_user(user_id: int, **kwargs) -> bool:
        """Обновить данные пользователя"""
        conn = get_connection()
        cursor = conn.cursor()

        fields = []
        values = []

        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)

        values.append(user_id)

        try:
            cursor.execute(f'''
                UPDATE users SET {', '.join(fields)} WHERE id = ?
            ''', values)
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    @staticmethod
    def is_admin(telegram_id: int) -> bool:
        """Проверить, является ли пользователь администратором"""
        user = UserManager.get_user_by_telegram_id(telegram_id)
        return user is not None and user['role'] == 'dispatcher'

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Удалить пользователя"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        """Получить пользователя по ID"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, telegram_id, name, role, is_admin, reference_id, is_active, created_at
            FROM users WHERE id = ?
        ''', (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'telegram_id': row[1],
                'name': row[2],
                'role': row[3],
                'is_admin': bool(row[4]),
                'reference_id': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7]
            }
        return None

    @staticmethod
    def find_user_by_name(name: str, role: str) -> dict:
        """Найти пользователя по имени и роли с умной логикой
        
        ЛОГИКА ПОИСКА:
        1. Если фамилия уникальная → искать можно по фамилии и по полному имени
        2. Если фамилия НЕ уникальная (есть дубликаты) → искать ТОЛЬКО по полному имени
        """
        print(f"[DEBUG find_user_by_name] Searching for name='{name}', role='{role}'")
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, telegram_id, name, role, is_admin, reference_id, is_active, created_at
            FROM users WHERE role = ? AND is_active = 1
        ''', (role,))

        rows = cursor.fetchall()
        print(f"[DEBUG find_user_by_name] Found {len(rows)} users with role '{role}'")

        if not rows:
            print(f"[DEBUG find_user_by_name] No users found with role '{role}'")
            conn.close()
            return None

        name_lower = name.lower().strip()

        # Шаг 1: Проверяем точное совпадение полного имени
        for row in rows:
            user_name = row[2]
            user_name_lower = user_name.lower().strip()

            print(f"[DEBUG find_user_by_name] Checking exact match: '{user_name}' == '{name}'")

            if name_lower == user_name_lower:
                print(f"[DEBUG find_user_by_name] EXACT MATCH FOUND! user_name='{user_name}'")
                result = {
                    'id': row[0],
                    'telegram_id': row[1],
                    'name': row[2],
                    'role': row[3],
                    'is_admin': bool(row[4]),
                    'reference_id': row[5],
                    'is_active': bool(row[6]),
                    'created_at': row[7]
                }
                conn.close()
                return result

        # Шаг 2: Проверяем, есть ли дубликаты фамилий ДЛЯ КОНКРЕТНОЙ ФАМИЛИИ
        input_surname = name.split()[0].lower() if name.split() else name.lower()
        print(f"[DEBUG find_user_by_name] Input surname: '{input_surname}'")

        surnames = []
        for row in rows:
            user_name = row[2]
            surname = user_name.split()[0] if user_name.split() else user_name
            surnames.append(surname.lower())

        from collections import Counter
        surname_counts = Counter(surnames)
        
        # Проверяем, есть ли дубликаты ТОЛЬКО для искомой фамилии
        has_duplicate_surname = surname_counts.get(input_surname, 0) > 1
        print(f"[DEBUG find_user_by_name] Surname '{input_surname}' count: {surname_counts.get(input_surname, 0)}")
        print(f"[DEBUG find_user_by_name] Has duplicate for '{input_surname}': {has_duplicate_surname}")

        # Шаг 3а: Если есть дубликаты ЭТОЙ фамилии → полное имя или сокращенное имя (Мороков А.А.)
        if has_duplicate_surname:
            print(f"[DEBUG find_user_by_name] Duplicate surname '{input_surname}' detected - using FULL NAME or ABBREVIATED (e.g., 'Мороков А.А.')")
            
            # Проверяем, является ли имя сокращенным (например, "Мороков А.А." или "Иванов И.И.")
            name_parts = name.split()
            is_abbreviated = len(name_parts) == 2 and len(name_parts[1]) >= 2 and name_parts[1][-1] == '.'
            
            if is_abbreviated:
                # Парсим фамилию и инициалы
                surname_input = name_parts[0].lower()
                initials_input = name_parts[1].lower()
                print(f"[DEBUG find_user_by_name] Detected abbreviated name: surname='{surname_input}', initials='{initials_input}'")
                
                # Ищем пользователя с такой фамилией и инициалами
                for row in rows:
                    user_name = row[2]
                    user_parts = user_name.split()
                    
                    if len(user_parts) >= 2:
                        user_surname = user_parts[0].lower()
                        
                        # Формируем инициалы из полного имени (например, "Александр Александрович" → "А.А.")
                        user_initials = ''
                        if len(user_parts) >= 2:
                            user_initials = user_parts[1][0].lower() + '.'
                        if len(user_parts) >= 3:
                            user_initials += user_parts[2][0].lower() + '.'
                        
                        print(f"[DEBUG find_user_by_name] Checking: user_surname='{user_surname}', user_initials='{user_initials}'")
                        
                        if surname_input == user_surname and initials_input == user_initials:
                            print(f"[DEBUG find_user_by_name] ABBREVIATED MATCH FOUND! user_name='{user_name}'")
                            result = {
                                'id': row[0],
                                'telegram_id': row[1],
                                'name': row[2],
                                'role': row[3],
                                'is_admin': bool(row[4]),
                                'reference_id': row[5],
                                'is_active': bool(row[6]),
                                'created_at': row[7]
                            }
                            conn.close()
                            return result
            
            print(f"[DEBUG find_user_by_name] NO MATCH FOUND for '{name}'")
            print(f"[DEBUG find_user_by_name] Recommendation: Use full name (e.g., 'Мороков Александр Александрович' or 'Мороков А.А.')")
            conn.close()
            return None

        # Шаг 3б: Если фамилии уникальны → можно и фамилия, и полное имя
        print(f"[DEBUG find_user_by_name] Unique surnames - can search by surname OR full name")
        print(f"[DEBUG find_user_by_name] Trying fuzzy matching with lenient cutoff (0.6)...")

        # Создаем словарь фамилия -> список пользователей с этой фамилией
        surname_to_users = {}
        for row in rows:
            user_name = row[2]
            surname = user_name.split()[0] if user_name.split() else user_name
            if surname not in surname_to_users:
                surname_to_users[surname] = []
            surname_to_users[surname].append(row)

        # Сравниваем поисковую строку с фамилиями (не с полными именами)
        surnames = list(surname_to_users.keys())
        matches = difflib.get_close_matches(name, surnames, n=1, cutoff=0.6)
        print(f"[DEBUG find_user_by_name] Fuzzy matches (cutoff=0.6): {matches}")

        if matches:
            matched_surname = matches[0]
            # Если нашли совпадение фамилии, возвращаем первого пользователя с этой фамилией
            matching_user = surname_to_users[matched_surname][0]
            print(f"[DEBUG find_user_by_name] FUZZY MATCH FOUND! surname='{matched_surname}', user_name='{matching_user[2]}'")
            result = {
                'id': matching_user[0],
                'telegram_id': matching_user[1],
                'name': matching_user[2],
                'role': matching_user[3],
                'is_admin': bool(matching_user[4]),
                'reference_id': matching_user[5],
                'is_active': bool(matching_user[6]),
                'created_at': matching_user[7]
            }
            conn.close()
            return result

        print(f"[DEBUG find_user_by_name] NO MATCH FOUND for '{name}'")
        print(f"[DEBUG find_user_by_name] Recommendation: Check the name spelling or use full name")

        conn.close()
        return None

    @staticmethod
    def set_admin(telegram_id: int) -> bool:
        """Назначить пользователя администратором"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('UPDATE users SET is_admin = 1 WHERE telegram_id = ?', (telegram_id,))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    @staticmethod
    def is_user_admin(user: dict) -> bool:
        """Проверить, является ли пользователь администратором"""
        return user is not None and user.get('is_admin', False)
