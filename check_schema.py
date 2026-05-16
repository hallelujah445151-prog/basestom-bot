import sqlite3

conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(orders)')
print('Orders table schema:')
for row in cursor.fetchall():
    print(row)

conn.close()
