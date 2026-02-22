import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'orders.db')


def init_db():
    """Создание таблиц базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            reference_id INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            technician_id INTEGER,
            patient_name TEXT,
            work_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            deadline TEXT NOT NULL,
            description TEXT,
            photo_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'in_progress',
            FOREIGN KEY (doctor_id) REFERENCES users(id),
            FOREIGN KEY (technician_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            reminder_type TEXT NOT NULL,
            sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    ''')

    conn.commit()
    conn.close()


def get_connection():
    """Получение соединения с БД"""
    return sqlite3.connect(DB_PATH)
