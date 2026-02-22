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
        current_date = now.date()

        reminder_time = time(10, 0, 0)

        if current_time < reminder_time:
            return

        if self.last_check_date == current_date:
            return

        time_diff = (now.hour - 10) * 60 + now.minute
        if time_diff > 10:
            self.last_check_date = current_date
            return

        self.last_check_date = current_date

        orders_due_tomorrow = self.reminder_service.get_orders_due_tomorrow()

        if not orders_due_tomorrow:
            return

        dispatchers = self.user_manager.get_users_by_role('dispatcher')

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
