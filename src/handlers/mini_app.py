from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes

# URL Mini App
MINI_APP_URL = "https://stomapp-miniapp-1.onrender.com"
LOCAL_MINI_APP_URL = "https://stomapp-miniapp-1.onrender.com"

async def open_mini_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Открытие Telegram Mini App"""
    web_app_url = LOCAL_MINI_APP_URL  # Для тестирования используйте локальный URL
    
    keyboard = [[InlineKeyboardButton(
        text="Открыть приложение",
        web_app=WebAppInfo(url=web_app_url)
    )]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Откройте мини-приложение для управления лабораторией!\n\n"
        "В приложении вы можете:\n"
        "• Просматривать свои заказы\n"
        "• Создавать новые заказы\n"
        "• Редактировать статусы\n"
        "• Использовать поиск и фильтры\n\n"
        "Приложение работает лучше в мобильной версии Telegram",
        reply_markup=reply_markup
    )

async def mini_app_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о Mini App"""
    await update.message.reply_text(
        "StomApp - Мини-приложение для управления лабораторией\n\n"
        "Возможности:\n"
        "• Просмотр всех заказов\n"
        "• Создание новых заказов (3 простых шага)\n"
        "• Поиск и фильтрация\n"
        "• Редактирование статусов\n"
        "• Статистика и отчеты\n\n"
        f"Ссылка: {LOCAL_MINI_APP_URL}\n\n"
        "Нажмите кнопку ниже чтобы открыть приложение:",
        reply_markup=InlineKeyboardMarkup([[
            [InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url=LOCAL_MINI_APP_URL))]
        ]])
    )