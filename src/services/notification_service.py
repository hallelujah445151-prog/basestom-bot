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
        technician_name_lower = technician_name.lower().strip()

        for tech in technicians:
            tech_name_lower = tech['name'].lower().strip()
            print(f"[DEBUG] send_to_technician: Checking exact match: '{tech['name']}' == '{technician_name}'")

            if technician_name_lower == tech_name_lower:
                technician = tech
                print(f"[DEBUG] send_to_technician: EXACT MATCH FOUND! technician = '{technician['name']}', telegram_id = {technician['telegram_id']}")
                break

        if not technician:
            print(f"[DEBUG] send_to_technician: No exact match, checking for duplicate surnames...")

            # Проверяем, есть ли дубликаты фамилии ДЛЯ КОНКРЕТНОГО ТЕХНИКА
            input_surname = technician_name.split()[0].lower() if technician_name.split() else technician_name.lower()
            print(f"[DEBUG] send_to_technician: Input surname: '{input_surname}'")

            surnames = []
            for tech in technicians:
                surname = tech['name'].split()[0] if tech['name'].split() else tech['name']
                surnames.append(surname.lower())

            from collections import Counter
            surname_counts = Counter(surnames)
            
            # Проверяем, есть ли дубликаты ТОЛЬКО для искомой фамилии
            has_duplicate_surname = surname_counts.get(input_surname, 0) > 1
            print(f"[DEBUG] send_to_technician: Surname '{input_surname}' count: {surname_counts.get(input_surname, 0)}")
            print(f"[DEBUG] send_to_technician: Has duplicate for '{input_surname}': {has_duplicate_surname}")

            # Логика: Если есть дубликаты ЭТОЙ фамилии → полное имя или сокращенное имя (Мороков А.А.)
            if has_duplicate_surname:
                print(f"[DEBUG] send_to_technician: Duplicate surname '{input_surname}' detected - using FULL NAME or ABBREVIATED (e.g., 'Мороков А.А.')")
                
                # Проверяем, является ли имя сокращенным (например, "Мороков А.А." или "Иванов И.И.")
                name_parts = technician_name.split()
                is_abbreviated = len(name_parts) == 2 and len(name_parts[1]) >= 2 and name_parts[1][-1] == '.'
                
                if is_abbreviated:
                    # Парсим фамилию и инициалы
                    surname_input = name_parts[0].lower()
                    initials_input = name_parts[1].lower()
                    print(f"[DEBUG] send_to_technician: Detected abbreviated name: surname='{surname_input}', initials='{initials_input}'")
                    
                    # Ищем пользователя с такой фамилией и инициалами
                    for tech in technicians:
                        user_name = tech['name']
                        user_parts = user_name.split()
                        
                        if len(user_parts) >= 2:
                            user_surname = user_parts[0].lower()
                            
                            # Формируем инициалы из полного имени (например, "Александр Александрович" → "А.А.")
                            user_initials = ''
                            if len(user_parts) >= 2:
                                user_initials = user_parts[1][0].lower() + '.'
                            if len(user_parts) >= 3:
                                user_initials += user_parts[2][0].lower() + '.'
                            
                            print(f"[DEBUG] send_to_technician: Checking: user_surname='{user_surname}', user_initials='{user_initials}'")
                            
                            if surname_input == user_surname and initials_input == user_initials:
                                technician = tech
                                print(f"[DEBUG] send_to_technician: ABBREVIATED MATCH FOUND! technician = '{technician['name']}', telegram_id = {technician['telegram_id']}")
                                break
                
                print(f"[DEBUG] send_to_technician: NO MATCH FOUND for '{technician_name}'")
                print(f"[DEBUG] send_to_technician: Recommendation: Use full name (e.g., 'Мороков Александр Александрович' or 'Мороков А.А.')")
                return False

            # Если фамилии уникальны → можно и фамилия, и полное имя
            print(f"[DEBUG] send_to_technician: Unique surnames - can search by surname OR full name")
            print(f"[DEBUG] send_to_technician: Trying fuzzy matching with lenient cutoff (0.6)...")

            # Создаем словарь фамилия -> список техников с этой фамилией
            surname_to_techs = {}
            for tech in technicians:
                surname = tech['name'].split()[0] if tech['name'].split() else tech['name']
                if surname not in surname_to_techs:
                    surname_to_techs[surname] = []
                surname_to_techs[surname].append(tech)

            # Сравниваем поисковую строку с фамилиями (не с полными именами)
            surnames = list(surname_to_techs.keys())
            matches = difflib.get_close_matches(technician_name, surnames, n=1, cutoff=0.6)
            print(f"[DEBUG] send_to_technician: Fuzzy matches (cutoff=0.6): {matches}")

            if matches:
                matched_surname = matches[0]
                technician = surname_to_techs[matched_surname][0]
                print(f"[DEBUG] send_to_technician: FUZZY MATCH FOUND! surname='{matched_surname}', technician = '{technician['name']}', telegram_id = {technician['telegram_id']}")

            if not technician:
                print(f"[DEBUG] send_to_technician: NO MATCH FOUND for '{technician_name}'")
                print(f"[DEBUG] send_to_technician: Recommendation: Check the name spelling or use full name")
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
        doctor_name_lower = doctor_name.lower().strip()

        for doc in doctors:
            doc_name_lower = doc['name'].lower().strip()
            print(f"[DEBUG] send_to_doctor: Checking exact match: '{doc['name']}' == '{doctor_name}'")

            if doctor_name_lower == doc_name_lower:
                doctor = doc
                print(f"[DEBUG] send_to_doctor: EXACT MATCH FOUND! doctor = '{doctor['name']}', telegram_id = {doctor['telegram_id']}")
                break

        if not doctor:
            print(f"[DEBUG] send_to_doctor: No exact match, checking for duplicate surnames...")

            # Проверяем, есть ли дубликаты фамилии ДЛЯ КОНКРЕТНОГО ВРАЧА
            input_surname = doctor_name.split()[0].lower() if doctor_name.split() else doctor_name.lower()
            print(f"[DEBUG] send_to_doctor: Input surname: '{input_surname}'")

            surnames = []
            for doc in doctors:
                surname = doc['name'].split()[0] if doc['name'].split() else doc['name']
                surnames.append(surname.lower())

            from collections import Counter
            surname_counts = Counter(surnames)
            
            # Проверяем, есть ли дубликаты ТОЛЬКО для искомой фамилии
            has_duplicate_surname = surname_counts.get(input_surname, 0) > 1
            print(f"[DEBUG] send_to_doctor: Surname '{input_surname}' count: {surname_counts.get(input_surname, 0)}")
            print(f"[DEBUG] send_to_doctor: Has duplicate for '{input_surname}': {has_duplicate_surname}")

            # Логика: Если есть дубликаты ЭТОЙ фамилии → полное имя или сокращенное имя (Мороков А.А.)
            if has_duplicate_surname:
                print(f"[DEBUG] send_to_doctor: Duplicate surname '{input_surname}' detected - using FULL NAME or ABBREVIATED (e.g., 'Мороков А.А.')")
                
                # Проверяем, является ли имя сокращенным (например, "Мороков А.А." или "Иванов И.И.")
                name_parts = doctor_name.split()
                is_abbreviated = len(name_parts) == 2 and len(name_parts[1]) >= 2 and name_parts[1][-1] == '.'
                
                if is_abbreviated:
                    # Парсим фамилию и инициалы
                    surname_input = name_parts[0].lower()
                    initials_input = name_parts[1].lower()
                    print(f"[DEBUG] send_to_doctor: Detected abbreviated name: surname='{surname_input}', initials='{initials_input}'")
                    
                    # Ищем пользователя с такой фамилией и инициалами
                    for doc in doctors:
                        user_name = doc['name']
                        user_parts = user_name.split()
                        
                        if len(user_parts) >= 2:
                            user_surname = user_parts[0].lower()
                            
                            # Формируем инициалы из полного имени (например, "Александр Александрович" → "А.А.")
                            user_initials = ''
                            if len(user_parts) >= 2:
                                user_initials = user_parts[1][0].lower() + '.'
                            if len(user_parts) >= 3:
                                user_initials += user_parts[2][0].lower() + '.'
                            
                            print(f"[DEBUG] send_to_doctor: Checking: user_surname='{user_surname}', user_initials='{user_initials}'")
                            
                            if surname_input == user_surname and initials_input == user_initials:
                                doctor = doc
                                print(f"[DEBUG] send_to_doctor: ABBREVIATED MATCH FOUND! doctor = '{doctor['name']}', telegram_id = {doctor['telegram_id']}")
                                break
                
                print(f"[DEBUG] send_to_doctor: NO MATCH FOUND for '{doctor_name}'")
                print(f"[DEBUG] send_to_doctor: Recommendation: Use full name (e.g., 'Мороков Александр Александрович' or 'Мороков А.А.')")
                return False

            # Если фамилии уникальны → можно и фамилия, и полное имя
            print(f"[DEBUG] send_to_doctor: Unique surnames - can search by surname OR full name")
            print(f"[DEBUG] send_to_doctor: Trying fuzzy matching with lenient cutoff (0.6)...")

            # Создаем словарь фамилия -> список врачей с этой фамилией
            surname_to_docs = {}
            for doc in doctors:
                surname = doc['name'].split()[0] if doc['name'].split() else doc['name']
                if surname not in surname_to_docs:
                    surname_to_docs[surname] = []
                surname_to_docs[surname].append(doc)

            # Сравниваем поисковую строку с фамилиями (не с полными именами)
            surnames = list(surname_to_docs.keys())
            matches = difflib.get_close_matches(doctor_name, surnames, n=1, cutoff=0.6)
            print(f"[DEBUG] send_to_doctor: Fuzzy matches (cutoff=0.6): {matches}")

            if matches:
                matched_surname = matches[0]
                doctor = surname_to_docs[matched_surname][0]
                print(f"[DEBUG] send_to_doctor: FUZZY MATCH FOUND! surname='{matched_surname}', doctor = '{doctor['name']}', telegram_id = {doctor['telegram_id']}")

            if not doctor:
                print(f"[DEBUG] send_to_doctor: NO MATCH FOUND for '{doctor_name}'")
                print(f"[DEBUG] send_to_doctor: Recommendation: Check the name spelling or use full name")
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

    async def send_to_all_admins(self, order: dict, photo_id: str = None):
        """Отправить уведомление всем администраторам"""
        admins = self.user_manager.get_all_admins()
        print(f"[DEBUG] send_to_all_admins: Found {len(admins)} admins")

        if not admins:
            print("[DEBUG] send_to_all_admins: No admins found")
            return False

        message = (
            f"🔔 Новый заказ в системе!\n\n"
            f"🆔 Заказ №{order['id']}\n"
            f"👤 Пациент: {order.get('patient_name', 'Не указан')}\n"
            f"🔧 Техник: {order.get('technician_name', 'Не указан')}\n"
            f"👨‍⚕️ Врач: {order.get('doctor_name', 'Не указан')}\n"
            f"🔨 Вид работы: {order.get('work_type', 'Не указано')}\n"
            f"📊 Количество: {order.get('quantity', 0)} шт\n"
        )

        if order.get('deadline'):
            message += f"📅 Срок выполнения: {order['deadline']}\n"

        success_count = 0
        for admin in admins:
            try:
                if photo_id:
                    await self.bot.send_photo(
                        chat_id=admin['telegram_id'],
                        photo=photo_id,
                        caption=message
                    )
                else:
                    await self.bot.send_message(
                        chat_id=admin['telegram_id'],
                        text=message
                    )
                success_count += 1
                print(f"[DEBUG] send_to_all_admins: Sent to admin '{admin['name']}' (id: {admin['telegram_id']})")
            except Exception as e:
                print(f"[DEBUG] send_to_all_admins: Failed to send to admin '{admin['name']}' (id: {admin['telegram_id']}): {e}")

        print(f"[DEBUG] send_to_all_admins: Successfully sent to {success_count}/{len(admins)} admins")
        return success_count > 0

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
