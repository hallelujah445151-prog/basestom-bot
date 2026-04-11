import sys
import codecs
sys.path.append('src')

# Устанавливаем UTF-8 кодировку для stdout (для Windows)
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from services.message_processor import MessageProcessor

print("=" * 80)
print("FINAL TEST - Bot Response Simulation")
print("=" * 80)

# Создаем процессор сообщений
processor = MessageProcessor()

# Тестовые сообщения для бота
test_messages = [
    "Мороков циркон на винте 7шт пациент Иванов",
    "Сидоров металлокерамика 13шт на завтра пациент Петров",
    "Козлов виниры 5шт от Иванова 15.02.2026 пациент Сидоров",
    "Плюхин металлокерамика 2 шт на 02.04.2026 врач Гаспарянидзе пациент Анохин"
]

for i, message in enumerate(test_messages, 1):
    print(f"\n{'=' * 80}")
    print(f"User message: {message}")
    print(f"{'=' * 80}")

    # Обрабатываем сообщение через ИИ
    processed_data = processor.normalize_message(message)

    if processed_data:
        # Форматируем сообщение для пользователя
        formatted = processor.format_message(processed_data)

        print(f"\nBot response:\n")
        print(f"✅ Обработано:\n\n{formatted}\n")
        print(f"📝 Подтверждаем создание заказа?\n")

        # Показываем детали для отладки
        print(f"\n[DEBUG] Processed data:")
        print(f"  Technician: {processed_data.get('technician_name')}")
        print(f"  Doctor: {processed_data.get('doctor_name')}")
        print(f"  Patient: {processed_data.get('patient_name')}")
        print(f"  Work Type: {processed_data.get('work_type')}")
        print(f"  Quantity: {processed_data.get('quantity')}")
        print(f"  Deadline: {processed_data.get('deadline')}")
        print(f"  Notes: {processed_data.get('notes')}")
        print(f"  AI Processing: {'YES' if processor.client else 'NO'}")

print("\n" + "=" * 80)
print("FINAL TEST COMPLETED!")
print("=" * 80)
