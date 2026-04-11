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

async def test_send_reminders_now():
    """Ручная отправка напоминаний для тестирования"""

    print("=" * 60)
    print("MANUAL REMINDER TEST - Sending now!")
    print("=" * 60)
    print()

    reminder_service = ReminderService()
    notification_service = NotificationService(os.getenv('BOT_TOKEN'))
    user_manager = UserManager()

    orders_due_tomorrow = reminder_service.get_orders_due_tomorrow()

    print(f"Found {len(orders_due_tomorrow)} orders due tomorrow")
    print()

    if not orders_due_tomorrow:
        print("No orders due tomorrow - nothing to send")
        return

    admins = user_manager.get_all_admins()
    print(f"Found {len(admins)} admins to notify")
    print()

    sent_count = 0
    for order in orders_due_tomorrow:
        print(f"Processing order {order['id']}...")

        technician_message = (
            f"⏰ НАПОМИНАНИЕ О СРОКЕ ВЫПОЛНЕНИЯ!\n\n"
            f"{reminder_service.format_reminder_message(order)}"
        )

        sent_tech = await notification_service.send_reminder_to_technician(order, technician_message)
        if sent_tech:
            sent_count += 1
            print(f"  -> Sent to technician {order.get('technician_name', 'N/A')}")
        else:
            print(f"  -> Failed to send to technician")

        technician_name = order.get('technician_name', 'Не указан')

        for admin in admins:
            admin_message = (
                f"⏰ НАПОМИНАНИЕ О СРОКЕ ВЫПОЛНЕНИЯ!\n\n"
                f"📋 Заказ №{order['id']}\n"
                f"👤 Пациент: {order.get('patient_name', 'Не указан')}\n"
                f"🔧 Техник: {technician_name}\n"
                f"🔨 Вид работы: {order.get('work_type', 'Не указано')}\n"
                f"📊 Количество: {order.get('quantity', 0)} шт\n"
                f"📅 Срок выполнения: {order.get('deadline', 'Не указан')}\n"
            )

            try:
                await notification_service.bot.send_message(
                    chat_id=admin['telegram_id'],
                    text=admin_message
                )
                print(f"  -> Sent to admin {admin['name']}")
            except Exception as e:
                print(f"  -> Failed to send to admin {admin['name']}: {e}")

        reminder_service.mark_reminder_sent(order['id'], 'today')
        print(f"  -> Marked reminder as sent in database")
        print()

    print("=" * 60)
    print(f"Test complete! Sent {sent_count}/{len(orders_due_tomorrow)} technician reminders")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_send_reminders_now())