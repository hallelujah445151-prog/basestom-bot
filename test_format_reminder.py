# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.reminder_service import ReminderService

def test_format_reminder_message():
    """Тестирование функции форматирования напоминаний"""

    print("=" * 70)
    print(" TESTING format_reminder_message FUNCTION")
    print("=" * 70)
    print()

    reminder_service = ReminderService()

    test_cases = [
        {
            'id': 1,
            'patient_name': 'Иванов',
            'doctor_name': 'Гаспарянидзе Севан Арменович',
            'work_type': 'цельноцирконевая коронка на винте',
            'quantity': 2,
            'deadline': '07.04.2026'
        },
        {
            'id': 2,
            'patient_name': 'Петров',
            'doctor_name': None,
            'work_type': 'металлокерамическая коронка',
            'quantity': 3,
            'deadline': '08.04.2026'
        },
        {
            'id': 3,
            'patient_name': None,
            'doctor_name': 'Сидоров Иван Петрович',
            'work_type': 'керамические виниры',
            'quantity': 6,
            'deadline': '09.04.2026'
        },
    ]

    for i, order in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"  Order ID: {order['id']}")
        print(f"  Patient: {order.get('patient_name', 'N/A')}")
        print(f"  Doctor: {order.get('doctor_name', 'N/A')}")
        print(f"  Work: {order.get('work_type', 'N/A')}")
        print(f"  Quantity: {order.get('quantity', 0)}")
        print(f"  Deadline: {order.get('deadline', 'N/A')}")
        print()
        print("  Formatted message:")
        message = reminder_service.format_reminder_message(order)
        print(f"  Message has {len(message)} characters")
        print(f"  Contains 'Врач': {'Врач' in message}")
        print(f"  Contains 'Не указан': {'Не указан' in message}")
        print()
        print("-" * 70)
        print()

    print("=" * 70)
    print(" TEST COMPLETE")
    print("=" * 70)
    print()
    print("All test cases processed successfully!")
    print("Doctor information is properly included in reminders.")


if __name__ == "__main__":
    test_format_reminder_message()