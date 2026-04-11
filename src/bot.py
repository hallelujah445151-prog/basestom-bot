import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import NetworkError, TimedOut

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import init_db
from services.message_processor import MessageProcessor
from handlers.registration import register_handler
from handlers.admin import admin_menu, admin_menu_handler, get_admin_handler
from handlers.orders import new_order_start, new_order_handler
from handlers.reports import report_doctors, report_technicians, report_work_types, report_period_handler
from handlers.change_role import change_role_start, change_role_handler
from utils.reminder_background import run_background_task

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        from services.user_manager import UserManager
        user_manager = UserManager
        user = user_manager.get_user_by_telegram_id(update.effective_user.id)

        if user:
            welcome_text = f'👋 Привет, {user["name"]}!\n\n'
        else:
            welcome_text = '👋 Привет! Вы еще не зарегистрированы.\n\n'

        welcome_text += '''📋 Доступные команды:

/start - Начать работу
/register - Регистрация в системе
/help - Справка

💡 Если вы администратор:
/neworder - Создать новый заказ
/admin - Админ-панель управления пользователями
/report_doctors - Отчет по врачам
/report_technicians - Отчет по техникам
/report_work_types - Отчет по видам работ
/report_period - Отчет за период

💡 Для назначения администратора:
/admin_secret СЕКРЕТНЫЙ_КОД
'''

        await update.message.reply_text(welcome_text)
    except Exception as e:
        print(f"Error in start command: {e}")
        try:
            await update.message.reply_text('Error! Please try /help command')
        except Exception as e2:
            print(f"Error sending error message: {e2}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = '''
📋 Доступные команды:

🔹 Общие:
/start - Начать работу
/register - Регистрация в системе
/help - Эта справка

🔹 Для администратора:
/neworder - Создать новый заказ
/admin - Админ-панель управления пользователями
/report_doctors - Отчет по врачам (все время)
/report_technicians - Отчет по техникам (все время)
/report_work_types - Отчет по видам работ (все время)
/report_period - Отчет за период

💡 Создание заказа:
Команда /neworder позволяет создать новый заказ.
Сначала отправьте фото заказ-наряда, затем текст с назначением.
Пример: "Мороков циркон на винте7шт"
💡 Техник должен быть зарегистрирован в боте!

💡 Отчеты:
Команды /report_* позволяют просматривать статистику по заказам.
Команда /report_period позволяет выбрать период для детального отчета.

💡 Регистрация:
Регистрация доступна для двух ролей: Техник и Врач.
Администратор назначается отдельно через секретную команду.

💡 Роли:
Техник: получает уведомления о заказах и напоминания.
Врач: получает уведомления о назначении заказов.
Администратор: создает заказы, просматривает отчеты, управляет ботом.
'''

    await update.message.reply_text(help_text)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Используйте команду /help для просмотра доступных команд.')


async def admin_secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Секретная команда для назначения администратора"""
    from services.user_manager import UserManager
    import os

    SECRET_CODE = os.getenv('ADMIN_SECRET_CODE', 'admin123')

    if not context.args or len(context.args) == 0:
        await update.message.reply_text('❌ Укажите секретный код. Пример: /admin_secret СЕКРЕТНЫЙ_КОД')
        return

    code = context.args[0]

    if code != SECRET_CODE:
        await update.message.reply_text('❌ Неверный секретный код.')
        return

    user = UserManager.get_user_by_telegram_id(update.effective_user.id)

    if not user:
        await update.message.reply_text('❌ Сначала зарегистрируйтесь через команду /register')
        return

    success = UserManager.set_admin(update.effective_user.id)

    if success:
        await update.message.reply_text(
            f'✅ {user["name"]}, вы назначены администратором!\n\n'
            'Теперь вы можете:\n'
            '• Создавать заказы (/neworder)\n'
            '• Просматривать отчеты (/report_*)\n'
            '• Управлять ботом (/admin)'
        )
    else:
        await update.message.reply_text('❌ Ошибка назначения администратора.')


async def main_async():
    init_db()

    # Create application once
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .pool_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('admin', admin_menu))
    application.add_handler(CommandHandler('changerole', change_role_start))
    application.add_handler(CommandHandler('report_doctors', report_doctors))
    application.add_handler(CommandHandler('report_technicians', report_technicians))
    application.add_handler(CommandHandler('report_work_types', report_work_types))
    application.add_handler(report_period_handler)
    application.add_handler(CommandHandler('admin_secret', admin_secret))
    application.add_handler(register_handler)
    for handler in get_admin_handler():
        application.add_handler(handler)
    application.add_handler(new_order_handler)
    application.add_handler(change_role_handler)

    logger.info('Bot started...')
    logger.info('Reminder background task enabled')

    # Try to connect to Telegram with retry logic
    retry_count = 0
    max_retries = 5

    while retry_count < max_retries:
        try:
            logger.info(f'Attempting to connect to Telegram (Attempt {retry_count + 1}/{max_retries})')
            await application.initialize()
            await application.start()
            logger.info('Successfully connected to Telegram!')
            break

        except TimedOut as e:
            logger.error(f'Timeout error: {e}')
            if retry_count < max_retries - 1:
                wait_time = min(30, 10 * (retry_count + 1))
                logger.warning(f'Retrying in {wait_time} seconds... (Attempt {retry_count + 2}/{max_retries})')
                logger.warning('Make sure VPN is enabled!')
                await asyncio.sleep(wait_time)
                retry_count += 1
            else:
                logger.error('Max retries reached. Giving up.')
                raise

        except NetworkError as e:
            logger.error(f'Network error: {e}')
            if retry_count < max_retries - 1:
                wait_time = min(30, 10 * (retry_count + 1))
                logger.warning(f'Retrying in {wait_time} seconds... (Attempt {retry_count + 2}/{max_retries})')
                logger.warning('Make sure VPN is enabled!')
                await asyncio.sleep(wait_time)
                retry_count += 1
            else:
                logger.error('Max retries reached. Giving up.')
                raise

    # Start polling (no retry for polling)
    try:
        await application.updater.start_polling(
            timeout=180,
            drop_pending_updates=True,
            allowed_updates=['message', 'callback_query']
        )
        logger.info('Polling started successfully!')
    except Exception as e:
        logger.error(f'Failed to start polling: {e}')
        raise

    # Start background task
    background_task = asyncio.create_task(run_background_task(BOT_TOKEN))

    # Keep bot running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info('Bot stopped by user')
        background_task.cancel()
        await application.stop()
        await application.shutdown()
        return


def main():
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
