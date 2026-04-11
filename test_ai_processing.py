import sys
sys.path.append('src')

from services.message_processor import MessageProcessor

print("=" * 80)
print("Testing AI Message Processing")
print("=" * 80)

# Создаем процессор сообщений
processor = MessageProcessor()

# Тестовые сообщения
test_messages = [
    "Мороков циркон на винте 7шт пациент Иванов",
    "Сидоров металлокерамика 13шт на завтра пациент Петров",
    "Козлов виниры 5шт от Иванова 15.02.2026 пациент Сидоров",
    "Плюхин металлокерамика 2 шт на 02.04.2026 врач Гаспарянидзе пациент Анохин"
]

for i, message in enumerate(test_messages, 1):
    print(f"\nTest {i}: '{message}'")
    print("-" * 80)
    
    result = processor.normalize_message(message)
    
    if result:
        print(f"Technician: {result.get('technician_name')}")
        print(f"Doctor: {result.get('doctor_name')}")
        print(f"Patient: {result.get('patient_name')}")
        print(f"Work Type: {result.get('work_type')}")
        print(f"Quantity: {result.get('quantity')}")
        print(f"Deadline: {result.get('deadline')}")
        print(f"Notes: {result.get('notes')}")
        
        # Проверяем, используется ли ИИ
        if processor.client:
            print("[AI] Using OpenRouter AI for processing")
        else:
            print("[AI] Using simple parser (no AI)")
    else:
        print("ERROR: Failed to process message")

print("\n" + "=" * 80)
print("Testing completed!")
print("=" * 80)
