# -*- coding: utf-8 -*-
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.dental_terminology_service import DentalTerminologyService


def main():
    """Тестирование и сохранение результатов"""
    
    print(u"Тестирование стоматологической терминологии...\n")
    
    service = DentalTerminologyService()

    test_cases = [
        (u"циркон на винте7шт", u"цельноцирконевая коронка на винте (7 шт)"),
        (u"виниры циркон", u"керамические виниры из диоксида циркония"),
        (u"мост циркон 4 зуба", u"мост из диоксида циркония (4 зуба)"),
        (u"бюгельный протез", u"бюгельный протез"),
        (u"абатмент", u"абатмент"),
        (u"кламмеры", u"кламмеры"),
        (u"Плюхин металлокерамика 2 шт", u"металлокерамическая коронка (2 шт)"),
        (u"Мороков циркон на винте7шт", u"цельноцирконевая коронка на винте (7 шт)"),
        (u"Козлов виниры циркон", u"керамические виниры из диоксида циркония"),
    ]

    output_path = os.path.join(os.path.dirname(__file__), "dental_test_results.txt")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(u"=== Тестирование стоматологической терминологии ===\n\n")
        
        for i, (input_text, expected) in enumerate(test_cases, 1):
            print(u"Тест {i}: {input_text} -> ...")
            result = service.normalize_work_type(input_text)
            is_correct = result.lower() == expected.lower()
            status = u"✅ ПРОВЕРНО" if is_correct else u"❌ ОШИБКА"
            
            f.write(u"Тест {i}: {input_text}\n")
            f.write(u"Ожидается: {expected}\n")
            f.write(u"Результат: {result}\n")
            f.write(u"Статус: {status}\n\n")

        passed = sum(1 for i, (input_text, expected) in enumerate(test_cases, 1) if service.normalize_work_type(input_text).lower() == expected.lower())
        total = len(test_cases)
        f.write(f"\nИтого: {passed}/{total} пройдено\n")
    
    print(u"Тесты сохранены в: {output_path}")
    print(u"\nРезультаты:")
    print(u"  Файл: dental_test_results.txt")


if __name__ == "__main__":
    main()
    input(u"\nНажмите Enter для выхода...")