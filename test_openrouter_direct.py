# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_openrouter_direct():
    """Тестирование OpenRouter API напрямую"""

    api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key:
        print("❌ OPENROUTER_API_KEY не найден!")
        return

    print(f"API ключ найден: {api_key[:20]}...")
    print()

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=15.0
        )

        print("Тестирование соединения с OpenRouter...")

        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "user", "content": "Напиши: 2 + 2"}
            ],
            temperature=0.3
        )

        result = response.choices[0].message.content.strip()
        print(f"Ответ OpenRouter: {result}")
        print("Соединение с OpenRouter работает!")

        print()
        print("Тестирование стоматологической терминологии...")

        test_input = "циркон на винте"
        system_prompt = """
        Ты эксперт по стоматологической терминологии. Твоя задача - исправить и нормализовать название стоматологической работы.

        ПРАВИЛА КОНВЕРТАЦИИ:
        1. циркон, циркониевый, диоксид циркония → цельноцирконевый
        2. металлокерамика, мк → металлокерамическая коронка
        3. на винте, винт → на винте

        Примеры:
        "циркон на винте" → "цельноцирконевая коронка на винте"
        "металлокерамика" → "металлокерамическая коронка"

        Верни ТОЛЬКО исправленное название работы.
        """

        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_input}
            ],
            temperature=0.3
        )

        result = response.choices[0].message.content.strip()
        print(f"Вход: {test_input}")
        print(f"Выход: {result}")

        expected = "цельноцирконевая коронка на винте"
        if result.lower() == expected.lower():
            print(f"Тест пройден!")
        else:
            print(f"Тест не пройден. Ожидалось: {expected}")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    test_openrouter_direct()
    input("\nНажмите Enter для выхода...")