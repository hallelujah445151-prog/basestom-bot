import sys
sys.path.append('src')

from services.message_processor import MessageProcessor

print("=" * 80)
print("Testing simple parser (without AI)")
print("=" * 80)

# Создаем процессор сообщений
processor = MessageProcessor()

# Тестовые сообщения для простого парсера
test_messages = [
    "Мороков циркон на винте 7шт пациент Иванов",
    "Сидоров металлокерамика 13шт на завтра пациент Петров",
    "Козлов виниры 5шт от Иванова 15.02.2026 пациент Сидоров"
]

for i, message in enumerate(test_messages, 1):
    print(f"\nTest {i}: '{message}'")
    print("-" * 80)

    result = processor.parse_message_simple(message)

    if result:
        # Форматируем сообщение
        formatted = processor.format_message(result)
        print(formatted)

        # Проверяем, используется ли нормализация
        print(f"\nWork type from parser: '{result.get('work_type')}'")
    else:
        print("ERROR: Failed to parse message")

print("\n" + "=" * 80)
print("Testing completed!")
print("=" * 80)
