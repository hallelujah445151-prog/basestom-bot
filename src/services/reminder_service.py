from datetime import datetime, timedelta
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class ReminderService:
    """Сервис для проверки сроков выполнения заказов и отправки напоминаний"""

    @staticmethod
    def get_orders_due_tomorrow():
        """Получить заказы с дедлайном на завтра"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT o.id, o.doctor_id, o.technician_id, t.name as technician_name, d.name as doctor_name,
                   o.patient_name, o.work_type, o.quantity, o.deadline, o.description, o.photo_id
            FROM orders o
            LEFT JOIN users t ON o.technician_id = t.id
            LEFT JOIN users d ON o.doctor_id = d.id
            WHERE o.deadline = ? AND o.status = 'in_progress'
            AND NOT EXISTS (
                SELECT 1 FROM reminders r WHERE r.order_id = o.id AND r.reminder_type = 'tomorrow'
            )
        ''', (tomorrow,))

        rows = cursor.fetchall()
        conn.close()

        orders = []
        for row in rows:
            orders.append({
                'id': row[0],
                'doctor_id': row[1],
                'technician_id': row[2],
                'technician_name': row[3],
                'doctor_name': row[4],
                'patient_name': row[5],
                'work_type': row[6],
                'quantity': row[7],
                'deadline': row[8],
                'description': row[9],
                'photo_id': row[10]
            })

        return orders

    @staticmethod
    def get_orders_due_today():
        """Получить заказы с дедлайном сегодня"""
        today = datetime.now().strftime('%d.%m.%Y')

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT o.id, o.doctor_id, o.technician_id, t.name as technician_name, d.name as doctor_name,
                   o.patient_name, o.work_type, o.quantity, o.deadline, o.description, o.photo_id
            FROM orders o
            LEFT JOIN users t ON o.technician_id = t.id
            LEFT JOIN users d ON o.doctor_id = d.id
            WHERE o.deadline = ? AND o.status = 'in_progress'
        ''', (today,))

        rows = cursor.fetchall()
        conn.close()

        orders = []
        for row in rows:
            orders.append({
                'id': row[0],
                'doctor_id': row[1],
                'technician_id': row[2],
                'technician_name': row[3],
                'doctor_name': row[4],
                'patient_name': row[5],
                'work_type': row[6],
                'quantity': row[7],
                'deadline': row[8],
                'description': row[9],
                'photo_id': row[10]
            })

        return orders

    @staticmethod
    def format_reminder_message(order: dict) -> str:
        """Форматирование сообщения напоминания"""
        message = (
            f"⏰ НАПОМИНАНИЕ О СРОКЕ ВЫПОЛНЕНИЯ!\n\n"
            f"📋 Заказ №{order['id']}\n"
            f"👤 Пациент: {order.get('patient_name', 'Не указан')}\n"
            f"👨‍⚕️ Врач: {order.get('doctor_name', 'Не указан')}\n"
            f"🔨 Вид работы: {order.get('work_type', 'Не указано')}\n"
            f"📊 Количество: {order.get('quantity', 0)} шт\n"
            f"📅 Срок выполнения: {order.get('deadline', 'Не указан')}\n"
        )

        return message

    @staticmethod
    def mark_reminder_sent(order_id: int, reminder_type: str = 'tomorrow'):
        """Отметить напоминание как отправленное"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO reminders (order_id, reminder_type)
                VALUES (?, ?)
            ''', (order_id, reminder_type))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка отметки напоминания: {e}")
            return False
        finally:
            conn.close()
