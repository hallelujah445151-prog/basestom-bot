import os
import sys
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_manager import UserManager
from services.message_processor import MessageProcessor
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
        'Или "Сидоров металлокерамика 13шт на завтра"\n\n'
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
        f'✅ Обработано:\n\n{formatted_message}\n\n'
        '📝 Подтверждаем создание заказа?'
    )

    context.user_data['order_data'] = processed_data
    context.user_data['order_message'] = formatted_message

    technician_id = None
    doctor_id = None

    if processed_data.get('technician_name'):
        technician = UserManager.find_user_by_name(processed_data['technician_name'], 'technician')
        if technician:
            technician_id = technician['id']
        else:
            await update.message.reply_text(f'⚠️ Техник "{processed_data["technician_name"]}" не найден в системе.')
            return ConversationHandler.END

    if processed_data.get('doctor_name'):
        print(f"[DEBUG] Processing doctor: '{processed_data['doctor_name']}'")
        doctor = UserManager.find_user_by_name(processed_data['doctor_name'], 'doctor')
        if doctor:
            doctor_id = doctor['id']
            print(f"[DEBUG] Doctor FOUND: {doctor}")
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
            processed_data.get('quantity'),
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
            'quantity': processed_data.get('quantity'),
            'deadline': processed_data.get('deadline'),
            'description': text,
            'photo_id': photo_id
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
    entry_points=[CommandHandler('neworder', new_order_start)],
    states={
        WAITING_PHOTO: [MessageHandler(filters.PHOTO, photo_received)],
        WAITING_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_received)]
    },
    fallbacks=[MessageHandler(filters.COMMAND, cancel_order)]
)
