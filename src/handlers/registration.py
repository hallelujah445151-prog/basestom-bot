from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, CommandHandler
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_manager import UserManager


SELECTING_ROLE, ENTERING_NAME = range(2)


async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса регистрации"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    if user:
        await update.message.reply_text(
            f'Вы уже зарегистрированы как {user["name"]} ({user["role"]})'
        )
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Техник", callback_data="role_technician")],
        [InlineKeyboardButton("Врач", callback_data="role_doctor")],
        [InlineKeyboardButton("Диспетчер", callback_data="role_dispatcher")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        '📋 Выберите вашу роль:',
        reply_markup=reply_markup
    )

    return SELECTING_ROLE


async def role_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора роли"""
    query = update.callback_query
    await query.answer()

    role = query.data.split('_')[1]
    context.user_data['role'] = role

    await query.edit_message_text(
        f'✅ Вы выбрали роль: {role}\n'
        '📝 Введите ваше ФИО:'
    )

    return ENTERING_NAME


async def name_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка введенного имени"""
    name = update.message.text
    role = context.user_data.get('role')

    success = UserManager.register_user(
        telegram_id=update.effective_user.id,
        name=name,
        role=role
    )

    if success:
        await update.message.reply_text(
            f'🎉 Регистрация завершена!\n\n'
            f'👤 Имя: {name}\n'
            f'🔹 Роль: {role}\n\n'
            f'Используйте /help для просмотра доступных команд'
        )
    else:
        await update.message.reply_text(
            '❌ Ошибка регистрации. Возможно, вы уже зарегистрированы.'
        )

    return ConversationHandler.END


async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена регистрации"""
    await update.message.reply_text('Регистрация отменена.')
    return ConversationHandler.END


register_handler = ConversationHandler(
    entry_points=[CommandHandler('register', register_start)],
    states={
        SELECTING_ROLE: [CallbackQueryHandler(role_selected)],
        ENTERING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_entered)]
    },
    fallbacks=[MessageHandler(filters.COMMAND, cancel_registration)]
)
