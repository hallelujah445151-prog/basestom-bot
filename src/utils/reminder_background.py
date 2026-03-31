import asyncio
import os
import sys
from datetime import datetime, time
from zoneinfo import ZoneInfo
from telegram import Bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.reminder_service import ReminderService
from services.notification_service import NotificationService
from services.user_manager import UserManager


class ReminderBackgroundTask:
    """Фоновая задача для проверки сроков и отправки напоминаний"""

    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token)
        self.reminder_service = ReminderService()
        self.notification_service = NotificationService(bot_token)
        self.user_manager = UserManager()
        self.running = False
        self.last_check_date = None
        self.timezone = ZoneInfo('Europe/Moscow')

    async def check_and_send_reminders(self):
        """Проверка заказов и отправка напоминаний"""
        now = datetime.now(self.timezone)
        current_time = now.time()

        reminder_start_time = time(9, 50, 0)
        reminder_end_time = time(10, 30, 0)

        print(f"[DEBUG] Current Moscow time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

        if not (reminder_start_time <= current_time <= reminder_end_time):
            return

        print(f"[DEBUG] Time window matched! Checking for orders due tomorrow...")

        orders_due_tomorrow = self.reminder_service.get_orders_due_tomorrow()

        if not orders_due_tomorrow:
            print("[DEBUG] No orders due tomorrow")
            return

        print(f"[DEBUG] Found {len(orders_due_tomorrow)} orders due tomorrow")

        dispatchers = self.user_manager.get_all_admins()

        for order in orders_due_tomorrow:
            print(f"[DEBUG] Processing order {order['id']} for {order.get('patient_name', 'Unknown')}")
            reminder_message = self.reminder_service.format_reminder_message(order)

            await self.notification_service.send_reminder_to_technician(order, reminder_message)

            technician_name = order.get('patient_name', 'Не указан')

            for dispatcher in dispatchers:
                await self.notification_service.send_reminder_to_dispatcher(
                    dispatcher['telegram_id'],
                    order,
                    technician_name
                )

            self.reminder_service.mark_reminder_sent(order['id'], 'tomorrow')
            print(f"[DEBUG] Reminder sent for order {order['id']}")

    async def start_background_task(self):
        """Запуск фонового процесса"""
        self.running = True
        print("Reminder background task started (checking every 5 minutes)")

        while self.running:
            try:
                await self.check_and_send_reminders()
            except Exception as e:
                print(f"Error in background task: {e}")

            await asyncio.sleep(300)

    def stop(self):
        """Остановка фонового процесса"""
        self.running = False
        print("Reminder background task stopped")


async def run_background_task(bot_token: str):
    """Запуск фоновой задачи"""
    task = ReminderBackgroundTask(bot_token)
    await task.start_background_task()
