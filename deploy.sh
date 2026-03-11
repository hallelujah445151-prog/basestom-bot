#!/bin/bash

# Скрипт для автоматической установки бота на VPS

echo "🚀 Начинаем установку бота на VPS..."

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
echo "🔧 Установка Python, pip, git и supervisor..."
sudo apt install python3 python3-pip git supervisor -y

# Создание директории проекта
echo "📁 Создание директории проекта..."
sudo mkdir -p /opt/basestom-bot
sudo chown $USER:$USER /opt/basestom-bot

# Создание виртуального окружения
echo "🐍 Создание виртуального окружения..."
cd /opt/basestom-bot
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей Python
echo "📥 Установка зависимостей Python..."
pip install -r requirements.txt

# Создание файла .env (если его нет)
if [ ! -f "src/.env" ]; then
    echo "⚠️  Файл .env не найден. Создайте его вручную в src/ с токенами:"
    echo "   BOT_TOKEN=your_bot_token"
    echo "   OPENROUTER_API_KEY=your_api_key"
    echo ""
    read -p "Введите токен бота: " BOT_TOKEN
    read -p "Введите API ключ OpenRouter: " OPENROUTER_KEY

    mkdir -p src
    cat > src/.env << EOF
BOT_TOKEN=$BOT_TOKEN
OPENROUTER_API_KEY=$OPENROUTER_KEY
EOF
    echo "✅ Файл .env создан"
fi

# Настройка Supervisor
echo "⚙️  Настройка Supervisor..."
sudo cp supervisor.conf /etc/supervisor/conf.d/basestom-bot.conf

# Замена username в supervisor.conf
CURRENT_USER=$(whoami)
sudo sed -i "s/your_username/$CURRENT_USER/g" /etc/supervisor/conf.d/basestom-bot.conf

# Перезагрузка Supervisor
echo "🔄 Перезагрузка Supervisor..."
sudo supervisorctl reread
sudo supervisorctl update

# Запуск бота
echo "▶️  Запуск бота..."
sudo supervisorctl start basestom-bot

# Проверка статуса
echo "📊 Статус бота:"
sudo supervisorctl status basestom-bot

echo ""
echo "✅ Установка завершена!"
echo ""
echo "Проверьте работу бота в Telegram:"
echo "1. Найдите бота: @sfdtgafvdba_bot"
echo "2. Напишите /start"
echo ""
echo "Команды управления:"
echo "  Запуск:   sudo supervisorctl start basestom-bot"
echo "  Остановка: sudo supervisorctl stop basestom-bot"
echo "  Рестарт:  sudo supervisorctl restart basestom-bot"
echo "  Статус:   sudo supervisorctl status basestom-bot"
echo "  Логи:     sudo supervisorctl tail -f basestom-bot"
