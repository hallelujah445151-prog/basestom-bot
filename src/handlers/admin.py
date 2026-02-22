from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_manager import UserManager


SELECTING_USER_TYPE, ENTERING_NAME, ENTERING_TELEGRAM_ID = range(3)


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ-меню для диспетчера"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    if not user or user['role'] != 'dispatcher':
        await update.message.reply_text('❌ У вас нет прав для этой команды.')
        return

    keyboard = [
        [InlineKeyboardButton("📋 Список пользователей", callback_data="admin_users")],
        [InlineKeyboardButton("➕ Добавить пользователя", callback_data="admin_add_user")],
        [InlineKeyboardButton("🔗 Привязать к реестру", callback_data="admin_link_user")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('⚙️ Админ-панель', reply_markup=reply_markup)


async def admin_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список всех пользователей"""
    query = update.callback_query
    await query.answer()

    users = UserManager.get_all_users()

    if not users:
        await query.edit_message_text('📭 Пользователей пока нет.')
        return

    message = "📋 Список пользователей:\n\n"

    for user in users:
        status = "✅" if user['is_active'] else "❌"
        message += f"{status} {user['name']} ({user['role']})\n"
        message += f"   Telegram ID: {user['telegram_id']}\n"

        if user['reference_id']:
            message += f"   Привязан к ID: {user['reference_id']}\n"

        message += "\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(message, reply_markup=reply_markup)


async def admin_add_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления пользователя"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Техник", callback_data="add_role_technician")],
        [InlineKeyboardButton("Врач", callback_data="add_role_doctor")],
        [InlineKeyboardButton("Диспетчер", callback_data="add_role_dispatcher")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text('➕ Выберите роль нового пользователя:', reply_markup=reply_markup)

    return SELECTING_USER_TYPE


async def admin_add_user_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор роли при добавлении пользователя"""
    query = update.callback_query
    await query.answer()

    role = query.data.split('_')[2]
    context.user_data['add_role'] = role

    await query.edit_message_text(f'✅ Роль: {role}\n📝 Введите ФИО пользователя:')

    return ENTERING_NAME


async def admin_add_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод имени при добавлении пользователя"""
    name = update.message.text
    context.user_data['add_name'] = name

    await update.message.reply_text(
        f'✅ Имя: {name}\n'
        f'📱 Введите Telegram ID пользователя (или пропустите):'
    )

    return ENTERING_TELEGRAM_ID


async def admin_add_user_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод Telegram ID при добавлении пользователя"""
    role = context.user_data.get('add_role')
    name = context.user_data.get('add_name')

    telegram_id = None
    if update.message.text and update.message.text.isdigit():
        telegram_id = int(update.message.text)

    success = UserManager.register_user(
        telegram_id=telegram_id,
        name=name,
        role=role
    )

    if success:
        await update.message.reply_text(
            f'🎉 Пользователь добавлен!\n\n'
            f'👤 Имя: {name}\n'
            f'🔹 Роль: {role}\n'
            f'📱 Telegram ID: {telegram_id or "Не указан"}'
        )
    else:
        await update.message.reply_text('❌ Ошибка добавления пользователя.')

    return ConversationHandler.END


def get_admin_handler():
    """Получить обработчик админ-панели"""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_add_user_start, pattern='^admin_add_user$')],
        states={
            SELECTING_USER_TYPE: [CallbackQueryHandler(admin_add_user_role, pattern='^add_role_')],
            ENTERING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_user_name)],
            ENTERING_TELEGRAM_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_user_telegram)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, lambda u, c: ConversationHandler.END)]
    )


async def admin_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок админ-меню"""
    query = update.callback_query
    await query.answer()

    if query.data == 'admin_menu':
        await admin_menu(update, context)
    elif query.data == 'admin_users':
        await admin_users_list(update, context)
    elif query.data == 'admin_back':
        await query.edit_message_text('Вернулись в главное меню.')
