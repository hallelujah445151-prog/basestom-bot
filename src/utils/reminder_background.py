import asyncio
import os
import sys
from datetime import datetime, time
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

    async def check_and_send_reminders(self):
        """Проверка заказов и отправка напоминаний"""
        now = datetime.now()
        current_time = now.time()

        reminder_start_time = time(9, 50, 0)
        reminder_end_time = time(10, 30, 0)

        if not (reminder_start_time <= current_time <= reminder_end_time):
            return

        orders_due_tomorrow = self.reminder_service.get_orders_due_tomorrow()

        if not orders_due_tomorrow:
            return

        dispatchers = self.user_manager.get_all_admins()

        for order in orders_due_tomorrow:
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
