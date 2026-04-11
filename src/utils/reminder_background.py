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
        """Проверка заказов и отправка напоминаний с retry-логикой"""
        now = datetime.now(self.timezone)
        current_time = now.time()
        current_date = now.date()

        reminder_start_time = time(10, 0, 0)   # 10:00
        reminder_end_time = time(10, 30, 0)    # 10:30

        print(f"[DEBUG] Current Moscow time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[DEBUG] Last check date: {self.last_check_date}")

        if current_time < reminder_start_time:
            print(f"[DEBUG] Not yet reminder time (need {reminder_start_time.strftime('%H:%M')}), skipping")
            return

        if current_time > time(12, 0, 0):
            print("[DEBUG] Too late for reminders, skipping")
            if self.last_check_date != current_date:
                self.last_check_date = current_date
            return

        retry_mode = self.last_check_date == current_date
        if retry_mode:
            print(f"[DEBUG] RETRY MODE - Failed reminders will be resent")
        else:
            print(f"[DEBUG] FIRST CHECK - Processing all orders due tomorrow")

        print(f"[DEBUG] Checking for orders due tomorrow...")

        orders_due_tomorrow = self.reminder_service.get_orders_due_tomorrow()

        if not orders_due_tomorrow:
            print("[DEBUG] No orders due tomorrow")
            if not retry_mode:
                self.last_check_date = current_date
            return

        print(f"[DEBUG] Found {len(orders_due_tomorrow)} orders due tomorrow")

        admins = self.user_manager.get_all_admins()
        print(f"[DEBUG] Found {len(admins)} admins to notify")

        sent_count = 0
        fully_sent_orders = 0

        for order in orders_due_tomorrow:
            print(f"[DEBUG] Processing order {order['id']} for {order.get('patient_name', 'Unknown')}")

            technician_message = f"⏰ НАПОМИНАНИЕ О СРОКЕ ВЫПОЛНЕНИЯ!\n\n{self.reminder_service.format_reminder_message(order)}"

            sent_tech = await self.notification_service.send_reminder_to_technician(order, technician_message)

            admin_success = True
            technician_name = order.get('technician_name', 'Не указан')

            for admin in admins:
                admin_message = (
                    f"⏰ НАПОМИНАНИЕ О СРОКЕ ВЫПОЛНЕНИЯ!\n\n"
                    f"📋 Заказ №{order['id']}\n"
                    f"👤 Пациент: {order.get('patient_name', 'Не указан')}\n"
                    f"👨‍⚕️ Врач: {order.get('doctor_name', 'Не указан')}\n"
                    f"🔧 Техник: {technician_name}\n"
                    f"🔨 Вид работы: {order.get('work_type', 'Не указано')}\n"
                    f"📊 Количество: {order.get('quantity', 0)} шт\n"
                    f"📅 Срок выполнения: {order.get('deadline', 'Не указан')}\n"
                )
                try:
                    await self.bot.send_message(chat_id=admin['telegram_id'], text=admin_message)
                except Exception as e:
                    print(f"[DEBUG] Failed to send to admin {admin['name']}: {e}")
                    admin_success = False

            order_fully_sent = sent_tech and admin_success

            if order_fully_sent:
                print(f"[DEBUG] Order {order['id']} - ALL REMINDERS SENT SUCCESSFULLY")
                fully_sent_orders += 1
                if sent_tech:
                    sent_count += 1

                self.reminder_service.mark_reminder_sent(order['id'], 'today')
            else:
                print(f"[DEBUG] Order {order['id']} - SOME REMINDERS FAILED, will retry")
                if sent_tech:
                    sent_count += 1

        print(f"[DEBUG] Total technician reminders sent: {sent_count}")
        print(f"[DEBUG] Orders fully sent: {fully_sent_orders}/{len(orders_due_tomorrow)}")

        if fully_sent_orders == len(orders_due_tomorrow):
            print(f"[DEBUG] All orders fully processed, marking day as checked")
            self.last_check_date = current_date
        elif retry_mode and current_time >= reminder_end_time:
            print(f"[DEBUG] Retry window ended, marking day as checked")
            self.last_check_date = current_date
        elif not retry_mode and current_time >= reminder_end_time:
            print(f"[DEBUG] First check window ended, marking day as checked")
            self.last_check_date = current_date

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
