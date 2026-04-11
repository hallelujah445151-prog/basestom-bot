# -*- coding: utf-8 -*-
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler, CallbackQueryHandler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_manager import UserManager
from services.message_processor import MessageProcessor
from services.notification_service import NotificationService
from database import get_connection
import sqlite3


WAITING_PHOTO, WAITING_TEXT, CLARIFYING_USER = range(3)


class OrderHandler:
    """Класс для обработки создания заказов с уточнением неоднозначных пользователей"""

    def __init__(self):
        pass

    def check_ambiguous_users(self, name: str, role: str) -> list:
        """Проверить наличие пользователей с одинаковой фамилией"""
        users = UserManager.get_users_by_role(role)

        if not users:
            return []

        name_parts = name.lower().split()
        ambiguous_users = []

        for user in users:
            user_name_lower = user['name'].lower()

            for name_part in name_parts:
                if name_part in user_name_lower:
                    ambiguous_users.append(user)
                    break

        # Убираем дубликаты
        seen = set()
        unique_users = []
        for user in ambiguous_users:
            user_id = user['telegram_id']
            if user_id not in seen:
                seen.add(user_id)
                unique_users.append(user)

        return unique_users

    async def handle_ambiguity(self, update: Update, context: ContextTypes.DEFAULT_TYPE, processed_data: dict, ambiguous_users: list, photo_id: str, role: str):
        """Обработка неоднозначности - показ списка для выбора"""
        keyboard = []
        for i, user in enumerate(ambiguous_users):
            short_name = user['name'][:20]
            callback_data = f"user_{user['telegram_id']}_{role}"
            keyboard.append([InlineKeyboardButton(short_name, callback_data=callback_data)])

        # Кнопка для уточнения через OpenRouter
        keyboard.append([InlineKeyboardButton("✍ Ввести уточнение", callback_data=f"clarify_{role}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        role_name = "техника" if role == "technician" else "врача"

        await update.message.reply_text(
            f"⚠️ Найдено несколько {role_name}ов с фамилией \"{processed_data.get(f'{role}_name')}\":\n"
            f"Выберите подходящего или введите уточнение:",
            reply_markup=reply_markup
        )

        context.user_data['order_data'] = processed_data
        context.user_data['photo_id'] = photo_id
        context.user_data[f'ambiguous_{role}s'] = ambiguous_users

        return CLARIFYING_USER

    async def user_selected_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора пользователя из списка"""
        query = update.callback_query
        await query.answer()

        callback_data = query.data

        if callback_data.startswith('user_'):
            parts = callback_data.split('_')
            telegram_id = int(parts[1])
            role = parts[2]

            selected_user = UserManager.get_user_by_telegram_id(telegram_id)

            if selected_user:
                print(f"[DEBUG] User selected: {selected_user}")

                role_key = f"selected_{role}"
                context.user_data[role_key] = selected_user

                # Продолжаем создание заказа
                await self.process_order_creation(update, context)

        elif callback_data.startswith('clarify_'):
            # Пользователь хочет ввести уточнение
            role = callback_data.split('_')[1]

            await update.message.reply_text(
                "📝 Введите уточнение к фамилии:\n\n"
                "Примеры:\n"
                "• \"А.А.\" для Морокова Александра Александровича\n"
                "• \"П.С.\" для Петрова Сергеевича\n"
                "💡 Уточнение должно содержать: фамилия + инициалы или отчество"
            )

            # Переходим в состояние ожидания уточнения
            role_key = f"waiting_clarification_{role}"
            context.user_data[role_key] = True

            return

        return

    async def process_clarification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текста с уточнением"""
        if not context.user_data.get(f"waiting_clarification_{context.user_data['role_key']}"):
            return

        clarification = update.message.text

        if not clarification or clarification.strip() == "":
            await update.message.reply_text("❌ Уточнение не должно быть пустым.")
            return

        role = context.user_data['role_key'].replace("waiting_clarification_", "")

        # Получаем сохраненные данные
        processed_data = context.user_data.get('order_data', {})
        photo_id = context.user_data.get('photo_id')

        if role == "technician":
            if processed_data.get('technician_name'):
                processed_data['technician_name'] = processed_data['technician_name'] + " + " + clarification
            else:
                processed_data['technician_name'] = clarification
        elif role == "doctor":
            if processed_data.get('doctor_name'):
                processed_data['doctor_name'] = processed_data['doctor_name'] + " " + clarification
            else:
                processed_data['doctor_name'] = clarification

        # Удаляем временное состояние ожидания
        del context.user_data[context.user_data['role_key']]

        # Продолжаем создание заказа с обновленным именем
        await self.process_order_creation(update, context)

    async def process_order_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Продолжение создания заказа после выбора пользователя"""
        processed_data = context.user_data.get('order_data', {})
        photo_id = context.user_data.get('photo_id')

        technician_id = None
        doctor_id = None

        if processed_data.get('technician_name'):
            technician = UserManager.find_user_by_name(processed_data['technician_name'], 'technician')
            if technician:
                technician_id = technician['id']
            else:
                await update.message.reply_text(f"⚠️ Техник \"{processed_data['technician_name']}\" не найден в системе.")
                return ConversationHandler.END

        if processed_data.get('doctor_name'):
            doctor = UserManager.find_user_by_name(processed_data['doctor_name'], 'doctor')
            if doctor:
                doctor_id = doctor['id']
            else:
                print(f"[DEBUG] Doctor NOT FOUND in database")

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO orders (doctor_id, technician_id, patient_name, work_type, quantity, deadline, description, photo_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doctor_id,
                technician_id,
                processed_data.get('patient_name'),
                processed_data.get('work_type'),
                processed_data.get('quantity') if processed_data.get('quantity') is not None else 0,
                processed_data.get('deadline'),
                processed_data.get('description'),
                photo_id
            ))

            order_id = cursor.lastrowid
            conn.commit()

            order_data = {
                'id': order_id,
                'doctor_id': doctor_id,
                'technician_id': technician_id,
                'doctor_name': processed_data.get('doctor_name'),
                'technician_name': processed_data.get('technician_name'),
                'patient_name': processed_data.get('patient_name'),
                'work_type': processed_data.get('work_type'),
                'quantity': processed_data.get('quantity'),
                'deadline': processed_data.get('deadline'),
                'description': processed_data.get('description'),
                'photo_id': photo_id
            }

            notification_service = NotificationService(os.getenv('BOT_TOKEN'))

            await notification_service.send_to_technician(order_data, photo_id)
            await notification_service.send_to_doctor(order_data, photo_id)
            await notification_service.send_to_dispatcher(update.effective_user.id, order_data)
            await notification_service.send_to_all_admins(order_data, photo_id)

            formatted_message = MessageProcessor().format_message(processed_data)

            await update.message.reply_text(
                f"🎉 Заказ №{order_id} создан!\n\n"
                f"{formatted_message}\n\n"
                "✅ Уведомления отправлены."
            )

            return ConversationHandler.END

        except sqlite3.Error as e:
            await update.message.reply_text(f"❌ Ошибка создания заказа: {e}")
            return ConversationHandler.END

        finally:
            conn.close()


async def new_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания нового заказа"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    if not user:
        await update.message.reply_text('❌ Сначала зарегистрируйтесь через команду /register')
        return ConversationHandler.END

    if not UserManager.is_user_admin(user):
        await update.message.reply_text('❌ Только администратор может создавать заказы.')
        return ConversationHandler.END

    await update.message.reply_text(
        '📸 Создание нового заказа\n\n'
        'Отправьте фото заказ-наряда:'
    )

    return WAITING_PHOTO


async def photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фото заказ-наряда"""
    photo = update.message.photo[-1]
    context.user_data['photo_id'] = photo.file_id

    await update.message.reply_text(
        '✅ Фото получено!\n\n'
        '📝 Теперь отправьте текст с назначением, например:\n'
        '"Мороков циркон на винте 7шт"\n\n'
        '💡 Важно: Техник должен быть зарегистрирован в боте!'
    )

    return WAITING_TEXT


async def text_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста с назначением"""
    text = update.message.text
    photo_id = context.user_data.get('photo_id')

    processor = MessageProcessor()

    processed_data = processor.normalize_message(text)
    print(f"[DEBUG] Processed data: {processed_data}")

    if not processed_data:
        await update.message.reply_text('❌ Не удалось обработать сообщение. Попробуйте еще раз.')
        return ConversationHandler.END

    formatted_message = processor.format_message(processed_data)

    await update.message.reply_text(
        f"✅ Обработано:\n\n{formatted_message}\n\n"
        '📝 Подтверждаем создание заказа?'
    )

    context.user_data['order_data'] = processed_data
    context.user_data['order_message'] = formatted_message

    technician_id = None
    doctor_id = None

    # Поиск техника с учетом логики дубликатов фамилий
    if processed_data.get('technician_name'):
        technician = UserManager.find_user_by_name(processed_data['technician_name'], 'technician')
        if technician:
            technician_id = technician['id']
        else:
            await update.message.reply_text(f"⚠️ Техник \"{processed_data['technician_name']}\" не найден в системе.")
            return ConversationHandler.END

    # Поиск врача с учетом логики дубликатов фамилий
    if processed_data.get('doctor_name'):
        doctor = UserManager.find_user_by_name(processed_data['doctor_name'], 'doctor')
        if doctor:
            doctor_id = doctor['id']
        else:
            await update.message.reply_text(f"⚠️ Врач \"{processed_data['doctor_name']}\" не найден в системе.")
            return ConversationHandler.END

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO orders (doctor_id, technician_id, patient_name, work_type, quantity, deadline, description, photo_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            doctor_id,
            technician_id,
            processed_data.get('patient_name'),
            processed_data.get('work_type'),
            processed_data.get('quantity') if processed_data.get('quantity') is not None else 0,
            processed_data.get('deadline'),
            text,
            photo_id
        ))

        order_id = cursor.lastrowid
        conn.commit()

        order_data = {
            'id': order_id,
            'doctor_id': doctor_id,
            'technician_id': technician_id,
            'doctor_name': processed_data.get('doctor_name'),
            'technician_name': processed_data.get('technician_name'),
            'patient_name': processed_data.get('patient_name'),
            'work_type': processed_data.get('work_type'),
            'quantity': processed_data.get('quantity') if processed_data.get('quantity') is not None else 0,
            'deadline': processed_data.get('deadline'),
            'description': text,
            'photo_id': photo_id
        }

        notification_service = NotificationService(os.getenv('BOT_TOKEN'))

        await notification_service.send_to_technician(order_data, photo_id)
        await notification_service.send_to_doctor(order_data, photo_id)
        await notification_service.send_to_dispatcher(update.effective_user.id, order_data)
        await notification_service.send_to_all_admins(order_data, photo_id)

        formatted_message = MessageProcessor().format_message(processed_data)

        await update.message.reply_text(
            f"🎉 Заказ №{order_id} создан!\n\n"
            f"{formatted_message}\n\n"
            "✅ Уведомления отправлены."
        )

        return ConversationHandler.END

    except sqlite3.Error as e:
        await update.message.reply_text(f"❌ Ошибка создания заказа: {e}")
        return ConversationHandler.END

    finally:
        conn.close()


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена создания заказа"""
    await update.message.reply_text('❌ Создание заказа отменено.')
    return ConversationHandler.END


# Создаем экземпляр класса для использования
order_handler = OrderHandler()

# ConversationHandler для создания заказов
new_order_handler = ConversationHandler(
    entry_points=[CommandHandler('neworder', new_order_start)],
    states={
        WAITING_PHOTO: [MessageHandler(filters.PHOTO, photo_received)],
        WAITING_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_received)],
        CLARIFYING_USER: [
            CallbackQueryHandler(order_handler.user_selected_callback, pattern='^user_'),
            CallbackQueryHandler(order_handler.user_selected_callback, pattern='^clarify_'),
            MessageHandler(filters.TEXT & ~filters.COMMAND, order_handler.process_clarification)
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel_order)]
)