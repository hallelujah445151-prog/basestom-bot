# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import get_connection

def create_test_order():
    """Создать тестовый заказ с дедлайном на завтра"""
    from datetime import datetime, timedelta

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO orders (doctor_id, technician_id, patient_name, work_type, quantity, deadline, description, photo_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            None,  # doctor_id
            5,     # technician_id (Плюхин)
            "Тестовый пациент",
            "цельноцирконевая коронка на винте",
            1,
            tomorrow,
            "Тестовый заказ для проверки напоминаний",
            None
        ))

        order_id = cursor.lastrowid
        conn.commit()

        print(f"Test order created!")
        print(f"   ID: {order_id}")
        print(f"   Patient: Test patient")
        print(f"   Work: цельноцирконевая коронка на винте")
        print(f"   Deadline: {tomorrow}")
        print(f"   Technician ID: 5")
        print()
        print("Reminder should arrive tomorrow at 10:00")
        print("Recipients: Technician and all admins")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    create_test_order()