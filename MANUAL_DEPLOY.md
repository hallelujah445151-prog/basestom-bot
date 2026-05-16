# Ручной деплой на сервер

## Петод 1: Использование Git (если код на GitHub)

### На локальной машине:
```powershell
cd C:\Users\crush\AppData\Roaming\projects\basestom
git add .
git commit -m "Описание изменений"
git push
```

### На сервере:
```bash
ssh root@31.129.99.125
cd /opt/basestom-bot
git pull
source venv/bin/activate
pip install -r requirements.txt
supervisorctl restart basestom-bot
supervisorctl status basestom-bot
```

## Петод 2: Ручной деплой (без Git)

### Шаг 1: Создание архива на локальной машине

**PowerShell:**
```powershell
cd C:\Users\crush\AppData\Roaming\projects\basestom

# Создайте список файлов для включения
$files = @(
    "src",
    "requirements.txt",
    "DEPLOY_COMMANDS.md",
    "supervisor.conf",
    "data/references.json",
    "src/.env"
)

# Создайте ZIP архив
Compress-Archive -Path $files -DestinationPath "basestom-bot.zip" -Force
```

### Шаг 2: Загрузка архива на сервер

**Используйте WinSCP или команду scp:**
```bash
scp basestom-bot.zip root@31.129.99.125:/tmp/
```

### Шаг 3: Распаковка и установка на сервере

```bash
# Подключение к серверу
ssh root@31.129.99.125

# Распаковка архива
cd /opt/basestom-bot
unzip -o /tmp/basestom-bot.zip
rm /tmp/basestom-bot.zip

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Перезапуск бота
supervisorctl restart basestom-bot

# Проверка статуса
supervisorctl status basestom-bot
```

## Петод 3: Редактирование файлов напрямую на сервере

```bash
# Подключение к серверу
ssh root@31.129.99.125

# Переход в директорию бота
cd /opt/basestom-bot

# Редактирование файла
nano src/services/message_processor.py

# Сохранение: Ctrl+O, Enter
# Выход: Ctrl+X

# Перезапуск бота
supervisorctl restart basestom-bot

# Проверка статуса
supervisorctl status basestom-bot

# Просмотр логов
supervisorctl tail -f basestom-bot
```

## Проверка после деплоя

1. Откройте Telegram
2. Найдите бота: @sfdtgafvdba_bot
3. Напишите: /start
4. Попробуйте создать заказ

## Решение проблем

### Бот не запускается:

```bash
# Проверка статуса
supervisorctl status basestom-bot

# Просмотр логов
supervisorctl tail -f basestom-bot

# Проверка файла .env
cat /opt/basestom-bot/src/.env

# Правильный формат .env:
BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8
OPENROUTER_API_KEY=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
```

### Ошибки зависимостей:

```bash
cd /opt/basestom-bot
source venv/bin/activate
pip install -r requirements.txt
```

### Ошибки базы данных:

```bash
cd /opt/basestom-bot/data
sqlite3 orders.db "SELECT * FROM orders ORDER BY id DESC LIMIT 5"
```

### Если нужно откатиться:

```bash
# Резервная копия базы данных
cp /opt/basestom-bot/data/orders.db /opt/basestom-bot/data/orders.db.backup

# Скачивание резервной копии на локальную машину
scp root@31.129.99.125:/opt/basestom-bot/data/orders.db.backup ./
```

## Полный список команд управления

```bash
# Запуск бота
supervisorctl start basestom-bot

# Остановка бота
supervisorctl stop basestom-bot

# Перезапуск бота
supervisorctl restart basestom-bot

# Статус бота
supervisorctl status basestom-bot

# Логи бота (в реальном времени)
supervisorctl tail -f basestom-bot

# Перезагрузка конфигурации Supervisor
supervisorctl reread
supervisorctl update
```
