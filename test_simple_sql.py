import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('src')

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from database import get_connection

print("=" * 100)
print("SIMPLE SQL TEST")
print("=" * 100)

# Создаем заказ для тестирования
conn = get_connection()
cursor = conn.cursor()

# Время
now_moscow = datetime.now(ZoneInfo('Europe/Moscow'))
today = now_moscow.strftime('%d.%m.%Y')
tomorrow_date = now_moscow + timedelta(days=1)
tomorrow = tomorrow_date.strftime('%d.%m.%Y')

print(f"\nToday: {today}")
print(f"Tomorrow: {tomorrow}")

# 1. Проверяем существующие заказы с дедлайном завтра
cursor.execute('''
    SELECT id, deadline, status
    FROM orders
    WHERE deadline = ? AND status = 'in_progress'
''', (tomorrow,))

orders_before = cursor.fetchall()
print(f"\nOrders with deadline tomorrow (before adding reminder): {len(orders_before)}")
if orders_before:
    for order in orders_before:
        print(f"  - Order #{order[0]}, Deadline: {order[1]}, Status: {order[2]}")

# 2. Добавляем тестовое напоминание для Order #27
test_order_id = 27
cursor.execute('''
    INSERT INTO reminders (order_id, reminder_type)
    VALUES (?, 'today')
''', (test_order_id,))
conn.commit()
print(f"\n[TEST] Added reminder for Order #{test_order_id} with type 'today'")

# 3. Проверяем функцию get_orders_due_tomorrow()
import sys
sys.path.append('src')
from services.reminder_service import ReminderService

orders_after = ReminderService.get_orders_due_tomorrow()
print(f"\nOrders returned by get_orders_due_tomorrow() (after adding reminder): {len(orders_after)}")

if orders_after:
    for order in orders_after:
        print(f"  - Order #{order['id']}, Deadline: {order.get('deadline')}")
else:
    print("  - No orders returned")

# 4. Удаляем тестовое напоминание
cursor.execute('DELETE FROM reminders WHERE order_id = ? AND reminder_type = ?', (test_order_id, 'today'))
conn.commit()
print(f"\n[TEST] Removed reminder for Order #{test_order_id}")

# 5. Проверяем снова
orders_after_removal = ReminderService.get_orders_due_tomorrow()
print(f"\nOrders returned by get_orders_due_tomorrow() (after removing reminder): {len(orders_after_removal)}")

if orders_after_removal:
    for order in orders_after_removal:
        print(f"  - Order #{order['id']}, Deadline: {order.get('deadline')}")

conn.close()

print("\n" + "=" * 100)
print("CONCLUSION")
print("=" * 100)
print("""
РЕЗУЛЬТАТ ТЕСТА:
================
1. Было X заказов с дедлайном завтра
2. Добавили напоминание 'today' для Order #27
3. get_orders_due_tomorrow() вернул (X-1) заказов (без Order #27)
4. Удалили напоминание для Order #27
5. get_orders_due_tomorrow() снова вернул X заказов (с Order #27)

Если так работает, то SQL фильтр WORKS CORRECTLY!

НО... Проблема в том, что напоминания отправляются многократно с 10:00 до 12:00!

ВОЗМОЖНАЯ ПРИЧИНА:
====================
Проблема может быть в том, что мы добавляем напоминание 'today'
НО... Мы отправляем напоминания ЗА 1 ДЕН ДО ДЕДЛАЙНА!

То есть:
- Заказ с дедлайном 15.04.2026
- Напоминание отправляем 14.04.2026 (в 10:00)
- Сохраняем reminder_type = 'today'
- Но... SQL проверяет o.deadline = '15.04.2026'
- И reminder_type = 'today'

Это нормально работает!

НО... Что если проблема в том, что мы ИСПОЛЬЗУЕМ НЕ ТИП 'today'?
Давайте проверим, какой тип мы используем при отправке напоминаний.
""")

print("\n" + "=" * 100)
