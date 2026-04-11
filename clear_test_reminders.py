# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import get_connection

def clear_test_reminders():
    """Очистить напоминания для тестовых заказов"""

    print("=" * 70)
    print(" CLEARING TEST REMINDERS")
    print("=" * 70)
    print()

    conn = get_connection()
    cursor = conn.cursor()

    # Показать текущие напоминания
    print("Current reminders:")
    cursor.execute('SELECT id, order_id, reminder_type, sent_at FROM reminders ORDER BY id DESC LIMIT 10')
    rows = cursor.fetchall()

    for row in rows:
        print(f"  Reminder {row[0]}: Order {row[1]}, Type: {row[2]}, Sent: {row[3]}")

    print()

    # Очистить напоминания для заказов 15, 16, 17, 18
    test_order_ids = [15, 16, 17, 18]

    cursor.execute('DELETE FROM reminders WHERE order_id IN (?, ?, ?, ?)', test_order_ids)
    deleted_count = cursor.rowcount
    conn.commit()

    print(f"Deleted {deleted_count} reminders for test orders 15, 16, 17, 18")
    print()

    # Показать оставшиеся напоминания
    print("Remaining reminders:")
    cursor.execute('SELECT id, order_id, reminder_type, sent_at FROM reminders ORDER BY id DESC LIMIT 10')
    rows = cursor.fetchall()

    if rows:
        for row in rows:
            print(f"  Reminder {row[0]}: Order {row[1]}, Type: {row[2]}, Sent: {row[3]}")
    else:
        print("  None")

    conn.close()

    print()
    print("=" * 70)
    print(" READY FOR TESTING!")
    print("=" * 70)
    print()
    print("Now you can run test_send_reminders_now.py to send reminders")


if __name__ == "__main__":
    clear_test_reminders()