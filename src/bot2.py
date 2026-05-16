# -*- coding: utf-8 -*-
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import NetworkError, TimedOut

# Добавляем импорт для Telegram Mini App
try:
    from handlers.mini_app import open_mini_app, mini_app_info
except:
    # Если файл не существует или есть ошибка - создам базовый handler
    pass

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
            welcome_text = f'Привет, {user["name"]}!\n\n'
        else:
            welcome_text = 'Привет! Вы еще не зарегистрированы.\n\n'

        welcome_text += '''
📋 Доступные команды:

/start - Начать работу
/register - Регистрация в системе
/help - Справка
/app - Открыть мини-приложение
/miniapp - Быстрый доступ к приложению

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
        logger.error(f"Error in start command: {e}")
        try:
            await update.message.reply_text("Произошла ошибка. Попробуйте /help")
        except:
            pass


async def help_command(update: Update, context: Enum):
    await update.message.reply_text("""
📋 Доступные команды:

🔹 Общие:
/start - Начать работу
/register - Регистрация в системе
/help - Эта справка
/app - Открыть мини-приложение
/miniapp - Быстрый доступ к приложению

🔹 Для администратора:
/neworder - Создать новый заказ
/admin - Админ-панель управления пользователями
/report_doctors - Отчет по врачам
/report_technicians - Отчет по техникам
/report_work_types - Отчет по видам работ
/report_period - Отчет за период

💡 Создание заказа:
Команда /neworder позволяет создать новый заказ.
Сначала отправьте фото заказ-наряда, затем текст с назначением.
Пример: "Мороков циркон на винте7шт"
💡 Техник должен быть зарегистрирован в боте!

💡 Мини-приложение (StomApp):
📱 Современное веб-приложение для управления лабораторией

🎯 Возможности:
• Просмотр всех заказов
• Создание новых заказов (3 простых шага)
• Поиск и фильтрация
• Редактирование статусов
• Статистика и отчеты
• Работает в Telegram без установки

💡 Администратор назначается отдельно через секретную команду.
''')