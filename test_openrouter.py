# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI

def test_openrouter():
    """Тестирование соединения с OpenRouter"""
    
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            print("❌ OPENROUTER_API_KEY не найден в .env!")
            return
        
        print(f"🔑 Ключ API: {api_key}")
        print("🌐 Проверка соединения с OpenRouter...")
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=15.0
        )
        
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "user", "content": "Напиши: 1 + 1"}
            ],
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ Ответ OpenRouter: {result}")
        print("✅ Соединение с OpenRouter работает!")
        
    except Exception as e:
        print(f"❌ Ошибка OpenRouter: {e}")


def test_dental():
    """Тестирование стоматологической терминологии"""
    
    try:
        test_openrouter()
    except:
        print("⚠️ Пропуск теста OpenRouter (соединение не работает)")
    
    print("\n" + "=" * 50)
    print("  Тестирование стоматологической терминологии")
    print("=" * 50)
    print()
    
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

    print(f"Тесты на промпте OpenRouter (Meta Llama 3 8B)\n")

    for i, (input_text, expected) in enumerate(test_cases, 1):
        try:
            print(u"{i}. Вход: {input_text}")
            print(f"   Ожидается: {expected}")
            print()
            
            result = service.normalize_work_type(input_text)
            is_correct = result.lower() == expected.lower()
            
            status = u"✅ ПРОВЕРНО" if is_correct else u"❌ ОШИБКА"
            
            print(u"   Результат: {result}")
            print(u"   Статус: {status}")
            print()
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            print()


if __name__ == "__main__":
    test_dental()
    print("\n" + "=" * 50)
    input("Нажмите Enter для завершения...")
