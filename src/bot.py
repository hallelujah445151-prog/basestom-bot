import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from database import init_db
from services.message_processor import MessageProcessor
from handlers.registration import register_handler, register_start
from handlers.admin import admin_menu, admin_menu_handler, get_admin_handler, delete_user_start, delete_user_selected
from handlers.orders import new_order_start, new_order_handler
from handlers.reports import report_doctors, report_technicians, report_work_types, report_period_start, report_period_handler
from handlers.change_role import change_role_start, change_role_handler
from utils.reminder_background import run_background_task

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_manager = __import__('services.user_manager', fromlist=['UserManager']).UserManager
        user = user_manager.UserManager.get_user_by_telegram_id(update.effective_user.id)

        if user:
            welcome_text = f'👋 Привет, {user["name"]}!\n\n'
        else:
            welcome_text = '👋 Привет! Вы еще не зарегистрированы.\n\n'

        welcome_text += '''
📋 Доступные команды:
/register - Регистрация в системе
/neworder - Создать новый заказ
/admin - Админ-панель (для диспетчера)
/changerole - Сменить роль (для тестирования)
/report - Отчеты (для диспетчера)
/help - Справка
'''

        await update.message.reply_text(welcome_text)
    except Exception as e:
        print(f"Error in start command: {e}")
        try:
            await update.message.reply_text(f'Hello! Available commands: /start /help /register')
        except Exception as e2:
            print(f"Error sending error message: {e2}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = '''
📋 Доступные команды:

🔹 Общие:
/start - Начать работу
/register - Регистрация в системе
/changerole - Сменить роль (для тестирования)
/help - Эта справка

🔹 Для диспетчера:
/neworder - Создать новый заказ
/admin - Админ-панель управления пользователями
/delete_user - Удалить пользователя
/report_doctors - Отчет по врачам (все время)
/report_technicians - Отчет по техникам (все время)
/report_work_types - Отчет по видам работ (все время)
/report_period - Отчет за период

💡 Создание заказа:
Команда /neworder позволяет создать новый заказ.
Сначала отправьте фото заказ-наряда, затем текст с назначением.

💡 Отчеты:
Команды /report_* позволяют просматривать статистику по заказам.
Команда /report_period позволяет выбрать период для детального отчета.

💡 Тестирование ролей:
Команда /changerole позволяет сменить роль для тестирования.
Диспетчер: может создавать заказы, просматривать отчеты, управлять пользователями.
Техник: получает уведомления о заказах и напоминания.
Врач: получает уведомления о назначении заказов.
'''

    await update.message.reply_text(help_text)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Используйте команду /help для просмотра доступных команд.')


async def main_async():
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('admin', admin_menu))
    application.add_handler(CommandHandler('neworder', new_order_start))
    application.add_handler(CommandHandler('changerole', change_role_start))
    application.add_handler(CommandHandler('delete_user', delete_user_start))
    application.add_handler(CommandHandler('report_doctors', report_doctors))
    application.add_handler(CommandHandler('report_technicians', report_technicians))
    application.add_handler(CommandHandler('report_work_types', report_work_types))
    application.add_handler(CommandHandler('report_period', report_period_start))

    application.add_handler(register_handler)
    application.add_handler(get_admin_handler())
    application.add_handler(new_order_handler)
    application.add_handler(change_role_handler)
    application.add_handler(report_period_handler)
    application.add_handler(CallbackQueryHandler(admin_menu_handler, pattern='^admin_'))
    application.add_handler(CallbackQueryHandler(delete_user_selected, pattern='^delete_user_|^delete_cancel'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print('Bot started...')
    print('Reminder background task started...')

    await application.initialize()
    await application.start()

    background_task = asyncio.create_task(run_background_task(BOT_TOKEN))

    await application.updater.start_polling()

    while True:
        await asyncio.sleep(1)


def main():
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
