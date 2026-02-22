from telegram import Bot, InputFile
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_manager import UserManager


class NotificationService:
    """Сервис для отправки уведомлений"""

    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token)
        self.user_manager = UserManager()

    async def send_to_technician(self, order: dict, photo_id: str = None):
        """Отправить уведомление технику"""
        if not order.get('technician_id'):
            return False

        technicians = self.user_manager.get_users_by_role('technician')
        technician = None

        for tech in technicians:
            if tech['reference_id'] == order['technician_id']:
                technician = tech
                break

        if not technician:
            return False

        message = (
            f"🔧 Вам назначена новая работа!\n\n"
            f"👤 Пациент: {order.get('patient_name', 'Не указан')}\n"
            f"👨‍⚕️ Врач: {order.get('doctor_name', 'Не указан')}\n"
            f"🔨 Вид работы: {order.get('work_type', 'Не указано')}\n"
            f"📊 Количество: {order.get('quantity', 0)} шт\n"
        )

        if order.get('deadline'):
            message += f"📅 Срок выполнения: {order['deadline']}\n"

        if order.get('description'):
            message += f"\n📝 Заметки: {order['description']}"

        try:
            if photo_id:
                await self.bot.send_photo(
                    chat_id=technician['telegram_id'],
                    photo=photo_id,
                    caption=message
                )
            else:
                await self.bot.send_message(
                    chat_id=technician['telegram_id'],
                    text=message
                )
            return True
        except Exception as e:
            print(f"Ошибка отправки уведомления технику: {e}")
            return False

    async def send_to_doctor(self, order: dict, photo_id: str = None):
        """Отправить уведомление врачу"""
        if not order.get('doctor_id'):
            return False

        doctors = self.user_manager.get_users_by_role('doctor')
        doctor = None

        for doc in doctors:
            if doc['reference_id'] == order['doctor_id']:
                doctor = doc
                break

        if not doctor:
            return False

        technician_name = order.get('technician_name', 'Не указан')
        work_type = order.get('work_type', 'Не указано')

        message = (
            f"📋 Ваша работа назначена технику!\n\n"
            f"👤 Пациент: {order.get('patient_name', 'Не указан')}\n"
            f"🔧 Техник: {technician_name}\n"
            f"🔨 Вид работы: {work_type}\n"
            f"📊 Количество: {order.get('quantity', 0)} шт\n"
        )

        if order.get('deadline'):
            message += f"📅 Срок выполнения: {order['deadline']}\n"

        try:
            if photo_id:
                await self.bot.send_photo(
                    chat_id=doctor['telegram_id'],
                    photo=photo_id,
                    caption=message
                )
            else:
                await self.bot.send_message(
                    chat_id=doctor['telegram_id'],
                    text=message
                )
            return True
        except Exception as e:
            print(f"Ошибка отправки уведомления врачу: {e}")
            return False

    async def send_to_dispatcher(self, telegram_id: int, order: dict):
        """Отправить уведомление диспетчеру"""
        technician_name = order.get('technician_name', 'Не указан')
        work_type = order.get('work_type', 'Не указано')
        quantity = order.get('quantity', 0)
        deadline = order.get('deadline', 'Не указан')

        message = (
            f"✅ Заказ создан!\n\n"
            f"👤 Пациент: {order.get('patient_name', 'Не указан')}\n"
            f"🔧 Техник: {technician_name}\n"
            f"🔨 Вид работы: {work_type}\n"
            f"📊 Количество: {quantity} шт\n"
        )

        if deadline:
            message += f"📅 Срок выполнения: {deadline}\n"

        sent_to = []
        if order.get('technician_id'):
            sent_to.append("технику")
        if order.get('doctor_id'):
            sent_to.append("врачу")

        if sent_to:
            message += f"\n📤 Уведомления отправлены: {', '.join(sent_to)}"

        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=message
            )
            return True
        except Exception as e:
            print(f"Ошибка отправки уведомления диспетчеру: {e}")
            return False

    async def send_reminder_to_technician(self, order: dict, reminder_message: str):
        """Отправить напоминание технику"""
        if not order.get('technician_id'):
            return False

        technicians = self.user_manager.get_users_by_role('technician')
        technician = None

        for tech in technicians:
            if tech['reference_id'] == order['technician_id']:
                technician = tech
                break

        if not technician:
            return False

        try:
            await self.bot.send_message(
                chat_id=technician['telegram_id'],
                text=reminder_message
            )
            return True
        except Exception as e:
            print(f"Ошибка отправки напоминания технику: {e}")
            return False

    async def send_reminder_to_dispatcher(self, telegram_id: int, order: dict, technician_name: str):
        """Отправить напоминание диспетчеру"""
        message = (
            f"⏰ НАПОМИНАНИЕ О СРОКЕ ВЫПОЛНЕНИЯ!\n\n"
            f"📋 Заказ №{order['id']}\n"
            f"👤 Пациент: {order.get('patient_name', 'Не указан')}\n"
            f"🔧 Техник: {technician_name}\n"
            f"🔨 Вид работы: {order.get('work_type', 'Не указано')}\n"
            f"📊 Количество: {order.get('quantity', 0)} шт\n"
            f"📅 Срок выполнения: {order.get('deadline', 'Не указан')}\n"
        )

        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=message
            )
            return True
        except Exception as e:
            print(f"Ошибка отправки напоминания диспетчеру: {e}")
            return False
