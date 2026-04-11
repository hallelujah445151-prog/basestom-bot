# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

def test_database():
    """Тестирование подключения к БД"""
    print("=" * 60)
    print("1. Testing database connection")
    print("=" * 60)

    try:
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM reminders")
        reminder_count = cursor.fetchone()[0]

        conn.close()

        print(f"OK - Database connection OK")
        print(f"   Orders: {order_count}")
        print(f"   Users: {user_count}")
        print(f"   Reminders: {reminder_count}")
        return True

    except Exception as e:
        print(f"FAIL - Database error: {e}")
        return False


def test_reminder_service():
    """Тестирование сервиса напоминаний"""
    print("\n" + "=" * 60)
    print("2. Testing reminder service")
    print("=" * 60)

    try:
        from services.reminder_service import ReminderService

        reminder_service = ReminderService()

        now_moscow = datetime.now(ZoneInfo('Europe/Moscow'))
        tomorrow = (now_moscow + timedelta(days=1)).strftime('%d.%m.%Y')

        print(f"Current Moscow time: {now_moscow.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tomorrow date: {tomorrow}")

        orders_due = reminder_service.get_orders_due_tomorrow()

        print(f"\nOK - Reminder service OK")
        print(f"   Found {len(orders_due)} orders due tomorrow")

        if orders_due:
            print("\n   Orders:")
            for order in orders_due:
                print(f"     - Order {order['id']}: {order.get('patient_name', 'N/A')}")

        return True

    except Exception as e:
        print(f"FAIL - Reminder service error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_manager():
    """Тестирование менеджера пользователей"""
    print("\n" + "=" * 60)
    print("3. Testing user manager")
    print("=" * 60)

    try:
        from services.user_manager import UserManager

        all_users = UserManager.get_all_users()
        admins = UserManager.get_all_admins()
        technicians = UserManager.get_users_by_role('technician')

        print(f"OK - User manager OK")
        print(f"   Total users: {len(all_users)}")
        print(f"   Admins: {len(admins)}")
        print(f"   Technicians: {len(technicians)}")

        if admins:
            print("\n   Admins:")
            for admin in admins:
                print(f"     - {admin['name']} (ID: {admin['telegram_id']})")

        return True

    except Exception as e:
        print(f"FAIL - User manager error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_notification_service():
    """Тестирование сервиса уведомлений"""
    print("\n" + "=" * 60)
    print("4. Testing notification service")
    print("=" * 60)

    try:
        from services.notification_service import NotificationService

        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            print("FAIL - BOT_TOKEN not found in environment")
            return False

        notification_service = NotificationService(bot_token)

        print(f"OK - Notification service initialized OK")
        print(f"   Bot token: {bot_token[:10]}...")
        return True

    except Exception as e:
        print(f"FAIL - Notification service error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_telegram_connection():
    """Тестирование подключения к Telegram API"""
    print("\n" + "=" * 60)
    print("5. Testing Telegram API connection")
    print("=" * 60)

    try:
        from telegram import Bot

        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            print("FAIL - BOT_TOKEN not found in environment")
            return False

        bot = Bot(token=bot_token)

        try:
            me = await bot.get_me()
            print(f"OK - Telegram API connection OK")
            print(f"   Bot name: {me.full_name}")
            print(f"   Bot username: @{me.username}")
            return True
        except Exception as e:
            print(f"FAIL - Telegram API connection failed: {e}")
            print(f"   Possible reasons:")
            print(f"   - VPN not enabled")
            print(f"   - Internet connection issues")
            print(f"   - Telegram API blocked")
            return False

    except Exception as e:
        print(f"FAIL - Telegram bot initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_reminder_sending():
    """Тестирование отправки напоминаний"""
    print("\n" + "=" * 60)
    print("6. Testing reminder sending")
    print("=" * 60)

    try:
        from services.reminder_service import ReminderService
        from services.notification_service import NotificationService
        from services.user_manager import UserManager

        reminder_service = ReminderService()
        notification_service = NotificationService(os.getenv('BOT_TOKEN'))
        user_manager = UserManager()

        orders_due = reminder_service.get_orders_due_tomorrow()

        if not orders_due:
            print("WARN - No orders due tomorrow - skipping test")
            return True

        print(f"Found {len(orders_due)} orders to send reminders for")

        admins = user_manager.get_all_admins()
        print(f"Found {len(admins)} admins to notify")

        success_count = 0
        for order in orders_due:
            print(f"\nProcessing order {order['id']}...")

            technician_message = (
                f"⏰ TEST REMINDER - Напоминание о сроке выполнения!\n\n"
                f"{reminder_service.format_reminder_message(order)}"
            )

            sent_tech = await notification_service.send_reminder_to_technician(
                order, technician_message
            )

            if sent_tech:
                success_count += 1
                print(f"  OK - Sent to technician")
            else:
                print(f"  FAIL - Failed to send to technician")

            technician_name = order.get('technician_name', 'Не указан')

            for admin in admins:
                admin_message = (
                    f"⏰ TEST REMINDER - Напоминание о сроке выполнения!\n\n"
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
                    print(f"  OK - Sent to admin {admin['name']}")
                except Exception as e:
                    print(f"  FAIL - Failed to send to admin {admin['name']}: {e}")

        print(f"\nOK - Reminder sending test complete")
        print(f"   Sent {success_count}/{len(orders_due)} technician reminders")

        return True

    except Exception as e:
        print(f"FAIL - Reminder sending error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Основная функция тестирования"""
    print("\n" + "=" * 70)
    print(" COMPREHENSIVE BOT TESTING")
    print("=" * 70)

    results = {}

    results['database'] = test_database()
    results['reminder_service'] = test_reminder_service()
    results['user_manager'] = test_user_manager()
    results['notification_service'] = test_notification_service()

    results['telegram'] = await test_telegram_connection()

    if results['telegram']:
        print("\nOK - Telegram connection OK! Testing reminder sending...")
        results['reminder_sending'] = await test_reminder_sending()
    else:
        print("\nFAIL - Telegram connection failed - skipping reminder sending test")
        results['reminder_sending'] = False

    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)

    for test, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test}")

    all_passed = all(results.values())

    print("\n" + "=" * 70)
    if all_passed:
        print(" ALL TESTS PASSED - Bot is ready!")
    else:
        print(" SOME TESTS FAILED - Check the errors above")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())