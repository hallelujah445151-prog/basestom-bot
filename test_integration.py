# -*- coding: utf-8 -*-
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.message_processor import MessageProcessor


def main():
    """Тестирование интеграции DentalTerminologyService в MessageProcessor"""

    print("=" * 60)
    print("Тестирование интеграции DentalTerminologyService")
    print("=" * 60)
    print()

    processor = MessageProcessor()

    test_messages = [
        "Мороков циркон на винте 7шт пациент Иванов",
        "Плюхин металлокерамика 2 шт",
        "Козлов виниры циркон пациент Петров",
        "Сидоров мост циркон 4 зуба",
        "Иванов бюгельный протез",
    ]

    print("Тестирование обработки сообщений...\n")

    for i, message in enumerate(test_messages, 1):
        print(f"Тест {i}: {message}")
        print("-" * 60)

        try:
            result = processor.parse_message_simple(message)

            print("Результат:")
            for key, value in result.items():
                if value:
                    print(f"  {key}: {value}")

        except Exception as e:
            print(f"❌ Ошибка: {e}")

        print()
        print("=" * 60)
        print()


if __name__ == "__main__":
    main()
    input("Нажмите Enter для выхода...")