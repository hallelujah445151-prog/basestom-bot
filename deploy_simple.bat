@echo off
REM ПРОСТОЙ СКРИПТ ЗАПУСКА БОТА (Windows)

echo ========================================
echo DEPLOY BASESTOM BOT
echo ========================================
echo.

REM Проверка .env файла
if not exist ".env" (
    echo [X] File .env not found!
    echo.
    echo Create .env file with:
    echo BOT_TOKEN=your_bot_token
    echo OPENROUTER_API_KEY=your_api_key
    echo.
    pause
    exit /b 1
)

echo [OK] .env file found
echo.

REM Создание директории данных
if not exist "data" (
    mkdir data
    echo [OK] Data directory created
)

REM Установка зависимостей
echo.
echo [INSTALL] Installing dependencies...
pip install -r requirements.txt --quiet
echo [OK] Dependencies installed
echo.

REM Запуск бота
echo ========================================
echo [START] Starting bot...
echo ========================================
echo Press Ctrl+C to stop
echo.

python src\bot.py

pause
