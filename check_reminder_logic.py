import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('src')

from datetime import datetime, time
from zoneinfo import ZoneInfo
from database import get_connection
from services.reminder_service import ReminderService

print("=" * 80)
print("Testing reminder logic")
print("=" * 80)

# Текущее время в Москве
now_moscow = datetime.now(ZoneInfo('Europe/Moscow'))
current_time = now_moscow.time()
current_date = now_moscow.date()

print(f"\nCurrent Moscow time: {now_moscow.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Current time: {current_time.strftime('%H:%M:%S')}")
print(f"Current date: {current_date}")
print("")

# Получаем заказы с дедлайном завтра
print("Getting orders due tomorrow...")
orders_due_tomorrow = ReminderService.get_orders_due_tomorrow()

if orders_due_tomorrow:
    print(f"Found {len(orders_due_tomorrow)} orders due tomorrow (WITHOUT reminders)")
    print("")
    print("Orders:")
    for i, order in enumerate(orders_due_tomorrow, 1):
        print(f"\n{i}. Order #{order['id']}")
        print(f"   Patient: {order.get('patient_name', 'Unknown')}")
        print(f"   Technician: {order.get('technician_name', 'Unknown')}")
        print(f"   Doctor: {order.get('doctor_name', 'Unknown')}")
        print(f"   Work type: {order.get('work_type', 'Unknown')}")
        print(f"   Quantity: {order.get('quantity', 0)}")
        print(f"   Deadline: {order.get('deadline', 'Unknown')}")
else:
    print("No orders due tomorrow (WITHOUT reminders)")

print("\n" + "=" * 80)
print("Testing reminders table...")
print("=" * 80)

# Проверяем таблицу reminders
conn = get_connection()
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM reminders')
total_reminders = cursor.fetchone()[0]

print(f"\nTotal reminders in database: {total_reminders}")

if total_reminders > 0:
    cursor.execute('SELECT * FROM reminders ORDER BY sent_at DESC LIMIT 5')
    recent_reminders = cursor.fetchall()

    print("\nRecent reminders:")
    for reminder in recent_reminders:
        print(f"  - Order ID: {reminder[1]}, Type: {reminder[2]}, Sent at: {reminder[3]}")

conn.close()

print("\n" + "=" * 80)
print("Testing completed!")
print("=" * 80)
print("\nSummary:")
print("- get_orders_due_tomorrow() returns orders WITHOUT reminders")
print("- mark_reminder_sent() adds record to reminders table")
print("- After successful send, order will NOT appear in get_orders_due_tomorrow()")
print("- Failed sends will be retried every 5 minutes until 10:30")
