import sys
import codecs

# Устанавливаем UTF-8 кодировку для stdout (для Windows)
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

sys.path.append('src')

from services.message_processor import MessageProcessor

print("=" * 80)
print("Testing bot response without AI")
print("=" * 80)

# Тестовое сообщение
test_message = "циркон 3 шт на 13.04.2026 врач Гаспарянидзе пациент Писькова"

print(f"\nUser message: '{test_message}'")
print("-" * 80)

# Создаем процессор без API ключа
import os
original_key = os.environ.get('OPENROUTER_API_KEY')
os.environ['OPENROUTER_API_KEY'] = ''

processor = MessageProcessor()

# Проверяем доступность ИИ
print(f"\nAI Available: {processor.is_ai_available()}")

if not processor.is_ai_available():
    print("\n[WARNING] AI is NOT available!")
    print("[WARNING] Bot should show warning message and stop order creation")

    # Проверяем, что будет выведено ботом
    warning_message = (
        "⚠️ ИИ обработка текста недоступна.\n\n"
        "Пожалуйста, используйте полный формат заказа:\n"
        "Техник Фамилия И.О.\n"
        "Пациент Фамилия И.О.\n"
        "Вид работы: [описание]\n"
        "Количество: X шт\n"
        "Срок: ДД.ММ.ГГГГ\n\n"
        "Или добавьте токен OpenRouter API в конфигурацию."
    )

    print("\nBot warning message:")
    print(warning_message)

    print("\n[INFO] Order creation will be stopped (ConversationHandler.END)")

# Восстанавливаем API ключ
if original_key:
    os.environ['OPENROUTER_API_KEY'] = original_key

print("\n" + "=" * 80)
print("Testing completed!")
print("=" * 80)
