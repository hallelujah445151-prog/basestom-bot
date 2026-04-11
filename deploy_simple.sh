#!/bin/bash

# ПРОСТОЙ СКРИПТ ДЕПЛОЯ БОТА
# Запустить: bash deploy_simple.sh

echo "🚀 ДЕПЛОЙ BASESTOM БОТА"
echo "======================================="
echo ""

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo ""
    echo "Создайте файл .env с следующим содержанием:"
    echo "BOT_TOKEN=your_bot_token"
    echo "OPENROUTER_API_KEY=your_api_key"
    echo ""
    exit 1
fi

echo "✅ Файл .env найден"
echo ""

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install -r requirements.txt --quiet
echo "✅ Зависимости установлены"
echo ""

# Создание директории данных
echo "📁 Создание директории данных..."
mkdir -p data
echo "✅ Директория создана"
echo ""

# Запуск бота
echo "🚀 ЗАПУСК БОТА"
echo "======================================="
echo ""
echo "Нажмите Ctrl+C для остановки"
echo ""

python src/bot.py
