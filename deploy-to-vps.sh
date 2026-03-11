#!/bin/bash

# ============================================
# Скрипт автоматического деплоя на VPS
# ============================================
# IP: 31.129.99.125
# Логин: root
# ============================================

set -e

echo "🚀 Начинаем деплой на VPS..."
echo ""

# Проверка наличия файла с токенами
if [ ! -f "src/.env" ]; then
    echo "❌ Файл src/.env не найден!"
    echo "Создайте его с токенами:"
    echo ""
    echo "BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8"
    echo "OPENROUTER_API_KEY=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"
    echo ""
    exit 1
fi

echo "✅ Файл src/.env найден"

# Настройка переменных
VPS_IP="31.129.99.125"
VPS_USER="root"
VPS_PATH="/opt/basestom-bot"
LOCAL_PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Загрузка файлов на VPS..."
echo ""

# Создание архива проекта
echo "📁 Создание архива проекта..."
ARCHIVE_NAME="basestom-bot-deploy.tar.gz"
tar -czf $ARCHIVE_NAME \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='data/orders.db' \
    --exclude='*.log' \
    --exclude='REPLIT_DEPLOYMENT.md' \
    --exclude='test_*.py' \
    requirements.txt \
    VPS_DEPLOYMENT.md \
    DEPLOYMENT_FILES.md \
    supervisor.conf \
    deploy.sh \
    src/ \
    data/references.json \
    src/.env

echo "✅ Архив создан: $ARCHIVE_NAME"

# Загрузка на VPS через SSH
echo "📤 Загрузка архива на VPS ($VPS_IP)..."
echo ""
echo "🔐 Введите пароль для $VPS_USER@$VPS_IP:"
echo ""

# Копирование архива на VPS
scp $ARCHIVE_NAME $VPS_USER@$VPS_IP:/tmp/

echo "✅ Архив загружен на VPS"

# Выполнение команд на VPS через SSH
echo ""
echo "🔧 Установка и настройка на VPS..."
echo ""
echo "🔐 Введите пароль для $VPS_USER@$VPS_IP:"
echo ""

ssh $VPS_USER@$VPS_IP << 'ENDSSH'
set -e

echo "📦 Обновление системы..."
apt update && apt upgrade -y

echo "🔧 Установка Python, pip, git и supervisor..."
apt install -y python3 python3-pip git supervisor

echo "📁 Создание директории проекта..."
mkdir -p /opt/basestom-bot

echo "📦 Распаковка архива..."
cd /opt/basestom-bot
tar -xzf /tmp/basestom-bot-deploy.tar.gz
rm /tmp/basestom-bot-deploy.tar.gz

echo "✅ Файлы распакованы"

echo "🐍 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

echo "📥 Установка зависимостей..."
pip install -r requirements.txt

echo "✅ Зависимости установлены"

echo "⚙️  Настройка Supervisor..."
CURRENT_USER=$(whoami)
sed "s/your_username/$CURRENT_USER/g" supervisor.conf > /tmp/basestom-bot.conf
cp /tmp/basestom-bot.conf /etc/supervisor/conf.d/basestom-bot.conf
rm /tmp/basestom-bot.conf

echo "✅ Supervisor настроен"

echo "🔄 Перезагрузка Supervisor..."
supervisorctl reread
supervisorctl update
supervisorctl stop basestom-bot || true
supervisorctl start basestom-bot

echo ""
echo "📊 Статус бота:"
supervisorctl status basestom-bot

echo ""
echo "✅ Деплой завершен!"
echo ""
echo "Проверьте работу бота в Telegram:"
echo "1. Найдите бота: @sfdtgafvdba_bot"
echo "2. Напишите /start"
echo ""
echo "Команды управления на VPS:"
echo "  Запуск:   supervisorctl start basestom-bot"
echo "  Остановка: supervisorctl stop basestom-bot"
echo "  Рестарт:  supervisorctl restart basestom-bot"
echo "  Статус:   supervisorctl status basestom-bot"
echo "  Логи:     supervisorctl tail -f basestom-bot"
echo ""

ENDSSH

# Удаление локального архива
echo "🧹 Удаление локального архива..."
rm $ARCHIVE_NAME

echo "✅ Всё готово!"
echo ""
echo "Бот запущен на VPS: $VPS_IP"
echo "Для управления подключитесь по SSH:"
echo "  ssh root@$VPS_IP"
echo ""
