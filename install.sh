#!/bin/bash

# ============================================
# Скрипт установки бота на VPS
# Запускать на VPS после подключения по SSH
# ============================================

set -e

echo "========================================"
echo "  Установка бота на VPS"
echo "========================================"
echo ""

# Проверка, запущен ли как root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Пожалуйста, запустите скрипт как root"
    echo "Используйте: sudo bash install.sh"
    exit 1
fi

echo "✅ Запуск от root"
echo ""

# Обновление системы
echo "📦 Обновление системы..."
apt update && apt upgrade -y

# Установка зависимостей
echo "🔧 Установка зависимостей..."
apt install -y python3 python3-pip python3-venv git supervisor

# Удаление старого проекта
echo "🗑️  Удаление старого проекта (если есть)..."
rm -rf /opt/basestom-bot

# Создание директории проекта
echo "📁 Создание директории проекта..."
mkdir -p /opt/basestom-bot
cd /opt/basestom-bot

# Клонирование с GitHub
echo "📥 Клонирование проекта с GitHub..."
git clone https://github.com/hallelujah445151-prog/basestom-bot.git .
git pull origin master

# Создание файла .env
echo "📝 Создание файла .env..."
cat > src/.env << 'EOF'
BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8
OPENROUTER_API_KEY=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
EOF

echo "✅ Файл .env создан"

# Создание виртуального окружения
echo "🐍 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Зависимости установлены"

# Настройка Supervisor
echo "⚙️  Настройка Supervisor..."
cat supervisor.conf | sed 's|your_username|root|g' > /etc/supervisor/conf.d/basestom-bot.conf
supervisorctl reread
supervisorctl update

# Создание логов
echo "📝 Создание лог-файлов..."
touch /var/log/basestom-bot.out.log /var/log/basestom-bot.err.log
chmod 644 /var/log/basestom-bot.*.log

# Остановка бота (если был запущен)
echo "🛑 Остановка старого процесса (если есть)..."
supervisorctl stop basestom-bot 2>/dev/null || true

# Запуск бота
echo "🚀 Запуск бота..."
supervisorctl start basestom-bot

# Ожидание запуска
sleep 3

# Проверка статуса
echo ""
echo "📊 Статус бота:"
supervisorctl status basestom-bot

echo ""
echo "========================================"
echo "  Установка завершена!"
echo "========================================"
echo ""
echo "✅ Бот запущен на VPS"
echo ""
echo "Проверьте бота в Telegram:"
echo "1. Найдите бота: @sfdtgafvdba_bot"
echo "2. Напишите: /start"
echo ""
echo "Команды управления:"
echo "  Статус:   supervisorctl status basestom-bot"
echo "  Логи:     supervisorctl tail -f basestom-bot"
echo "  Рестарт:  supervisorctl restart basestom-bot"
echo "  Остановка: supervisorctl stop basestom-bot"
echo ""
