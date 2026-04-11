import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

ENTERING_TEXT, ENTERING_TEXT_2 = range(2)

async def test_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тест начала conversation"""
    print('[TEST] test_start called')
    await update.message.reply_text('Введите первое текстовое сообщение:')
    return ENTERING_TEXT

async def test_step_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовый шаг 1"""
    print('[TEST] test_step_1 called')
    text = update.message.text
    await update.message.reply_text(f'Вы ввели: {text}\n\nВведите второе сообщение:')
    return ENTERING_TEXT_2

async def test_step_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовый шаг 2"""
    print('[TEST] test_step_2 called')
    text = update.message.text
    await update.message.reply_text(f'Конец! Вы ввели: {text}')
    return ConversationHandler.END

test_handler = ConversationHandler(
    entry_points=[CommandHandler('test', test_start)],
    states={
        ENTERING_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, test_step_1)],
        ENTERING_TEXT_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, test_step_2)]
    },
    fallbacks=[]
)
