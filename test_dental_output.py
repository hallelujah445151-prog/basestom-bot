# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.dental_terminology_service import DentalTerminologyService


def run_test():
    """Тестирование и вывод результатов"""
    
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

    passed = 0
    failed = 0

    for i, (input_text, expected) in enumerate(test_cases, 1):
        try:
            print(u"Тест {i}: {input_text}")
            result = service.normalize_work_type(input_text)
            is_correct = result.lower() == expected.lower()
            
            if is_correct:
                passed += 1
                print(u"   Ожидается: {expected}")
                print(u"   Результат: {result}")
                print(u"   Статус: ✅ ПРОВЕРНО")
            else:
                failed += 1
                print(u"   Ожидается: {expected}")
                print(u"   Результат: {result}")
                print(u"   Статус: ❌ ОШИБКА")
            
        except Exception as e:
            print(u"   Ошибка: {e}")
            failed += 1

    print()
    print(u"=" * 50)
    print(f"Результат: {passed}/{len(test_cases)} пройдено, {failed} с ошибками")
    print("=" * 50)
    print(u"Нажмите Enter для завершения...")

    input()


if __name__ == "__main__":
    run_test()
