#!/bin/bash

# ============================================
# Быстрый деплой на VPS (одна команда)
# ============================================

echo "============================================="
echo "Быстрый деплой на VPS (одна команда)"
echo "============================================="
echo ""

cd "$(dirname "$0")"

# Шаг 1: Создание архива проекта
echo "Шаг 1: Создание архива проекта..."
tar -czf basestom-bot-deploy.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='data/orders.db' \
    --exclude='*.log' \
    --exclude='test_*.py' \
    requirements.txt \
    DEPLOY_COMMANDS.md \
    supervisor.conf \
    src/ \
    data/references.json \
    src/.env

if [ $? -ne 0 ]; then
    echo "Ошибка при создании архива!"
    exit 1
fi

echo ""
echo "Шаг 2: Загрузка архива на VPS..."
echo "Введите пароль для root@31.129.99.125:"
echo ""

scp basestom-bot-deploy.tar.gz root@31.129.99.125:/tmp/

if [ $? -ne 0 ]; then
    echo "Ошибка при загрузке архива на VPS!"
    exit 1
fi

echo ""
echo "Шаг 3: Установка и настройка на VPS..."
echo "Введите пароль для root@31.129.99.125:"
echo ""

ssh root@31.129.99.125 << 'ENDSSH'
cd /opt/basestom-bot
tar -xzf /tmp/basestom-bot-deploy.tar.gz
rm /tmp/basestom-bot-deploy.tar.gz
source venv/bin/activate
pip install -r requirements.txt
supervisorctl restart basestom-bot
supervisorctl status basestom-bot
ENDSSH

if [ $? -ne 0 ]; then
    echo "Ошибка при установке на VPS!"
    exit 1
fi

echo ""
echo "Удаление локального архива..."
rm basestom-bot-deploy.tar.gz

echo ""
echo "============================================="
echo "Деплой завершен успешно!"
echo "============================================="
echo ""
echo "Проверьте работу бота в Telegram:"
echo "1. Найдите бота: @sfdtgafvdba_bot"
echo "2. Напишите /start"
echo ""
echo "Для управления ботом:"
echo "  Статус:  ssh root@31.129.99.125 supervisorctl status basestom-bot"
echo "  Логи:    ssh root@31.129.99.125 supervisorctl tail -f basestom-bot"
echo ""
