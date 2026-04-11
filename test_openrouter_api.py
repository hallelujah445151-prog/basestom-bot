import os
import sys
import httpx
from openai import OpenAI

# Устанавливаем UTF-8 кодировку для stdout (для Windows)
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Загружаем API ключ
api_key = "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"

print("Testing OpenRouter API connection...")
print("=" * 80)

try:
    # Создаем кастомный httpx клиент без прокси
    http_client = httpx.Client(
        base_url="https://openrouter.ai/api/v1",
        timeout=30.0,
        follow_redirects=True
    )
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        http_client=http_client
    )
    print("✅ OpenAI client initialized successfully")
    
    # Тестовый запрос
    test_prompt = """
    Текст: "Мороков циркон на винте 7шт пациент Иванов"

    Распознай данные в формате JSON:
    {
        "technician_name": "ФИО техники",
        "work_type": "вид работы",
        "quantity": количество,
        "patient_name": "пациент"
    }
    """

    print("\nSending test request...")
    response = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[
            {"role": "system", "content": "Ты эксперт по обработке заказов в зуботехнической лаборатории."},
            {"role": "user", "content": test_prompt}
        ],
        temperature=0.3
    )

    print(f"\n[OK] Response received!")
    print(f"Model: {response.model}")
    print(f"Response: {response.choices[0].message.content}")

except Exception as e:
    print(f"\n[ERROR] {e}")
    print(f"Error type: {type(e).__name__}")
