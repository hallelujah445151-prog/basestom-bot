import sys
sys.path.append('src')

from services.message_processor import MessageProcessor

print("=" * 80)
print("Testing quantity recognition")
print("=" * 80)

# Создаем процессор
processor = MessageProcessor()

# Тестовое сообщение с количеством
test_message = "циркон 3 шт на 13.04.2026 врач Гаспарянидзе пациент Писькова"

print(f"Input message: '{test_message}'")
print("-" * 80)

# Тестируем ИИ обработку
result = processor.normalize_message(test_message)

print(f"\nAI Result:")
print(f"  Technician: {result.get('technician_name')}")
print(f"  Doctor: {result.get('doctor_name')}")
print(f"  Patient: {result.get('patient_name')}")
print(f"  Work Type: {result.get('work_type')}")
print(f"  Quantity: {result.get('quantity')} (type: {type(result.get('quantity'))})")
print(f"  Deadline: {result.get('deadline')}")

# Проверяем, если quantity = 0 или None
quantity = result.get('quantity')
if quantity is None:
    print(f"\n[WARNING] Quantity is None!")
elif quantity == 0:
    print(f"\n[WARNING] Quantity is 0!")
elif quantity:
    print(f"\n[OK] Quantity is {quantity}")
else:
    print(f"\n[WARNING] Quantity has unexpected value: {quantity}")

# Форматируем сообщение
formatted = processor.format_message(result)
print(f"\nFormatted message:\n{formatted}")

print("\n" + "=" * 80)
