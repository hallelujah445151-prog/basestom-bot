import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.dental_terminology_service import DentalTerminologyService


def test_and_save():
    """Тестирование и сохранение результатов"""

    print("Тестирование стоматологической терминологии...")
    print()

    service = DentalTerminologyService()

    # Тестовые примеры
    test_cases = [
        ("циркон на винте7шт", "цельноцирконевая коронка на винте (7 шт)"),
        ("виниры циркон", "керамические виниры из диокса циркония"),
        ("мост циркон 4 зуба", "мост из диоксида циркония (4 зуба)"),
        ("бюгельный протез", "бюгельный протез"),
        ("абатмент", "абатмент"),
        ("кламмеры", "кламмеры"),
        ("Плюхин металлокерамика 2 шт", "металлокерамическая коронка (2 шт)"),
        ("Мороков циркон на винте7шт", "цельноцирконевая коронка на винте (7 шт)"),
        ("Козлов виниры циркон", "керамические виниры из диоксида циркония"),
    ]

    results = []

    for input_text, expected in test_cases:
        print(f"Вход: {input_text}")
        result = service.normalize_work_type(input_text)
        is_correct = result.lower() == expected.lower()
        results.append({
            'input': input_text,
            'expected': expected,
            'result': result,
            'correct': is_correct
        })

        # Сохраняем результаты в файл
        with open('dental_test_results.txt', 'w', encoding='utf-8') as f:
            f.write("=== Тестирование стоматологической терминологии ===\n\n")
            for r in results:
                f.write(f"Вход: {r['input']}\n")
                f.write(f"Ожидается: {r['expected']}\n")
                f.write(f"Результат: {r['result']}\n")
                f.write(f"Статус: {'✅ ПРОВЕРНО' if r['correct'] else '❌ ОШИБКА'}\n\n")
            passed = sum(1 for r in results if r['correct'])
            f.write(f"Итого: {passed}/{len(results)} пройдено\n")

        print(f"Тесты сохранены в: dental_test_results.txt")

    return results


if __name__ == "__main__":
    test_and_save()
    input("\nНажмите Enter для выхода...")
