import sqlite3

conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

# Получаем имя техника Плюхин
cursor.execute("SELECT name FROM users WHERE id = 5")
result = cursor.fetchone()

print(f"Name in database (ID=5): {result[0]}")
print(f"Name we're searching for: Плюхин Владимир Александрович")
print(f"Are they equal? {result[0] == 'Плюхин Владимир Александрович'}")

# Проверяем точное совпадение с lower()
print(f"\nLowercase comparison:")
print(f"Database name (lower): {result[0].lower()}")
print(f"Search name (lower): {'Плюхин Владимир Александрович'.lower()}")
print(f"Are they equal (lower)? {result[0].lower() == 'плюхин владимир александрович'}")

# Проверяем, может ли быть проблема с лишними пробелами
print(f"\nChecking for extra spaces:")
print(f"Database name repr: {repr(result[0])}")
print(f"Search name repr: {repr('Плюхин Владимир Александрович')}")

conn.close()
