# ГОТОВОЕ РЕШЕНИЕ ДЛЯ НАПОМИНАНИЙ

## ТРЕБОВАНИЯ

1. Отправлять напоминания в 10:00 для заказов с дедлайном завтра
2. Если отправка не удалась → повторная попытка в 10:05
3. Если снова не удалось → повторная попытка в 10:10
4. Повторять каждые 5 минут до 10:30
5. После 10:30 → проверки прекращаются, напоминания НЕ отправляются

## ГОТОВОЕ РЕШЕНИЕ

### Файл: src/utils/reminder_background.py

```python
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
        self.reminder_start_time = time(10, 0, 0)   # 10:00
        self.reminder_end_time = time(10, 30, 0)    # 10:30

    def is_in_reminder_window(self, current_time: time) -> bool:
        """Проверяем, находимся ли мы в окне напоминаний (10:00-10:30)"""
        return self.reminder_start_time <= current_time <= self.reminder_end_time

    async def check_and_send_reminders(self):
        """Проверка заказов и отправка напоминаний с retry-логикой"""
        now = datetime.now(self.timezone)
        current_time = now.time()
        current_date = now.date()

        print(f"[DEBUG] Current Moscow time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[DEBUG] Last check date: {self.last_check_date}")
        print(f"[DEBUG] Current time: {current_time.strftime('%H:%M:%S')}")

        # Проверяем, находимся ли мы в окне напоминаний
        if not self.is_in_reminder_window(current_time):
            if current_time < self.reminder_start_time:
                print(f"[DEBUG] Not yet reminder time (need {self.reminder_start_time.strftime('%H:%M')}), skipping")
            else:
                print("[DEBUG] Too late for reminders, skipping")
                if self.last_check_date != current_date:
                    self.last_check_date = current_date
            return

        print(f"[DEBUG] IN REMINDER WINDOW: {current_time.strftime('%H:%M:%S')}")

        # Проверяем, нужно ли выполнять проверку
        if self.last_check_date == current_date:
            print(f"[DEBUG] RETRY MODE - Processing failed reminders")
            retry_mode = True
        else:
            print(f"[DEBUG] FIRST CHECK - Processing all orders due tomorrow")
            retry_mode = False
            self.last_check_date = current_date

        print(f"[DEBUG] Checking for orders due tomorrow...")

        orders_due_tomorrow = self.reminder_service.get_orders_due_tomorrow()

        if not orders_due_tomorrow:
            print("[DEBUG] No orders due tomorrow")
            return

        print(f"[DEBUG] Found {len(orders_due_tomorrow)} orders due tomorrow")

        admins = self.user_manager.get_all_admins()
        print(f"[DEBUG] Found {len(admins)} admins to notify")

        sent_count = 0
        fully_sent_orders = 0
        failed_orders = []

        for order in orders_due_tomorrow:
            print(f"[DEBUG] Processing order {order['id']} for {order.get('patient_name', 'Unknown')}")

            technician_message = f"⏰ НАПОМИНАНИЕ О СРОКЕ ВЫПОЛНЕНИЯ!\n\n{self.reminder_service.format_reminder_message(order)}"

            # Отправляем технику
            try:
                await self.notification_service.send_reminder_to_technician(order, technician_message)
                sent_tech = True
                print(f"[DEBUG] Order {order['id']} - Reminder sent to technician")
            except Exception as e:
                sent_tech = False
                print(f"[DEBUG] Order {order['id']} - Failed to send to technician: {e}")

            # Отправляем администраторам
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

            # Если отправка технику успешна → отмечаем напоминание как отправленное
            if sent_tech:
                print(f"[DEBUG] Order {order['id']} - REMINDER SENT, marking as processed")
                self.reminder_service.mark_reminder_sent(order['id'], 'today')
                sent_count += 1
                fully_sent_orders += 1
            else:
                print(f"[DEBUG] Order {order['id']} - FAILED, will retry")
                failed_orders.append(order['id'])

        print(f"[DEBUG] Total technician reminders sent: {sent_count}")
        print(f"[DEBUG] Orders successfully sent: {fully_sent_orders}/{len(orders_due_tomorrow)}")
        print(f"[DEBUG] Orders failed: {len(failed_orders)}")

        # Если ВСЕ заказы успешно отправлены → можно прекратить проверки для сегодняшнего дня
        if fully_sent_orders == len(orders_due_tomorrow):
            print(f"[DEBUG] All orders successfully sent, marking day as checked")
            # НЕ обновляем last_check_date, чтобы завтра отправка была в 10:00

    async def start_background_task(self):
        """Запуск фонового процесса"""
        self.running = True
        print("Reminder background task started (checking every 5 minutes)")

        while self.running:
            try:
                await self.check_and_send_reminders()
            except Exception as e:
                print(f"Error in background task: {e}")

            # Проверка каждые 5 минут
            await asyncio.sleep(300)

    def stop(self):
        """Остановка фонового процесса"""
        self.running = False
        print("Reminder background task stopped")


async def run_background_task(bot_token: str):
    """Запуск фоновой задачи"""
    task = ReminderBackgroundTask(bot_token)
    await task.start_background_task()
```
