import sys
sys.path.append('src')

from services.message_processor import MessageProcessor

print("=" * 80)
print("Testing AI availability check")
print("=" * 80)

# Создаем процессор с ИИ (доступен)
processor_with_ai = MessageProcessor()
print(f"\n1. AI Available: {processor_with_ai.is_ai_available()}")

# Тестовая проверка: создаем процессор без API ключа
import os

# Временно скрываем API ключ
original_key = os.environ.get('OPENROUTER_API_KEY')
os.environ['OPENROUTER_API_KEY'] = ''

# Создаем процессор без ИИ
processor_without_ai = MessageProcessor()
print(f"2. AI Available (no API key): {processor_without_ai.is_ai_available()}")

# Восстанавливаем API ключ
if original_key:
    os.environ['OPENROUTER_API_KEY'] = original_key

print("\n" + "=" * 80)
print("Testing completed!")
print("=" * 80)
print("\nРезультат:")
print("- Если API ключ есть → AI Available: True")
print("- Если API ключ нет → AI Available: False")
print("- При AI Available: False → бот будет показывать предупреждение")
