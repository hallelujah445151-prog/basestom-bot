import sqlite3

conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

cursor.execute('SELECT id, deadline FROM orders WHERE deadline IS NOT NULL LIMIT 5')
results = cursor.fetchall()

print('Deadline format in database:')
for row in results:
    print(f"  Order #{row[0]}: deadline={repr(row[1])} (type: {type(row[1]).__name__})")

conn.close()
