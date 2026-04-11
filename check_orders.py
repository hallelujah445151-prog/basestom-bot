# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import get_connection

def check_orders():
    """Проверить заказы и дедлайны в базе данных"""
    conn = get_connection()
    cursor = conn.cursor()

    print("=== Заказы в базе данных ===\n")

    cursor.execute('''
        SELECT id, deadline, work_type, patient_name, technician_id, doctor_id, status
        FROM orders ORDER BY id DESC LIMIT 10
    ''')

    rows = cursor.fetchall()

    if not rows:
        print("Заказов нет")
    else:
        for row in rows:
            print(f"Order {row[0]}:")
            print(f"  Дедлайн: {row[1]}")
            print(f"  Работа: {row[2]}")
            print(f"  Пациент: {row[3]}")
            print(f"  Техник ID: {row[4]}")
            print(f"  Врач ID: {row[5]}")
            print(f"  Статус: {row[6]}")
            print()

    print("\n=== Напоминания ===\n")

    cursor.execute('''
        SELECT r.id, r.order_id, r.reminder_type, r.sent_at, o.deadline
        FROM reminders r
        JOIN orders o ON r.order_id = o.id
        ORDER BY r.id DESC LIMIT 10
    ''')

    rows = cursor.fetchall()

    if not rows:
        print("Напоминаний нет")
    else:
        for row in rows:
            print(f"Reminder {row[0]}:")
            print(f"  Order ID: {row[1]}")
            print(f"  Type: {row[2]}")
            print(f"  Sent at: {row[3]}")
            print(f"  Order deadline: {row[4]}")
            print()

    conn.close()


if __name__ == "__main__":
    check_orders()