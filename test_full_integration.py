# -*- coding: utf-8 -*-
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.message_processor import MessageProcessor


def main():
    """Полное тестирование интеграции"""

    print("=" * 70)
    print(" ПОЛНОЕ ТЕСТИРОВАНИЕ DentalTerminologyService")
    print("=" * 70)
    print()

    processor = MessageProcessor()

    print("1. ТЕСТИРОВАНИЕ ПРЯМОГО ВЫЗОВА ДЕНТАЛЬНОГО СЕРВИСА")
    print("-" * 70)
    print()

    dental_tests = [
        ("циркон на винте", "цельноцирконевая коронка на винте"),
        ("виниры циркон", "керамические виниры"),
        ("металлокерамика", "металлокерамическая коронка"),
        ("мост циркон", "мост из циркония"),
    ]

    for i, (input_text, expected) in enumerate(dental_tests, 1):
        result = processor.normalize_dental_terminology(input_text)
        status = "OK" if result.lower() == expected.lower() else "WARN"
        print(f"{status} {i}. {input_text:20} -> {result}")

    print()
    print("2. ТЕСТИРОВАНИЕ КЭШИРОВАНИЯ")
    print("-" * 70)
    print()

    test_term = "циркон на винте"
    print(f"Первый вызов: '{test_term}'")
    result1 = processor.normalize_dental_terminology(test_term)
    print(f"Результат: {result1}")

    print(f"Второй вызов (из кэша): '{test_term}'")
    result2 = processor.normalize_dental_terminology(test_term)
    print(f"Результат: {result2}")

    print()
    print("3. ТЕСТИРОВАНИЕ ОБРАБОТКИ СООБЩЕНИЙ")
    print("-" * 70)
    print()

    message_tests = [
        "Мороков циркон на винте 7шт пациент Иванов",
        "Плюхин металлокерамика 2 шт",
        "Козлов виниры циркон пациент Петров",
    ]

    for i, message in enumerate(message_tests, 1):
        print(f"Тест {i}: {message}")
        result = processor.parse_message_simple(message)

        formatted = processor.format_message(result)
        print(f"Форматированное сообщение: {formatted}")
        print()

    print("4. ТЕСТИРОВАНИЕ ФОРМАТИРОВАНИЯ С ДАННЫМИ")
    print("-" * 70)
    print()

    test_data = {
        'technician_name': 'Мороков',
        'patient_name': 'Иванов',
        'work_type': 'циркон на винте',
        'quantity': 7,
        'deadline': '15.04.2026'
    }

    formatted = processor.format_message(test_data)
    print(f"Данные: {test_data}")
    print(f"Форматированное: {formatted}")

    print()
    print("=" * 70)
    print(" ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 70)


if __name__ == "__main__":
    main()