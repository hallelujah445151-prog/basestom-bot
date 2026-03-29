from datetime import datetime, timedelta
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


def convert_date_format(date_str):
    """Конвертировать дату из ДД.ММ.ГГГГ в ГГГГ-ММ-ДД"""
    try:
        dt = datetime.strptime(date_str, '%d.%m.%Y')
        return dt.strftime('%Y-%m-%d')
    except:
        return None


class ReportService:
    """Сервис для сбора статистики и формирования отчетов"""

    @staticmethod
    def get_doctor_statistics(start_date=None, end_date=None):
        """Получить статистику по врачам"""
        conn = get_connection()
        cursor = conn.cursor()

        base_query = '''
            FROM orders o
            JOIN users u ON o.doctor_id = u.id
            WHERE o.status = 'in_progress'
        '''

        params = []
        where_clause = base_query

        if start_date:
            start_date_sql = convert_date_format(start_date)
            if start_date_sql:
                where_clause += ' AND DATE(o.created_at) >= ?'
                params.append(start_date_sql)

        if end_date:
            end_date_sql = convert_date_format(end_date)
            if end_date_sql:
                where_clause += ' AND DATE(o.created_at) <= ?'
                params.append(end_date_sql)

        query = f'''
            SELECT u.name, o.work_type, COUNT(o.id) as order_count
            {where_clause}
            GROUP BY u.id, o.work_type
            ORDER BY u.name, o.work_type
        '''

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        doc_data = {}
        for row in rows:
            name = row[0]
            work_type = row[1]
            order_count = row[2]

            if name not in doc_data:
                doc_data[name] = {
                    'name': name,
                    'work_types': []
                }

            doc_data[name]['work_types'].append({
                'work_type': work_type,
                'order_count': order_count
            })

        return list(doc_data.values())

    @staticmethod
    def get_technician_statistics(start_date=None, end_date=None):
        """Получить статистику по техникам"""
        conn = get_connection()
        cursor = conn.cursor()

        base_query = '''
            FROM orders o
            JOIN users u ON o.technician_id = u.id
            WHERE o.status = 'in_progress'
        '''

        params = []
        where_clause = base_query

        if start_date:
            start_date_sql = convert_date_format(start_date)
            if start_date_sql:
                where_clause += ' AND DATE(o.created_at) >= ?'
                params.append(start_date_sql)

        if end_date:
            end_date_sql = convert_date_format(end_date)
            if end_date_sql:
                where_clause += ' AND DATE(o.created_at) <= ?'
                params.append(end_date_sql)

        query = f'''
            SELECT u.name, o.work_type, COUNT(o.id) as order_count, SUM(o.quantity) as total_quantity
            {where_clause}
            GROUP BY u.id, o.work_type
            ORDER BY u.name, o.work_type
        '''

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        tech_data = {}
        for row in rows:
            name = row[0]
            work_type = row[1]
            order_count = row[2]
            total_quantity = row[3] or 0

            if name not in tech_data:
                tech_data[name] = {
                    'name': name,
                    'work_types': []
                }

            tech_data[name]['work_types'].append({
                'work_type': work_type,
                'order_count': order_count,
                'total_quantity': total_quantity
            })

        return list(tech_data.values())

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
            start_date_sql = convert_date_format(start_date)
            if start_date_sql:
                query += ' AND DATE(created_at) >= ?'
                params.append(start_date_sql)

        if end_date:
            end_date_sql = convert_date_format(end_date)
            if end_date_sql:
                query += ' AND DATE(created_at) <= ?'
                params.append(end_date_sql)

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

        start_date_sql = convert_date_format(start_date)
        end_date_sql = convert_date_format(end_date)

        if not start_date_sql or not end_date_sql:
            return {
                'total_orders': 0,
                'total_quantity': 0,
                'total_doctors': 0,
                'total_technicians': 0
            }

        cursor.execute('''
            SELECT COUNT(*), SUM(quantity), COUNT(DISTINCT doctor_id), COUNT(DISTINCT technician_id)
            FROM orders
            WHERE status = 'in_progress'
            AND DATE(created_at) >= ?
            AND DATE(created_at) <= ?
        ''', (start_date_sql, end_date_sql))

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

        total_orders = 0

        for doc in stats:
            doc_orders = sum(wt['order_count'] for wt in doc['work_types'])
            total_orders += doc_orders

            message += f"👨‍⚕️ {doc['name']}\n"

            if doc['work_types']:
                message += "   Виды работ:\n"
                for i, wt in enumerate(doc['work_types'], 1):
                    message += f"   {i}. {wt['work_type']} ({wt['order_count']} заказ)\n"
            else:
                message += "   ❌ Нет работ\n"

            message += "\n"

        message += f"📋 Всего заказов: {total_orders}\n"

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

        total_orders = 0
        total_quantity = 0

        for tech in stats:
            tech_orders = sum(wt['order_count'] for wt in tech['work_types'])
            tech_quantity = sum(wt['total_quantity'] for wt in tech['work_types'])
            total_orders += tech_orders
            total_quantity += tech_quantity

            message += f"👤 {tech['name']}\n"

            if tech['work_types']:
                message += "   Виды работ:\n"
                for i, wt in enumerate(tech['work_types'], 1):
                    message += f"   {i}. {wt['work_type']} ({wt['order_count']} заказ, {wt['total_quantity']} шт)\n"
            else:
                message += "   ❌ Нет работ\n"

            message += "\n"

        message += f"📋 Всего заказов: {total_orders}\n"
        message += f"📊 Всего единиц: {total_quantity}\n"

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
