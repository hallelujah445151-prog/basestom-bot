from datetime import datetime, timedelta
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class ReportService:
    """Сервис для сбора статистики и формирования отчетов"""

    @staticmethod
    def get_doctor_statistics(start_date=None, end_date=None):
        """Получить статистику по врачам"""
        conn = get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT u.name, COUNT(o.id) as order_count,
                   GROUP_CONCAT(o.work_type, ', ') as work_types
            FROM orders o
            JOIN users u ON o.doctor_id = u.id
            WHERE o.status = 'in_progress'
        '''

        params = []

        if start_date:
            query += ' AND DATE(o.created_at) >= DATE(?, "start of day")'
            params.append(start_date)

        if end_date:
            query += ' AND DATE(o.created_at) <= DATE(?, "start of day")'
            params.append(end_date)

        query += ' GROUP BY u.id ORDER BY order_count DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        stats = []
        for row in rows:
            stats.append({
                'name': row[0],
                'order_count': row[1],
                'work_types': row[2] or ''
            })

        return stats

    @staticmethod
    def get_technician_statistics(start_date=None, end_date=None):
        """Получить статистику по техникам"""
        conn = get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT u.name, COUNT(o.id) as order_count,
                   SUM(o.quantity) as total_quantity,
                   GROUP_CONCAT(o.work_type, ', ') as work_types
            FROM orders o
            JOIN users u ON o.technician_id = u.id
            WHERE o.status = 'in_progress'
        '''

        params = []

        if start_date:
            query += ' AND DATE(o.created_at) >= DATE(?, "start of day")'
            params.append(start_date)

        if end_date:
            query += ' AND DATE(o.created_at) <= DATE(?, "start of day")'
            params.append(end_date)

        query += ' GROUP BY u.id ORDER BY order_count DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        stats = []
        for row in rows:
            stats.append({
                'name': row[0],
                'order_count': row[1],
                'total_quantity': row[2] or 0,
                'work_types': row[3] or ''
            })

        return stats

    @staticmethod
    def get_work_type_statistics(start_date=None, end_date=None):
        """Получить статистику по видам работ"""
        conn = get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT work_type, COUNT(*) as order_count,
                   SUM(quantity) as total_quantity
            FROM orders
            WHERE status = 'in_progress'
        '''

        params = []

        if start_date:
            query += ' AND DATE(created_at) >= DATE(?, "start of day")'
            params.append(start_date)

        if end_date:
            query += ' AND DATE(created_at) <= DATE(?, "start of day")'
            params.append(end_date)

        query += ' GROUP BY work_type ORDER BY order_count DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        stats = []
        for row in rows:
            stats.append({
                'work_type': row[0],
                'order_count': row[1],
                'total_quantity': row[2] or 0
            })

        return stats

    @staticmethod
    def get_period_statistics(start_date, end_date):
        """Получить общую статистику за период"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*), SUM(quantity), COUNT(DISTINCT doctor_id), COUNT(DISTINCT technician_id)
            FROM orders
            WHERE status = 'in_progress'
            AND DATE(created_at) >= DATE(?, "start of day")
            AND DATE(created_at) <= DATE(?, "start of day")
        ''', (start_date, end_date))

        row = cursor.fetchone()
        conn.close()

        return {
            'total_orders': row[0] or 0,
            'total_quantity': row[1] or 0,
            'total_doctors': row[2] or 0,
            'total_technicians': row[3] or 0
        }

    @staticmethod
    def format_doctor_report(stats, period=None):
        """Форматировать отчет по врачам"""
        message = "📊 ОТЧЕТ ПО ВРАЧАМ\n\n"

        if period:
            message += f"📅 Период: {period}\n\n"

        if not stats:
            message += "❌ Нет данных за указанный период"
            return message

        total_orders = sum(s['order_count'] for s in stats)
        message += f"📋 Всего заказов: {total_orders}\n\n"

        for i, stat in enumerate(stats, 1):
            message += (
                f"{i}. {stat['name']}\n"
                f"   📦 Заказов: {stat['order_count']}\n"
                f"   🔨 Виды работ: {stat['work_types'][:50]}{'...' if len(stat['work_types']) > 50 else ''}\n\n"
            )

        return message

    @staticmethod
    def format_technician_report(stats, period=None):
        """Форматировать отчет по техникам"""
        message = "📊 ОТЧЕТ ПО ТЕХНИКАМ\n\n"

        if period:
            message += f"📅 Период: {period}\n\n"

        if not stats:
            message += "❌ Нет данных за указанный период"
            return message

        total_orders = sum(s['order_count'] for s in stats)
        total_quantity = sum(s['total_quantity'] for s in stats)

        message += f"📋 Всего заказов: {total_orders}\n"
        message += f"📊 Всего единиц: {total_quantity}\n\n"

        for i, stat in enumerate(stats, 1):
            message += (
                f"{i}. {stat['name']}\n"
                f"   📦 Заказов: {stat['order_count']}\n"
                f"   📊 Единиц: {stat['total_quantity']}\n"
                f"   🔨 Виды работ: {stat['work_types'][:50]}{'...' if len(stat['work_types']) > 50 else ''}\n\n"
            )

        return message

    @staticmethod
    def format_work_type_report(stats, period=None):
        """Форматировать отчет по видам работ"""
        message = "📊 ОТЧЕТ ПО ВИДАМ РАБОТ\n\n"

        if period:
            message += f"📅 Период: {period}\n\n"

        if not stats:
            message += "❌ Нет данных за указанный период"
            return message

        total_orders = sum(s['order_count'] for s in stats)
        total_quantity = sum(s['total_quantity'] for s in stats)

        message += f"📋 Всего заказов: {total_orders}\n"
        message += f"📊 Всего единиц: {total_quantity}\n\n"

        for i, stat in enumerate(stats, 1):
            message += (
                f"{i}. {stat['work_type']}\n"
                f"   📦 Заказов: {stat['order_count']}\n"
                f"   📊 Единиц: {stat['total_quantity']}\n\n"
            )

        return message

    @staticmethod
    def format_period_report(stats, period):
        """Форматировать общий отчет за период"""
        message = "📊 ОБЩИЙ ОТЧЕТ\n\n"
        message += f"📅 Период: {period}\n\n"

        message += (
            f"📋 Всего заказов: {stats['total_orders']}\n"
            f"📊 Всего единиц: {stats['total_quantity']}\n"
            f"👨‍⚕️ Врачей: {stats['total_doctors']}\n"
            f"🔧 Техников: {stats['total_technicians']}\n"
        )

        return message
