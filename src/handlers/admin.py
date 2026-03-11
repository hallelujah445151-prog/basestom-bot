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
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    if not user or user['role'] != 'dispatcher':
        await update.message.reply_text('❌ У вас нет прав для этой команды.')
        return

    query = update.callback_query
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


async def admin_add_user_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор роли при добавлении пользователя"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if 'add_cancel' in data:
        await query.edit_message_text('❌ Добавление отменено.')
        return ConversationHandler.END

    role = data.split('_')[2]
    context.user_data['add_role'] = role

    await query.edit_message_text(f'✅ Выбрана роль: {role}\n📝 Введите ФИО пользователя:')

    return ENTERING_NAME


async def admin_add_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод имени пользователя"""
    name = update.message.text
    role = context.user_data.get('add_role')

    success = UserManager.register_user(
        telegram_id=None,
        name=name,
        role=role,
        reference_id=None
    )

    if success:
        await update.message.reply_text(f'✅ Пользователь добавлен!\n👤 Имя: {name}\n🔹 Роль: {role}')
    else:
        await update.message.reply_text('❌ Ошибка добавления пользователя.')

    return ConversationHandler.END


async def admin_add_user_telegram_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод Telegram ID пользователя"""
    telegram_id = update.message.text

    try:
        telegram_id = int(telegram_id)
    except ValueError:
        await update.message.reply_text('❌ Неверный формат Telegram ID. Введите число.')
        return

    role = context.user_data.get('add_role')

    success = UserManager.register_user(
        telegram_id=telegram_id,
        name=context.user_data.get('add_name'),
        role=role,
        reference_id=None
    )

    if success:
        await update.message.reply_text(f'✅ Пользователь добавлен!\n👤 Имя: {context.user_data.get("add_name")}\n🔹 Роль: {role}\n📱 Telegram ID: {telegram_id}')
    else:
        await update.message.reply_text('❌ Ошибка добавления пользователя.')

    return ConversationHandler.END


async def delete_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало удаления пользователя"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

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
            InlineKeyboardButton(f"🗑️ {user_data['name']} ({user_data['role']})", callback_data=f"delete_user_{user_data['id']}"),
            InlineKeyboardButton(f"❌ Отмена", callback_data='delete_cancel')
        ])

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

    if query.data == 'admin_menu':
        await admin_menu(update, context)
    elif query.data == 'admin_users':
        await admin_users_list(update, context)
    elif query.data == 'admin_delete_user':
        await delete_user_start(update, context)
    elif query.data == 'admin_back':
        await query.edit_message_text('🔙 Вернулись в главное меню.')


def get_admin_handler():
    """Получить обработчики админ-панели"""
    return [
        ConversationHandler(
            entry_points=[CallbackQueryHandler(admin_add_user_start, pattern='^admin_add_user$')],
            states={
                SELECTING_USER_TYPE: [CallbackQueryHandler(admin_add_user_role, pattern='^add_role_')],
                ENTERING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_user_name)],
                ENTERING_TELEGRAM_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_user_telegram_id)]
            },
            fallbacks=[MessageHandler(filters.COMMAND, lambda u, c: ConversationHandler.END)]
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(delete_user_start, pattern='^admin_delete_user$')],
            states={
                SELECTING_USER_FOR_DELETE: [CallbackQueryHandler(delete_user_selected, pattern='^delete_user_|^delete_cancel')]
            },
            fallbacks=[MessageHandler(filters.COMMAND, lambda u, c: ConversationHandler.END)]
        )
    ]
