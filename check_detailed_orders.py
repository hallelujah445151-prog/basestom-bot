# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import get_connection

def check_orders_and_reminders():
    """Подробная проверка заказов и напоминаний"""

    print("=" * 70)
    print(" DETAILED ORDERS AND REMINDERS CHECK")
    print("=" * 70)
    print()

    now_moscow = datetime.now(ZoneInfo('Europe/Moscow'))
    today = now_moscow.strftime('%d.%m.%Y')
    tomorrow = (now_moscow + timedelta(days=1)).strftime('%d.%m.%Y')

    print(f"Current Moscow time: {now_moscow.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Today: {today}")
    print(f"Tomorrow: {tomorrow}")
    print()

    conn = get_connection()
    cursor = conn.cursor()

    print("ALL ORDERS:")
    print("-" * 70)

    cursor.execute('''
        SELECT id, deadline, patient_name, work_type, status, created_at
        FROM orders
        ORDER BY deadline ASC
    ''')

    rows = cursor.fetchall()

    for row in rows:
        order_id, deadline, patient, work, status, created = row
        status_indicator = "DUE TOMORROW" if deadline == tomorrow else ""
        print(f"Order {order_id}:")
        print(f"  Deadline: {deadline}")
        print(f"  Patient: {patient}")
        print(f"  Work: {work}")
        print(f"  Status: {status}")
        print(f"  Created: {created}")
        print(f"  {status_indicator}")
        print()

    print("\nALL REMINDERS:")
    print("-" * 70)

    cursor.execute('''
        SELECT r.id, r.order_id, r.reminder_type, r.sent_at,
               o.deadline as order_deadline,
               o.patient_name, o.work_type
        FROM reminders r
        JOIN orders o ON r.order_id = o.id
        ORDER BY r.id DESC
    ''')

    rows = cursor.fetchall()

    for row in rows:
        reminder_id, order_id, reminder_type, sent_at, deadline, patient, work = row
        print(f"Reminder {reminder_id}:")
        print(f"  Order ID: {order_id}")
        print(f"  Type: {reminder_type}")
        print(f"  Sent at: {sent_at}")
        print(f"  Order deadline: {deadline}")
        print(f"  Patient: {patient}")
        print(f"  Work: {work}")
        print()

    print("\nORDERS DUE TOMORROW WITHOUT REMINDERS:")
    print("-" * 70)

    cursor.execute('''
        SELECT o.id, o.deadline, o.patient_name, o.work_type
        FROM orders o
        WHERE o.deadline = ? AND o.status = 'in_progress'
        AND NOT EXISTS (
            SELECT 1 FROM reminders r WHERE r.order_id = o.id AND r.reminder_type = 'today'
        )
    ''', (tomorrow,))

    rows = cursor.fetchall()

    if rows:
        for row in rows:
            order_id, deadline, patient, work = row
            print(f"Order {order_id}:")
            print(f"  Deadline: {deadline}")
            print(f"  Patient: {patient}")
            print(f"  Work: {work}")
            print()
    else:
        print("None found")
        print()

    conn.close()

    print("=" * 70)


if __name__ == "__main__":
    check_orders_and_reminders()