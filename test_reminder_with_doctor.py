# -*- coding: utf-8 -*-
import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

from services.reminder_service import ReminderService
from services.notification_service import NotificationService
from services.user_manager import UserManager
from database import get_connection

def clear_test_reminders():
    """Очистить напоминания для тестовых заказов"""

    print("=" * 70)
    print(" CLEARING TEST REMINDERS")
    print("=" * 70)
    print()

    conn = get_connection()
    cursor = conn.cursor()

    test_order_ids = [15, 16, 17, 18]

    cursor.execute('DELETE FROM reminders WHERE order_id IN (?, ?, ?, ?)', test_order_ids)
    deleted_count = cursor.rowcount
    conn.commit()

    print(f"Deleted {deleted_count} reminders for test orders 15, 16, 17, 18")

    cursor.execute('SELECT id, order_id, reminder_type, sent_at FROM reminders')
    rows = cursor.fetchall()

    print(f"\nRemaining reminders: {len(rows)}")
    for row in rows:
        print(f"  Reminder {row[0]}: Order {row[1]}, Type: {row[2]}, Sent: {row[3]}")

    conn.close()

    print()
    print("READY FOR TESTING!")


async def test_reminder_with_doctor_info():
    """Тестирование напоминаний с информацией о враче"""

    print("=" * 70)
    print(" TESTING REMINDERS WITH DOCTOR INFO")
    print("=" * 70)
    print()

    reminder_service = ReminderService()
    notification_service = NotificationService(os.getenv('BOT_TOKEN'))
    user_manager = UserManager()

    orders_due = reminder_service.get_orders_due_tomorrow()

    if not orders_due:
        print("No orders due tomorrow - create test orders first")
        return

    print(f"Found {len(orders_due)} orders to process")

    admins = user_manager.get_all_admins()
    print(f"Found {len(admins)} admins to notify")

    for order in orders_due:
        print(f"\n--- Processing Order {order['id']} ---")

        print("Order data:")
        print(f"  ID: {order['id']}")
        print(f"  Patient: {order.get('patient_name', 'N/A')}")
        print(f"  Doctor: {order.get('doctor_name', 'N/A')}")
        print(f"  Technician: {order.get('technician_name', 'N/A')}")
        print(f"  Work: {order.get('work_type', 'N/A')}")
        print(f"  Quantity: {order.get('quantity', 0)}")
        print(f"  Deadline: {order.get('deadline', 'N/A')}")

        print("\nTechnician message:")
        technician_message = f"TEST - Напоминание о сроке выполнения!\n\n{reminder_service.format_reminder_message(order)}"
        print(f"Message preview: ... (see Telegram for full message)")

        real_technician_message = f"⏰ TEST - Напоминание о сроке выполнения!\n\n{reminder_service.format_reminder_message(order)}"
        sent_tech = await notification_service.send_reminder_to_technician(order, real_technician_message)

        admin_success = True
        technician_name = order.get('technician_name', 'Не указан')

        print("\nAdmin message:")
        admin_message = (
            f"TEST - Напоминание о сроке выполнения!\n\n"
            f"Заказ №{order['id']}\n"
            f"Пациент: {order.get('patient_name', 'Не указан')}\n"
            f"Врач: {order.get('doctor_name', 'Не указан')}\n"
            f"Техник: {technician_name}\n"
            f"Вид работы: {order.get('work_type', 'Не указано')}\n"
            f"Количество: {order.get('quantity', 0)} шт\n"
            f"Срок выполнения: {order.get('deadline', 'Не указан')}\n"
        )
        print(f"Message preview: ... (see Telegram for full message)")

        for admin in admins:
            real_admin_message = (
                f"⏰ TEST - Напоминание о сроке выполнения!\n\n"
                f"📋 Заказ №{order['id']}\n"
                f"👤 Пациент: {order.get('patient_name', 'Не указан')}\n"
                f"👨‍⚕️ Врач: {order.get('doctor_name', 'Не указан')}\n"
                f"🔧 Техник: {technician_name}\n"
                f"🔨 Вид работы: {order.get('work_type', 'Не указано')}\n"
                f"📊 Количество: {order.get('quantity', 0)} шт\n"
                f"📅 Срок выполнения: {order.get('deadline', 'Не указан')}\n"
            )
            try:
                await notification_service.bot.send_message(
                    chat_id=admin['telegram_id'],
                    text=real_admin_message
                )
                print(f"\nSent to admin {admin['name']} (ID: {admin['telegram_id']})")
            except Exception as e:
                print(f"\nFailed to send to admin {admin['name']}: {e}")
                admin_success = False

        order_fully_sent = sent_tech and admin_success

        if order_fully_sent:
            print(f"\nRESULT: Order FULLY SENT - Marked as completed")
            reminder_service.mark_reminder_sent(order['id'], 'today')
        else:
            print(f"\nRESULT: Order PARTIALLY SENT - Will be retried")

    print()
    print("=" * 70)
    print(" TEST COMPLETE")
    print("=" * 70)
    print()
    print("Check your Telegram for reminders with doctor information!")


if __name__ == "__main__":
    clear_test_reminders()
    asyncio.run(test_reminder_with_doctor_info())