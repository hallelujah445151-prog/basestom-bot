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
        """Найти пользователя по имени и роли"""
        print(f"[DEBUG find_user_by_name] Searching for name='{name}', role='{role}'")
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, telegram_id, name, role, is_admin, reference_id, is_active, created_at
            FROM users WHERE role = ? AND is_active = 1
        ''', (role,))

        rows = cursor.fetchall()
        print(f"[DEBUG find_user_by_name] Found {len(rows)} users with role '{role}'")

        for row in rows:
            user_name = row[2]
            print(f"[DEBUG find_user_by_name] Checking user: '{user_name}'")
            if name.lower() in user_name.lower() or user_name.lower() in name.lower():
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

        print(f"[DEBUG find_user_by_name] No exact match, trying fuzzy matching...")
        user_names = [row[2] for row in rows]
        matches = difflib.get_close_matches(name, user_names, n=1, cutoff=0.7)
        print(f"[DEBUG find_user_by_name] Fuzzy matches: {matches}")

        if matches:
            for row in rows:
                if row[2] == matches[0]:
                    print(f"[DEBUG find_user_by_name] FUZZY MATCH FOUND! user_name='{row[2]}'")
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
