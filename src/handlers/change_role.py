from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_manager import UserManager
from database import get_connection
import sqlite3


async def change_role_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало смены роли"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    if not user:
        if update.callback_query:
            await update.callback_query.edit_message_text('❌ Сначала зарегистрируйтесь через команду /register')
        else:
            await update.message.reply_text('❌ Сначала зарегистрируйтесь через команду /register')
        return

    current_role = user['role']
    current_name = user['name']

    keyboard = [
        [InlineKeyboardButton("Диспетчер (Dispatcher)", callback_data=f"role_dispatcher_{user['id']}")],
        [InlineKeyboardButton("Техник (Technician)", callback_data=f"role_technician_{user['id']}")],
        [InlineKeyboardButton("Врач (Doctor)", callback_data=f"role_doctor_{user['id']}")],
        [InlineKeyboardButton("❌ Отмена", callback_data=f"role_cancel_{user['id']}")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            f'📋 Смена роли\n\n'
            f'Текущая роль: {current_role}\n'
            f'Имя: {current_name}\n\n'
            f'Выберите новую роль:',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            f'📋 Смена роли\n\n'
            f'Текущая роль: {current_role}\n'
            f'Имя: {current_name}\n\n'
            f'Выберите новую роль:',
            reply_markup=reply_markup
        )


async def role_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора роли"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if 'role_cancel' in data:
        await query.edit_message_text('❌ Смена роли отменена.')
        return

    # Извлекаем user_id из callback_data
    parts = data.split('_')
    role = parts[1]
    user_id = int(parts[2])

    # Сопоставление ролей с реестрами
    role_mapping = {
        'dispatcher': 'dispatcher',
        'technician': 'technician',
        'doctor': 'doctor'
    }

    role_name = {
        'dispatcher': 'Диспетчер',
        'technician': 'Техник',
        'doctor': 'Врач'
    }[role]

    # Обновляем роль в users
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('UPDATE users SET role = ? WHERE id = ?', (role, user_id))
    conn.commit()
    conn.close()

    # Возвращаем обновленного пользователя
    capabilities = []
    if role == 'dispatcher':
        capabilities.append('📝 Создавать заказы и просматривать отчеты')
    if role == 'technician':
        capabilities.append('🔧 Получать уведомления о заказах')
    if role == 'doctor':
        capabilities.append('📋 Получать уведомления о назначении')

    capabilities_text = '\n'.join(capabilities) if capabilities else ''

    await query.edit_message_text(
        f'✅ Роль изменена на: {role_name}\n\n'
        f'💡 Новые возможности:\n{capabilities_text}'
    )


change_role_handler = CallbackQueryHandler(
    role_selected,
    pattern='^role_(dispatcher|technician|doctor|cancel)_'
)
