# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.reminder_service import ReminderService
from services.notification_service import NotificationService
from services.user_manager import UserManager
from database import get_connection

def test_reminder_logic():
    """Тестирование логики напоминаний"""

    print("=" * 60)
    print("Testing reminder logic")
    print("=" * 60)
    print()

    now_moscow = datetime.now(ZoneInfo('Europe/Moscow'))
    today = now_moscow.strftime('%d.%m.%Y')
    tomorrow = (now_moscow + timedelta(days=1)).strftime('%d.%m.%Y')

    print(f"Current Moscow time: {now_moscow.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Today: {today}")
    print(f"Tomorrow: {tomorrow}")
    print()

    print("Checking for orders due tomorrow...")
    reminder_service = ReminderService()
    orders_due_tomorrow = reminder_service.get_orders_due_tomorrow()

    print(f"Found {len(orders_due_tomorrow)} orders due tomorrow")
    print()

    if orders_due_tomorrow:
        print("Orders:")
        for order in orders_due_tomorrow:
            print(f"  Order {order['id']}:")
            print(f"    Patient: {order.get('patient_name', 'N/A')}")
            print(f"    Work: {order.get('work_type', 'N/A')}")
            print(f"    Deadline: {order.get('deadline', 'N/A')}")
            print(f"    Technician: {order.get('technician_name', 'N/A')}")
            print(f"    Doctor: {order.get('doctor_name', 'N/A')}")
            print()
    else:
        print("No orders due tomorrow")
        print()

        print("Checking ALL orders in database...")
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, deadline, patient_name, work_type, status
            FROM orders
            ORDER BY deadline ASC
        ''')

        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            print(f"Order {row[0]}: deadline={row[1]}, patient={row[2]}, work={row[3]}, status={row[4]}")

    print()
    print("=" * 60)
    print("Test complete")
    print("=" * 60)


if __name__ == "__main__":
    test_reminder_logic()