@echo off
chcp 65001 >nul
echo =============================================
echo Быстрый деплой на VPS (одна команда)
echo =============================================
echo.

cd /d "C:\Users\crush\AppData\Roaming\projects\basestom"

echo Шаг 1: Создание архива проекта...
tar -czf basestom-bot-deploy.tar.gz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='venv' --exclude='.env' --exclude='data/orders.db' --exclude='*.log' --exclude='test_*.py' requirements.txt DEPLOY_COMMANDS.md supervisor.conf src/ data/references.json src/.env

if %errorlevel% neq 0 (
    echo Ошибка при создании архива!
    pause
    exit /b 1
)

echo.
echo Шаг 2: Загрузка архива на VPS...
echo Введите пароль для root@31.129.99.125:
echo.
scp basestom-bot-deploy.tar.gz root@31.129.99.125:/tmp/

if %errorlevel% neq 0 (
    echo Ошибка при загрузке архива на VPS!
    pause
    exit /b 1
)

echo.
echo Шаг 3: Установка и настройка на VPS...
echo Введите пароль для root@31.129.99.125:
echo.

ssh root@31.129.99.125 "cd /opt/basestom-bot ^&^& tar -xzf /tmp/basestom-bot-deploy.tar.gz ^&^& rm /tmp/basestom-bot-deploy.tar.gz ^&^& source venv/bin/activate ^&^& pip install -r requirements.txt ^&^& supervisorctl restart basestom-bot ^&^& supervisorctl status basestom-bot"

if %errorlevel% neq 0 (
    echo Ошибка при установке на VPS!
    pause
    exit /b 1
)

echo.
echo Удаление локального архива...
del basestom-bot-deploy.tar.gz

echo.
echo =============================================
echo Деплой завершен успешно!
echo =============================================
echo.
echo Проверьте работу бота в Telegram:
echo 1. Найдите бота: @sfdtgafvdba_bot
echo 2. Напишите /start
echo.
echo Для управления ботом:
echo   Статус:  ssh root@31.129.99.125 supervisorctl status basestom-bot
echo   Логи:    ssh root@31.129.99.125 supervisorctl tail -f basestom-bot
echo.
pause
