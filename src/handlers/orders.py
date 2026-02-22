import os
import sys
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_manager import UserManager
from services.message_processor import MessageProcessor
from services.reference_manager import ReferenceManager
from services.notification_service import NotificationService
from database import get_connection
import sqlite3


WAITING_PHOTO, WAITING_TEXT = range(2)


async def new_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания нового заказа"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    if not user:
        await update.message.reply_text('❌ Сначала зарегистрируйтесь через команду /register')
        return ConversationHandler.END

    if user['role'] != 'dispatcher':
        await update.message.reply_text('❌ Только диспетчер может создавать заказы.')
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
        'Или "Сидоров металлокерамика 13шт на завтра"'
    )

    return WAITING_TEXT


async def text_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста с назначением"""
    text = update.message.text
    photo_id = context.user_data.get('photo_id')

    processor = MessageProcessor()
    ref_manager = ReferenceManager()

    processed_data = processor.normalize_message(text)

    if not processed_data:
        await update.message.reply_text('❌ Не удалось обработать сообщение. Попробуйте еще раз.')
        return ConversationHandler.END

    formatted_message = processor.format_message(processed_data)

    await update.message.reply_text(
        f'✅ Обработано:\n\n{formatted_message}\n\n'
        '📝 Подтверждаем создание заказа?'
    )

    context.user_data['order_data'] = processed_data
    context.user_data['order_message'] = formatted_message

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO orders (doctor_id, technician_id, patient_name, work_type, quantity, deadline, description, photo_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            processed_data.get('doctor_id'),
            processed_data.get('technician_id'),
            processed_data.get('patient_name'),
            processed_data.get('work_type'),
            processed_data.get('quantity'),
            processed_data.get('deadline'),
            text,
            photo_id
        ))

        order_id = cursor.lastrowid
        conn.commit()

        order_data = {
            'id': order_id,
            'doctor_id': processed_data.get('doctor_id'),
            'technician_id': processed_data.get('technician_id'),
            'doctor_name': processed_data.get('doctor_name'),
            'technician_name': processed_data.get('technician_name'),
            'patient_name': processed_data.get('patient_name'),
            'work_type': processed_data.get('work_type'),
            'quantity': processed_data.get('quantity'),
            'deadline': processed_data.get('deadline'),
            'description': text
        }

        notification_service = NotificationService(os.getenv('BOT_TOKEN'))

        await notification_service.send_to_technician(order_data, photo_id)
        await notification_service.send_to_doctor(order_data, photo_id)
        await notification_service.send_to_dispatcher(update.effective_user.id, order_data)

        await update.message.reply_text(
            f'🎉 Заказ №{order_id} создан!\n\n'
            f'{formatted_message}\n\n'
            '✅ Уведомления отправлены.'
        )

        return ConversationHandler.END

    except sqlite3.Error as e:
        await update.message.reply_text(f'❌ Ошибка создания заказа: {e}')
        return ConversationHandler.END
    finally:
        conn.close()


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена создания заказа"""
    await update.message.reply_text('❌ Создание заказа отменено.')
    return ConversationHandler.END


new_order_handler = ConversationHandler(
    entry_points=[],
    states={
        WAITING_PHOTO: [MessageHandler(filters.PHOTO, photo_received)],
        WAITING_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_received)]
    },
    fallbacks=[MessageHandler(filters.COMMAND, cancel_order)]
)
