from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler, ConversationHandler
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_manager import UserManager
from services.report_service import ReportService

ENTERING_START_DATE, ENTERING_END_DATE = range(2)


async def report_period_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало формирования отчета за период"""
    print(f"[DEBUG] report_period_start called for user {update.effective_user.id}")
    
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)
    print(f"[DEBUG] User found: {user}")
    
    if not user:
        print("[DEBUG] No user found")
        await update.message.reply_text('❌ Сначала зарегистрируйтесь через команду /register')
        return ConversationHandler.END
    
    if not UserManager.is_user_admin(user):
        print(f"[DEBUG] User is NOT admin: {user['role']}, is_admin: {user.get('is_admin', False)}")
        await update.message.reply_text('❌ Только администратор может просматривать отчеты.')
        return ConversationHandler.END
    
    print("[DEBUG] User IS admin, requesting date")
    await update.message.reply_text(
        '📊 Формирование отчета за период\n\n'
        '📅 Введите начальную дату (ДД.ММ.ГГГГ):'
    )
    
    return ENTERING_START_DATE


async def report_period_start_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка начальной даты"""
    start_date = update.message.text
    print(f"[DEBUG] report_period_start_date called, received date: {start_date}")
    
    try:
        datetime.strptime(start_date, '%d.%m.%Y')
        print(f"[DEBUG] Date parsed successfully: {start_date}")
    except ValueError:
        print("[DEBUG] Invalid date format")
        await update.message.reply_text('❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ')
        return ENTERING_START_DATE
    
    context.user_data['report_start_date'] = start_date
    print(f"[DEBUG] Start date saved, transitioning to END_DATE state")

    await update.message.reply_text(
        f'✅ Начальная дата: {start_date}\n\n'
        '📅 Введите конечную дату (ДД.ММ.ГГГГ):'
    )
    
    return ENTERING_END_DATE


async def report_period_end_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка конечной даты и формирование отчета"""
    end_date = update.message.text
    print(f"[DEBUG] report_period_end_date called, received end date: {end_date}")
    
    try:
        datetime.strptime(end_date, '%d.%m.%Y')
        print(f"[DEBUG] End date parsed successfully: {end_date}")
    except ValueError:
        print("[DEBUG] Invalid date format")
        await update.message.reply_text('❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ')
        return ENTERING_END_DATE
    
    start_date = context.user_data.get('report_start_date')
    print(f"[DEBUG] Start date from context: {start_date}")
    
    if not start_date:
        print("[DEBUG] No start date in context")
        await update.message.reply_text('❌ Начальная дата не найдена. Начните заново через /report_period')
        return ConversationHandler.END
    
    period = f"{start_date} - {end_date}"
    print(f"[DEBUG] Period: {period}")

    report_service = ReportService()

    period_stats = report_service.get_period_statistics(start_date, end_date)
    doctor_stats = report_service.get_doctor_statistics(start_date, end_date)
    technician_stats = report_service.get_technician_statistics(start_date, end_date)
    work_type_stats = report_service.get_work_type_statistics(start_date, end_date)

    messages = [
        report_service.format_period_report(period_stats, period),
        report_service.format_doctor_report(doctor_stats, period),
        report_service.format_technician_report(technician_stats, period),
        report_service.format_work_type_report(work_type_stats, period)
    ]

    for message in messages:
        await update.message.reply_text(message)

    print("[DEBUG] Report sent, ending conversation")
    return ConversationHandler.END


async def report_period_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена формирования отчета"""
    print("[DEBUG] report_period_cancel called")
    await update.message.reply_text('❌ Формирование отчета отменено.')
    return ConversationHandler.END


report_period_handler = ConversationHandler(
    entry_points=[CommandHandler('report_period', report_period_start)],
    states={
        ENTERING_START_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_period_start_date)],
        ENTERING_END_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_period_end_date)],
    },
    fallbacks=[CommandHandler('cancel', report_period_cancel)],
    name='report_period_conversation',
    persistent=False,
    block=False
)


async def report_doctors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отчет по врачам за все время"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)
    
    if not user:
        await update.message.reply_text('❌ Сначала зарегистрируйтесь через команду /register')
        return
    
    if not UserManager.is_user_admin(user):
        await update.message.reply_text('❌ Только администратор может просматривать отчеты.')
        return
    
    report_service = ReportService()
    stats = report_service.get_doctor_statistics()
    message = report_service.format_doctor_report(stats)
    
    await update.message.reply_text(message)


async def report_technicians(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отчет по техникам за все время"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)
    
    if not user:
        await update.message.reply_text('❌ Сначала зарегистрируйтесь через команду /register')
        return
    
    if not UserManager.is_user_admin(user):
        await update.message.reply_text('❌ Только администратор может просматривать отчеты.')
        return
    
    report_service = ReportService()
    stats = report_service.get_technician_statistics()
    message = report_service.format_technician_report(stats)
    
    await update.message.reply_text(message)


async def report_work_types(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отчет по видам работ за все время"""
    user = UserManager.get_user_by_telegram_id(update.effective_user.id)
    
    if not user:
        await update.message.reply_text('❌ Сначала зарегистрируйтесь через команду /register')
        return
    
    if not UserManager.is_user_admin(user):
        await update.message.reply_text('❌ Только администратор может просматривать отчеты.')
        return
    
    report_service = ReportService()
    stats = report_service.get_work_type_statistics()
    message = report_service.format_work_type_report(stats)
    
    await update.message.reply_text(message)
