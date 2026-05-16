import sys
import codecs

# Устанавливаем UTF-8 кодировку для stdout (для Windows)
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

sys.path.append('src')

from services.message_processor import MessageProcessor

print("=" * 80)
print("Testing bot response WITH AI")
print("=" * 80)

# Тестовое сообщение
test_message = "циркон 3 шт на 13.04.2026 врач Гаспарянидзе пациент Писькова"

print(f"\nUser message: '{test_message}'")
print("-" * 80)

processor = MessageProcessor()

# Проверяем доступность ИИ
ai_available = processor.is_ai_available()
print(f"\nAI Available: {ai_available}")

if ai_available:
    print("\n[OK] AI is available!")
    print("[OK] Bot will use AI for message processing")

    # Обрабатываем сообщение через ИИ
    processed_data = processor.normalize_message(test_message)

    print("\nProcessed data:")
    print(f"  Technician: {processed_data.get('technician_name')}")
    print(f"  Doctor: {processed_data.get('doctor_name')}")
    print(f"  Patient: {processed_data.get('patient_name')}")
    print(f"  Work Type: {processed_data.get('work_type')}")
    print(f"  Quantity: {processed_data.get('quantity')}")
    print(f"  Deadline: {processed_data.get('deadline')}")

    # Форматируем сообщение
    formatted = processor.format_message(processed_data)

    print("\nBot response:")
    print(f"✅ Обработано:\n\n{formatted}\n\n")
    print(f"📝 Подтверждаем создание заказа?")
else:
    print("\n[WARNING] AI is NOT available!")
    print("[WARNING] Bot should show warning message and stop order creation")

print("\n" + "=" * 80)
print("Testing completed!")
print("=" * 80)
