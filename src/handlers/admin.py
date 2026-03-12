from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_manager import UserManager


SELECTING_USER_TYPE, ENTERING_NAME, ENTERING_TELEGRAM_ID = range(3)
SELECTING_USER_FOR_DELETE = range(1)


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ-меню для диспетчера"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    if not user or user['role'] != 'dispatcher':
        await update.message.reply_text('❌ У вас нет прав для этой команды.')
        return

    keyboard = [
        [InlineKeyboardButton("📋 Список пользователей", callback_data='admin_users')],
        [InlineKeyboardButton("➕ Добавить пользователя", callback_data='admin_add_user')],
        [InlineKeyboardButton("🗑️ Удалить пользователя", callback_data='admin_delete_user')],
        [InlineKeyboardButton("🔙 Назад", callback_data='admin_back')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('⚙️ Админ-панель', reply_markup=reply_markup)


async def admin_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список всех пользователей"""
    query = update.callback_query
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    if not user or user['role'] != 'dispatcher':
        await query.edit_message_text('❌ У вас нет прав для этой команды.')
        return

    await query.answer()

    users = UserManager.get_all_users()

    if not users:
        await query.edit_message_text('📭 Пользователей пока нет.')
        return

    message = "📋 Список пользователей:\n\n"

    for i, user_data in enumerate(users, 1):
        status = "✅" if user_data['is_active'] else "❌"
        message += f"{i}. {status} {user_data['name']} ({user_data['role']})\n"
        message += f"   Telegram ID: {user_data['telegram_id']}\n"

        if user_data['reference_id']:
            message += f"   Привязан к ID: {user_data['reference_id']}\n"

        message += "\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='admin_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)


async def admin_add_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления пользователя"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    # Проверяем тип update (callback или message)
    if update.callback_query:
        # Если callback - вызываем для редактирования сообщения
        result = await _admin_add_user_start_callback(update, context, user)
    elif update.message:
        # Если message - обычная команда /admin_add_user
        result = await _admin_add_user_start_message(update, context, user)
    return result


async def _admin_add_user_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Начало добавления пользователя (callback версия)"""
    query = update.callback_query

    if not user or user['role'] != 'dispatcher':
        await query.edit_message_text('❌ У вас нет прав для этой команды.')
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Техник", callback_data='add_role_technician')],
        [InlineKeyboardButton("Врач", callback_data='add_role_doctor')],
        [InlineKeyboardButton("Диспетчер", callback_data='add_role_dispatcher')],
        [InlineKeyboardButton("❌ Отмена", callback_data='add_cancel')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text('➕ Добавить пользователя\n\nВыберите роль:', reply_markup=reply_markup)

    return SELECTING_USER_TYPE


async def _admin_add_user_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Начало добавления пользователя (message версия)"""
    if not user or user['role'] != 'dispatcher':
        await update.message.reply_text('❌ У вас нет прав для этой команды.')
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Техник", callback_data='add_role_technician')],
        [InlineKeyboardButton("Врач", callback_data='add_role_doctor')],
        [InlineKeyboardButton("Диспетчер", callback_data='add_role_dispatcher')],
        [InlineKeyboardButton("❌ Отмена", callback_data='add_cancel')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('➕ Добавить пользователя\n\nВыберите роль:', reply_markup=reply_markup)

    return SELECTING_USER_TYPE


async def delete_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало удаления пользователя"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    # Проверяем тип update (callback или message)
    if update.callback_query:
        # Если callback - вызываем для редактирования сообщения
        result = await _delete_user_start_callback(update, context, user)
    elif update.message:
        # Если message - обычная команда /delete_user
        result = await _delete_user_start_message(update, context, user)
    return result


async def _delete_user_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Начало удаления пользователя (callback версия)"""
    query = update.callback_query

    if not user or user['role'] != 'dispatcher':
        await query.edit_message_text('❌ У вас нет прав для этой команды.')
        return ConversationHandler.END

    users = UserManager.get_all_users()

    if not users:
        await query.edit_message_text('❌ Нет пользователей для удаления.')
        return ConversationHandler.END

    keyboard = []
    for user_data in users:
        keyboard.append([
            InlineKeyboardButton(f"🗑️ {user_data['name']} ({user_data['role']})", callback_data=f"delete_user_{user_data['id']}")
        ])

    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data='delete_cancel')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text('🗑️ Удаление пользователя\n\nВыберите пользователя для удаления:', reply_markup=reply_markup)

    return SELECTING_USER_FOR_DELETE


async def _delete_user_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Начало удаления пользователя (message версия)"""
    if not user or user['role'] != 'dispatcher':
        await update.message.reply_text('❌ У вас нет прав для этой команды.')
        return ConversationHandler.END

    users = UserManager.get_all_users()

    if not users:
        await update.message.reply_text('❌ Нет пользователей для удаления.')
        return ConversationHandler.END

    keyboard = []
    for user_data in users:
        keyboard.append([
            InlineKeyboardButton(f"🗑️ {user_data['name']} ({user_data['role']})", callback_data=f"delete_user_{user_data['id']}")
        ])

    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data='delete_cancel')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('🗑️ Удаление пользователя\n\nВыберите пользователя для удаления:', reply_markup=reply_markup)

    return SELECTING_USER_FOR_DELETE


async def _delete_user_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Начало удаления пользователя (callback версия)"""
    query = update.callback_query

    if not user or user['role'] != 'dispatcher':
        await query.edit_message_text('❌ У вас нет прав для этой команды.')
        return ConversationHandler.END

    users = UserManager.get_all_users()

    if not users:
        await query.edit_message_text('❌ Нет пользователей для удаления.')
        return ConversationHandler.END

    keyboard = []
    for user_data in users:
        keyboard.append([
            InlineKeyboardButton(f"🗑️ {user_data['name']} ({user_data['role']})", callback_data=f"delete_user_{user_data['id']}")
        ])

    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data='delete_cancel')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text('🗑️ Удаление пользователя\n\nВыберите пользователя для удаления:', reply_markup=reply_markup)

    return SELECTING_USER_FOR_DELETE


async def _delete_user_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    """Начало удаления пользователя (message версия)"""
    if not user or user['role'] != 'dispatcher':
        await update.message.reply_text('❌ У вас нет прав для этой команды.')
        return ConversationHandler.END

    users = UserManager.get_all_users()

    if not users:
        await update.message.reply_text('❌ Нет пользователей для удаления.')
        return ConversationHandler.END

    keyboard = []
    for user_data in users:
        keyboard.append([
            InlineKeyboardButton(f"🗑️ {user_data['name']} ({user_data['role']})", callback_data=f"delete_user_{user_data['id']}")
        ])

    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data='delete_cancel')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('🗑️ Удаление пользователя\n\nВыберите пользователя для удаления:', reply_markup=reply_markup)

    return SELECTING_USER_FOR_DELETE


async def delete_user_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора пользователя для удаления"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if 'delete_cancel' in data:
        await query.edit_message_text('❌ Удаление отменено.')
        return ConversationHandler.END

    user_id = int(data.split('_')[2])

    user_data = UserManager.get_user_by_id(user_id)

    if not user_data:
        await query.edit_message_text('❌ Пользователь не найден.')
        return ConversationHandler.END

    # Подтверждение удаления
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить удаление", callback_data=f"delete_confirm_{user_id}")],
        [InlineKeyboardButton("❌ Отмена", callback_data='delete_cancel')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f'🗑️ Удаление пользователя\n\n'
        f'Вы уверены, что хотите удалить пользователя?\n\n'
        f'👤 Пользователь: {user_data["name"]}\n'
        f'🔹 Роль: {user_data["role"]}\n'
        f'📅 Создан: {user_data["created_at"]}\n\n'
        'Это действие необратимо!',
        reply_markup=reply_markup
    )

    return SELECTING_USER_FOR_DELETE


async def delete_user_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение удаления пользователя"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if 'delete_cancel' in data:
        await query.edit_message_text('❌ Удаление отменено.')
        return ConversationHandler.END

    if 'delete_confirm' not in data:
        return

    user_id = int(data.split('_')[2])

    # Удаляем пользователя
    success = UserManager.delete_user(user_id)

    if success:
        await query.edit_message_text(f'✅ Пользователь ID {user_id} успешно удален!')
    else:
        await query.edit_message_text(f'❌ Ошибка при удалении пользователя ID {user_id}.')

    return ConversationHandler.END


async def admin_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок админ-меню"""
    query = update.callback_query
    await query.answer()

    if query.data == 'admin_users':
        await admin_users_list(update, context)
    elif query.data == 'admin_add_user':
        # Показываем инструкции вместо запуска диалога
        await query.edit_message_text(
            '➕ Добавить пользователя\n\n'
            'Для добавления пользователя используйте команду:\n'
            '/admin_add_user - выбрать роль и ввести данные'
        )
    elif query.data == 'admin_delete_user':
        # Показываем инструкции вместо запуска диалога
        await query.edit_message_text(
            '🗑️ Удаление пользователя\n\n'
            'Для удаления пользователя используйте команду:\n'
            '/delete_user - выбрать пользователя для удаления'
        )
    elif query.data == 'admin_back':
        await query.edit_message_text('🔙 Вернулись в главное меню.')


def get_admin_handler():
    """Получить обработчики админ-панели"""
    return [
        CallbackQueryHandler(admin_menu_handler, pattern='^admin_'),
        CallbackQueryHandler(admin_add_user_role, pattern='^add_role_'),
        CallbackQueryHandler(delete_user_selected, pattern='^delete_user_|^delete_cancel'),
        CallbackQueryHandler(delete_user_confirm, pattern='^delete_confirm_|^delete_cancel'),
        CommandHandler('admin_add_user', admin_add_user_start),
        CommandHandler('delete_user', delete_user_start),
        ConversationHandler(
            entry_points=[
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_user_telegram_id)
            ],
            states={
                ENTERING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_user_name)]
            },
            fallbacks=[MessageHandler(filters.COMMAND, lambda u, c: ConversationHandler.END)]
        )
    ]
