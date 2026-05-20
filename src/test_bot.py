import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler
from handlers.registration import register_handler
from handlers.admin import admin_menu_handler, get_admin_handler
from handlers.orders import new_order_handler
from handlers.reports import report_doctors, report_technicians, report_work_types, report_period_start, report_period_handler
from handlers.change_role import change_role_handler

from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def test_handlers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тест всех обработчиков"""
    print(f'[TEST] /test command received from user {update.effective_user.id}')
    await update.message.reply_text(
        '✅ Бот работает! Хендлеры загружены.\n\n'
        'Зарегистрированные обработчики:\n'
        '• /start - Запуск\n'
        '• /help - Справка\n'
        '• /register - Регистрация\n'
        '• /admin_secret endurance - Назначение админа\n'
        '• /neworder - Создание заказа\n'
        '• /admin - Админ-панель\n'
        '• /report_doctors - Отчет по врачам\n'
        '• /report_technicians - Отчет по техникам\n'
        '• /report_work_types - Отчет по видам работ\n'
        '• /report_period - Отчет за период\n\n'
        'Если вы не админ, используйте /admin_secret endurance'
    )

async def main_async():
    """Тестирование бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('test', test_handlers))
    application.add_handler(register_handler)
    application.add_handler(report_period_handler)

    print('Test bot started...')
    print('Use /test command to verify bot is working')
    print('Press Ctrl+C to stop')

    await application.initialize()
    await application.start()
    await application.updater.start_polling(timeout=120, drop_pending_updates=True)

    while True:
        import asyncio
        await asyncio.sleep(1)

def main():
    import asyncio
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
