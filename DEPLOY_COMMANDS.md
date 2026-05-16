# Команды для деплоя на сервер

## Быстрый деплой (одна команда)

### Windows (PowerShell)
```powershell
cd C:\Users\crush\AppData\Roaming\projects\basestom
.\deploy-to-vps.bat
```

### Linux/Mac (Bash)
```bash
cd ~/projects/basestom
./deploy-to-vps.sh
```

## Ручной деплой (по шагам)

### 1. Подключение к VPS
```bash
ssh root@31.129.99.125
```

### 2. Обновление кода
```bash
cd /opt/basestom-bot
git pull
```

### 3. Активация виртуального окружения
```bash
cd /opt/basestom-bot
source venv/bin/activate
```

### 4. Обновление зависимостей
```bash
pip install -r requirements.txt
```

### 5. Перезапуск бота через Supervisor
```bash
# Рестарт бота
supervisorctl restart basestom-bot

# Или остановка и запуск
supervisorctl stop basestom-bot
supervisorctl start basestom-bot
```

## Управление ботом на VPS

### Статус бота
```bash
supervisorctl status basestom-bot
```

### Запуск бота
```bash
supervisorctl start basestom-bot
```

### Остановка бота
```bash
supervisorctl stop basestom-bot
```

### Рестарт бота
```bash
supervisorctl restart basestom-bot
```

### Просмотр логов (в реальном времени)
```bash
supervisorctl tail -f basestom-bot
```

### Перезагрузка конфигурации Supervisor
```bash
supervisorctl reread
supervisorctl update
```

## Полный список команд деплоя

### Windows (PowerShell)
```powershell
# 1. Заливка файлов на VPS
scp basestom-bot-deploy.tar.gz root@31.129.99.125:/tmp/

# 2. Подключение к VPS
ssh root@31.129.99.125

# 3. Распаковка и установка
cd /opt/basestom-bot
tar -xzf /tmp/basestom-bot-deploy.tar.gz
rm /tmp/basestom-bot-deploy.tar.gz

# 4. Активация виртуального окружения
source venv/bin/activate

# 5. Обновление зависимостей
pip install -r requirements.txt

# 6. Рестарт бота
supervisorctl restart basestom-bot

# 7. Проверка статуса
supervisorctl status basestom-bot
```

### Linux/Mac (Bash)
```bash
# 1. Подключение к VPS
ssh root@31.129.99.125

# 2. Обновление кода
cd /opt/basestom-bot
git pull

# 3. Активация виртуального окружения
source venv/bin/activate

# 4. Обновление зависимостей
pip install -r requirements.txt

# 5. Рестарт бота
supervisorctl restart basestom-bot

# 6. Проверка статуса
supervisorctl status basestom-bot
```

## Проверка работы бота

После деплоя:

1. Откройте Telegram
2. Найдите бота: @sfdtgafvdba_bot
3. Напишите /start
4. Попробуйте создать заказ: "Плюхин металлокерамика 2шт пациент Иванов"

## Решение проблем

### Бот не отвечает
```bash
# Проверка статуса
supervisorctl status basestom-bot

# Просмотр логов
supervisorctl tail -f basestom-bot

# Рестарт
supervisorctl restart basestom-bot
```

### Ошибки зависимостей
```bash
cd /opt/basestom-bot
source venv/bin/activate
pip install -r requirements.txt
```

### Ошибки базы данных
```bash
cd /opt/basestom-bot/data
sqlite3 orders.db "SELECT * FROM orders ORDER BY id DESC LIMIT 5"
```

## Настройка переменных окружения

Если нужно изменить токен или API ключ:

1. Подключитесь к VPS
2. Отредактируйте файл .env:
```bash
nano /opt/basestom-bot/src/.env
```

3. Измените необходимые значения:
```
BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8
OPENROUTER_API_KEY=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
```

4. Сохраните файл (Ctrl+O, Enter)
5. Выйдите из редактора (Ctrl+X)

6. Рестарт бота:
```bash
supervisorctl restart basestom-bot
```

## Важные файлы

### Supervisor конфигурация
```bash
/etc/supervisor/conf.d/basestom-bot.conf
```

### Логи бота
```bash
/var/log/supervisor/basestom-bot-*.log
```

### База данных
```bash
/opt/basestom-bot/data/orders.db
```

### Токены и ключи
```bash
/opt/basestom-bot/src/.env
```

## Резервное копирование базы данных

```bash
# Создание резервной копии
cp /opt/basestom-bot/data/orders.db /opt/basestom-bot/data/orders.db.backup.$(date +%Y%m%d_%H%M%S)

# Скачивание резервной копии на локальную машину
scp root@31.129.99.125:/opt/basestom-bot/data/orders.db.backup.* /local/backup/path/
```
