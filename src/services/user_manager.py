import sqlite3
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class UserManager:
    """Управление пользователями"""

    @staticmethod
    def register_user(telegram_id: int, name: str, role: str, reference_id: int = None) -> bool:
        """Регистрация нового пользователя"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (telegram_id, name, role, reference_id)
                VALUES (?, ?, ?, ?)
            ''', (telegram_id, name, role, reference_id))
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
            SELECT id, telegram_id, name, role, reference_id, is_active, created_at
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
                'reference_id': row[4],
                'is_active': bool(row[5]),
                'created_at': row[6]
            }
        return None

    @staticmethod
    def get_all_users() -> list:
        """Получить всех пользователей"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, telegram_id, name, role, reference_id, is_active, created_at
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
                'reference_id': row[4],
                'is_active': bool(row[5]),
                'created_at': row[6]
            })

        return users

    @staticmethod
    def get_users_by_role(role: str) -> list:
        """Получить пользователей по роли"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, telegram_id, name, role, reference_id, is_active, created_at
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
                'reference_id': row[4],
                'is_active': bool(row[5]),
                'created_at': row[6]
            })

        return users

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
