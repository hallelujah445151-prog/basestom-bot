from telegram import Bot, InputFile
import sys
import os
import difflib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_manager import UserManager


class NotificationService:
    """Сервис для отправки уведомлений"""

    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token)
        self.user_manager = UserManager()

    async def send_to_technician(self, order: dict, photo_id: str = None):
        """Отправить уведомление технику"""
        technician_name = order.get('technician_name')
        print(f"[DEBUG] send_to_technician: technician_name = '{technician_name}'")

        if not technician_name:
            print("[DEBUG] send_to_technician: technician_name is empty, returning False")
            return False

        technicians = self.user_manager.get_users_by_role('technician')
        print(f"[DEBUG] send_to_technician: Found {len(technicians)} technicians in database")

        technician = None

        for tech in technicians:
            print(f"[DEBUG] send_to_technician: Checking technician: '{tech['name']}'")
            if technician_name.lower() in tech['name'].lower() or tech['name'].lower() in technician_name.lower():
                technician = tech
                print(f"[DEBUG] send_to_technician: EXACT MATCH FOUND! technician = '{technician['name']}', telegram_id = {technician['telegram_id']}")
                break

        if not technician:
            print(f"[DEBUG] send_to_technician: No exact match, trying fuzzy matching...")
            technician_names = [tech['name'] for tech in technicians]
            matches = difflib.get_close_matches(technician_name, technician_names, n=1, cutoff=0.7)
            print(f"[DEBUG] send_to_technician: Fuzzy matches: {matches}")

            if matches:
                for tech in technicians:
                    if tech['name'] == matches[0]:
                        technician = tech
                        print(f"[DEBUG] send_to_technician: FUZZY MATCH FOUND! technician = '{technician['name']}', telegram_id = {technician['telegram_id']}")
                        break

        if not technician:
            print(f"[DEBUG] send_to_technician: NO MATCH FOUND for '{technician_name}'")
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
        doctor_name = order.get('doctor_name')
        print(f"[DEBUG] send_to_doctor: doctor_name = '{doctor_name}'")

        if not doctor_name:
            print("[DEBUG] send_to_doctor: doctor_name is empty, returning False")
            return False

        doctors = self.user_manager.get_users_by_role('doctor')
        print(f"[DEBUG] send_to_doctor: Found {len(doctors)} doctors in database")

        doctor = None

        for doc in doctors:
            print(f"[DEBUG] send_to_doctor: Checking doctor: '{doc['name']}'")
            if doctor_name.lower() in doc['name'].lower() or doc['name'].lower() in doctor_name.lower():
                doctor = doc
                print(f"[DEBUG] send_to_doctor: EXACT MATCH FOUND! doctor = '{doctor['name']}', telegram_id = {doctor['telegram_id']}")
                break

        if not doctor:
            print(f"[DEBUG] send_to_doctor: No exact match, trying fuzzy matching...")
            doctor_names = [doc['name'] for doc in doctors]
            matches = difflib.get_close_matches(doctor_name, doctor_names, n=1, cutoff=0.7)
            print(f"[DEBUG] send_to_doctor: Fuzzy matches: {matches}")

            if matches:
                for doc in doctors:
                    if doc['name'] == matches[0]:
                        doctor = doc
                        print(f"[DEBUG] send_to_doctor: FUZZY MATCH FOUND! doctor = '{doctor['name']}', telegram_id = {doctor['telegram_id']}")
                        break

        if not doctor:
            print(f"[DEBUG] send_to_doctor: NO MATCH FOUND for '{doctor_name}'")
            return False

        technician_name = order.get('technician_name', 'Не указан')
        work_type = order.get('work_type', 'Не указано')
        print(f"[DEBUG] send_to_doctor: Sending notification to doctor '{doctor['name']}'")

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
        not_sent = []

        if technician_name:
            if order.get('technician_id'):
                sent_to.append(f"технику {technician_name}")
            else:
                not_sent.append(f"технику {technician_name} (не найден в базе)")

        if order.get('doctor_name'):
            if order.get('doctor_id'):
                sent_to.append(f"врачу {order.get('doctor_name')}")
            else:
                not_sent.append(f"врачу {order.get('doctor_name')} (не найден в базе)")

        if sent_to:
            message += f"\n📤 Уведомления отправлены: {', '.join(sent_to)}"

        if not_sent:
            message += f"\n⚠️ Уведомления НЕ отправлены: {', '.join(not_sent)}"

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
        technician_name = order.get('technician_name')

        if not technician_name:
            return False

        technicians = self.user_manager.get_users_by_role('technician')

        for tech in technicians:
            if technician_name.lower() in tech['name'].lower() or tech['name'].lower() in technician_name.lower():
                technician = tech
                break
        else:
            technician = None

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
            f"👨‍⚕️ Врач: {order.get('doctor_name', 'Не указан')}\n"
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
