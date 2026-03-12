# 🚀 Запуск бота локально

## Требования

- ✅ Python 3.14.3 (уже установлен)
- ✅ pip 25.3 (уже установлен)
- ✅ Файл `.env` с токенами (существует)

## Установка зависимостей

### Windows (cmd)
```cmd
cd C:\Users\crush\AppData\Roaming\projects\basestom
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
cd C:\Users\crush\AppData\Roaming\projects\basestom
pip install -r requirements.txt
```

## Запуск бота

### Windows (cmd)
```cmd
cd C:\Users\crush\AppData\Roaming\projects\basestom
python src/bot.py
```

### Windows (PowerShell)
```powershell
cd C:\Users\crush\AppData\Roaming\projects\basestom
python src\bot.py
```

## Что будет в консоли

```
Bot started...
Reminder background task started...
```

## Остановка бота

**Нажмите `Ctrl + C`** в консоли для остановки

## Возможные проблемы

### 1. ModuleNotFoundError: No module named 'telegram'

**Решение:**
```cmd
pip install python-telegram-bot==20.7
```

### 2. ImportError: No module named 'dotenv'

**Решение:**
```cmd
pip install python-dotenv==1.0.0
```

### 3. FileNotFoundError: .env file not found

**Решение:**
Проверьте, что файл `src\.env` существует и содержит:
```
BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8
OPENROUTER_API_KEY=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
```

### 4. Telegram API Error

**Решение:**
- Проверьте, что токен бота правильный
- Проверьте, что бот не был удален через BotFather
- Проверьте интернет-соединение

## Тестирование

После запуска:

1. **Откройте Telegram**
2. **Найдите бота:** `@sfdtgafvdba_bot`
3. **Напишите:** `/start`
4. **Должно прийти приветственное сообщение**

## Локальная база данных

Бот создаст локальную базу данных:
```
C:\Users\crush\AppData\Roaming\projects\basestom\data\orders.db
```

**Важно:** Локальная БД отделена от БД на VPS.

## Автоматический запуск

### Создание bat-файла для быстрого запуска

Создайте файл `run_local.bat` в папке `basestom`:
```batch
@echo off
cd /d "%~dp0"
echo Starting bot locally...
python src\bot.py
pause
```

**Запуск:** Дважды кликните по `run_local.bat`

### Создание PowerShell скрипта

Создайте файл `run_local.ps1`:
```powershell
cd "C:\Users\crush\AppData\Roaming\projects\basestom"
Write-Host "Starting bot locally..."
python src\bot.py
```

**Запуск:** Щелкните правой кнопкой → "Запуск с помощью PowerShell"

## Различия между локальным и VPS запуском

| Характеристика | Локально | VPS |
|--------------|----------|-----|
| Доступность | Только когда запущен | Постоянно |
| База данных | Отдельная локальная | Отдельная на сервере |
| Интернет | Требуется | Требуется |
| Перезапуск | Вручную | Автоматически (Supervisor) |
| Логи | В консоли | В файле `/var/log/` |

## Полезные команды

### Проверка зависимостей
```cmd
pip list | findstr "telegram dotenv openai"
```

### Обновление зависимостей
```cmd
pip install -r requirements.txt --upgrade
```

### Удаление зависимостей
```cmd
pip uninstall python-telegram-bot python-dotenv openai -y
```

### Чистка кэша Python
```cmd
cd C:\Users\crush\AppData\Roaming\projects\basestom
rmdir /s /q __pycache__
rmdir /s /q src\__pycache__
rmdir /s /q src\handlers\__pycache__
rmdir /s /q src\services\__pycache__
rmdir /s /q src\utils\__pycache__
```

## Советы

1. **Используйте отдельное окно консоли** для логов бота
2. **Не закрывайте консоль** случайно, бот остановится
3. **Сохраняйте файл `run_local.bat`** для быстрого запуска
4. **Регулярно обновляйте зависимости** перед запуском
5. **Делайте бэкап локальной БД** перед тестами:
   ```cmd
   copy data\orders.db data\orders.db.backup
   ```

## Быстрый старт

```cmd
cd C:\Users\crush\AppData\Roaming\projects\basestom
pip install -r requirements.txt
python src\bot.py
```

Готово! Бот запущен локально.
