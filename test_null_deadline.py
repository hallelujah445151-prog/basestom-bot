import sys
sys.path.append('src')

from handlers.orders import OrderHandler

print("=" * 80)
print("Testing Order Creation with NULL deadline")
print("=" * 80)

# Создаем handler
order_handler = OrderHandler()

# Тестовые данные с NULL deadline
test_data = {
    'doctor_name': None,
    'technician_name': 'Плюхин',
    'patient_name': 'Иванов',
    'work_type': 'металлокерамическая коронка',
    'quantity': 2,
    'deadline': None,  # NULL значение
    'description': 'Тестовый заказ'
}

print(f"Test data: {test_data}")
print(f"  doctor_name: {test_data.get('doctor_name')}")
print(f"  technician_name: {test_data.get('technician_name')}")
print(f"  patient_name: {test_data.get('patient_name')}")
print(f"  work_type: {test_data.get('work_type')}")
print(f"  quantity: {test_data.get('quantity')}")
print(f"  deadline: {test_data.get('deadline')}")
print(f"  description: {test_data.get('description')}")

# Проверяем обработку NULL значений
print("\nProcessing NULL values:")
print(f"  quantity: {test_data.get('quantity') if test_data.get('quantity') is not None else 0}")
print(f"  deadline: {test_data.get('deadline') if test_data.get('deadline') is not None else ''}")

print("\n" + "=" * 80)
print("Testing completed!")
print("=" * 80)
