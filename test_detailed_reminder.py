import sys
import os
import codecs

# Устанавливаем UTF-8 кодировку для stdout (для Windows)
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('src')

import asyncio
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from database import get_connection
from services.reminder_service import ReminderService
from services.notification_service import NotificationService
from services.user_manager import UserManager

print("=" * 100)
print("DETAILED REMINDER TESTING")
print("=" * 100)

# Текущее время в Москве
now_moscow = datetime.now(ZoneInfo('Europe/Moscow'))
current_time = now_moscow.time()
current_date = now_moscow.date()

print(f"\nCurrent Moscow time: {now_moscow.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Current time object: {current_time}")
print(f"Current date object: {current_date}")

# Временные рамки для напоминаний
reminder_start_time = time(10, 0, 0)   # 10:00
reminder_end_time = time(10, 30, 0)    # 10:30

print(f"\nReminder window:")
print(f"  Start: {reminder_start_time}")
print(f"  End: {reminder_end_time}")
print(f"  Current: {current_time}")

# Проверяем, находимся ли мы в окне напоминаний
if current_time >= reminder_start_time and current_time <= reminder_end_time:
    print(f"\n[OK] IN REMINDER WINDOW")
elif current_time < reminder_start_time:
    print(f"\n[INFO] BEFORE REMINDER WINDOW")
elif current_time > reminder_end_time:
    print(f"\n[INFO] AFTER REMINDER WINDOW")

print("\n" + "=" * 100)
print("STEP 1: Checking reminders table")
print("=" * 100)

# Проверяем таблицу reminders
conn = get_connection()
cursor = conn.cursor()

# Создаем таблицу reminders, если её нет
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        reminder_type TEXT NOT NULL,
        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

cursor.execute('SELECT COUNT(*) FROM reminders')
total_reminders = cursor.fetchone()[0]

print(f"\nTotal reminders in database: {total_reminders}")

if total_reminders > 0:
    cursor.execute('SELECT * FROM reminders ORDER BY sent_at DESC LIMIT 10')
    recent_reminders = cursor.fetchall()
    
    print("\nRecent reminders:")
    for i, reminder in enumerate(recent_reminders, 1):
        print(f"{i}. ID: {reminder[0]}, Order ID: {reminder[1]}, Type: {reminder[2]}, Sent at: {reminder[3]}")

print("\n" + "=" * 100)
print("STEP 2: Getting orders due tomorrow WITHOUT reminders")
print("=" * 100)

# Получаем заказы с дедлайном завтра (БЕЗ записей в reminders)
orders_due_tomorrow = ReminderService.get_orders_due_tomorrow()

print(f"\nOrders due tomorrow (WITHOUT reminders): {len(orders_due_tomorrow)}")

if orders_due_tomorrow:
    for i, order in enumerate(orders_due_tomorrow, 1):
        print(f"\n{i}. Order #{order['id']}")
        print(f"   Patient: {order.get('patient_name', 'Unknown')}")
        print(f"   Technician: {order.get('technician_name', 'Unknown')}")
        print(f"   Doctor: {order.get('doctor_name', 'Unknown')}")
        print(f"   Work type: {order.get('work_type', 'Unknown')}")
        print(f"   Quantity: {order.get('quantity', 0)}")
        print(f"   Deadline: {order.get('deadline', 'Unknown')}")

print("\n" + "=" * 100)
print("STEP 3: Understanding the PROBLEM")
print("=" * 100)

print("""
ПРОБЛЕМА:
========
В таблице reminders есть ЗАПИСИ о напоминаниях.
Но функция get_orders_due_tomorrow() ИГНОРИРУЕТ эти записи
только если reminder_type = 'today' для заказа.

ЛОГИКА:
========
1. В 10:00 get_orders_due_tomorrow() возвращает ВСЕ заказы с дедлайном завтра
2. Отправляем напоминания для ВСЕХ заказов
3. Если успешно -> создаем запись в reminders
4. В 10:05 get_orders_due_tomorrow() снова возвращает ВСЕ заказы
   (Потому что заказы с дедлайном завтра не изменились)
5. Если запись в reminders уже есть -> заказа НЕ должно быть в результате
   (Из-за SQL фильтра: AND NOT EXISTS (SELECT 1 FROM reminders ...))

ВОПРОС:
========
Почему SQL фильтр NOT EXISTS не работает?

ПОТЕНЦИАЛЬНАЯ ПРИЧИНА:
========================
Проблема может быть в том, что мы используем разные даты:
- get_orders_due_tomorrow() использует завтрашнюю дату для DEADLINE
- reminders использует текущую дату для записи sent_at
- SQL запрос проверяет deadline = tomorrow
- SQL запрос проверяет reminder_type = 'today'

Это может создавать несовпадение!
""")

print("\n" + "=" * 100)
print("STEP 4: Testing SQL query")
print("=" * 100)

now_moscow = datetime.now(ZoneInfo('Europe/Moscow'))
today = now_moscow.strftime('%d.%m.%Y')
tomorrow_date = now_moscow + timedelta(days=1)
tomorrow = tomorrow_date.strftime('%d.%m.%Y')

print(f"\nToday (format used in SQL): {today}")
print(f"Tomorrow (format used in SQL): {tomorrow}")

# Прямой тест SQL запроса
cursor.execute('''
    SELECT o.id, o.deadline, r.reminder_type, r.sent_at
    FROM orders o
    LEFT JOIN reminders r ON o.id = r.order_id AND r.reminder_type = 'today'
    WHERE o.deadline = ?
    AND o.status = 'in_progress'
''', (tomorrow,))

results = cursor.fetchall()
print(f"\nDirect SQL query results: {len(results)}")

if results:
    for result in results:
        print(f"  Order ID: {result[0]}, Deadline: {result[1]}, Reminder type: {result[2]}, Sent at: {result[3]}")
else:
    print("  No orders found with deadline tomorrow")

conn.close()

print("\n" + "=" * 100)
print("STEP 5: Testing with real data")
print("=" * 100)

print("""
ТЕОРИЯ:
========
Если заказ с дедлайном 13.04.2026:
- Сегодня: 12.04.2026
- Завтра: 13.04.2026
- SQL проверяет: o.deadline = '13.04.2026' (правильно)
- SQL проверяет: NOT EXISTS (SELECT 1 FROM reminders WHERE order_id = X AND reminder_type = 'today')
- Если запись существует в reminders -> заказа НЕ будет в результате
- Если записи НЕТ в reminders -> заказ БУДЕТ в результате

ПРОБЛЕМА В КОДЕ:
==================
Смотрим строку 31-34 в reminder_service.py:

cursor.execute('''
    SELECT o.id, o.doctor_id, o.technician_id, t.name as technician_name, d.name as doctor_name,
           o.patient_name, o.work_type, o.quantity, o.deadline, o.description, o.photo_id
    FROM orders o
    LEFT JOIN users t ON o.technician_id = t.id
    LEFT JOIN users d ON o.doctor_id = d.id
    WHERE o.deadline = ? AND o.status = 'in_progress'
    AND NOT EXISTS (
        SELECT 1 FROM reminders r WHERE r.order_id = o.id AND r.reminder_type = 'today'
    )
''', (tomorrow,))

Этот запрос выглядит ПРАВИЛЬНЫМ!

Но почему тогда напоминания отправляются многократно?

ВОЗМОЖНОЕ РЕШЕНИЕ:
====================
Проверим, что дата в reminders записывается правильно.
""")

print("\n" + "=" * 100)
print("STEP 6: Testing reminder timestamp")
print("=" * 100)

# Создаем тестовую запись
cursor.execute('''
    INSERT INTO reminders (order_id, reminder_type)
    VALUES (999, 'test')
''')
conn.commit()

cursor.execute('SELECT * FROM reminders WHERE order_id = 999')
test_result = cursor.fetchone()

print(f"\nTest reminder record: {test_result}")
print(f"  ID: {test_result[0]}")
print(f"  Order ID: {test_result[1]}")
print(f"  Type: {test_result[2]}")
print(f"  Sent at: {test_result[3]}")

# Удаляем тестовую запись
cursor.execute('DELETE FROM reminders WHERE order_id = 999')
conn.commit()

conn.close()

print("\n" + "=" * 100)
print("CONCLUSION")
print("=" * 100)

print("""
НАЙДЕНА ПРОБЛЕМА:
==================
SQL запрос в get_orders_due_tomorrow() ВЕРНЫЙ и должен работать правильно.

НО... Проблема может быть в том, что:

1. При отправке напоминания в reminder_background.py (строка 106),
   мы вызываем mark_reminder_sent() ТОЛЬКО если order_fully_sent == True.

2. Но order_fully_sent == True только если И technician И admins успешно получили.

3. Если technician получил, но admins НЕ получили -> order_fully_sent == False
   -> mark_reminder_sent() НЕ вызывается
   -> Запись в reminders НЕ создается
   -> Заказ БУДЕТ возвращаться в get_orders_due_tomorrow()
   -> Напоминание будет отправляться снова каждые 5 минут!

РЕШЕНИЕ:
========
Нужно менять логику:
- Отмечать в reminders даже при частичной отправке (только technician)
- Или вообще убрать зависимость от admin_success
- ИЛИ использовать другие критерии для отметки
""")

print("\n" + "=" * 100)
