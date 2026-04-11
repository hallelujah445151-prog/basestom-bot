import sys
sys.path.append('src')

from services.message_processor import MessageProcessor

print("=" * 80)
print("Testing format_message() method")
print("=" * 80)

# Создаем процессор сообщений
processor = MessageProcessor()

# Тестовые данные (уже нормализованные)
test_data = [
    {
        'technician_name': 'Мороков',
        'patient_name': 'Иванов',
        'work_type': 'цельнометаллическая коронка на винте',
        'quantity': 7
    },
    {
        'technician_name': 'Сидоров',
        'patient_name': 'Петров',
        'work_type': 'металлокерамическая коронка',
        'quantity': 13,
        'notes': 'на завтра'
    },
    {
        'technician_name': 'Козлов',
        'doctor_name': 'Иванов',
        'patient_name': 'Сидоров',
        'work_type': 'керамические виниры из диоксида циркония',
        'quantity': 5,
        'deadline': '15.02.2026'
    },
    {
        'technician_name': 'Плюхин',
        'doctor_name': 'Гаспарянидзе',
        'patient_name': 'Анохин',
        'work_type': 'керамические виниры из диоксида циркония',
        'quantity': 2,
        'deadline': '02.04.2026'
    }
]

for i, data in enumerate(test_data, 1):
    print(f"\nTest {i}:")
    print("-" * 80)
    
    formatted = processor.format_message(data)
    print(formatted)

print("\n" + "=" * 80)
print("Testing completed!")
print("=" * 80)
