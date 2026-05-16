# Руководство по деплою на сервер

## Метод 1: Автоматический деплой (одна команда)

### Windows:
```powershell
cd C:\Users\crush\AppData\Roaming\projects\basestom
.\deploy.bat
```

### Linux/Mac:
```bash
cd ~/projects/basestom
chmod +x deploy.sh
./deploy.sh
```

## Метод 2: Ручной деплой (пошагово)

### 1. Подключение к серверу
```bash
ssh root@31.129.99.125
```

### 2. Перейти в директорию бота
```bash
cd /opt/basestom-bot
```

### 3. Обновление кода
```bash
git pull
```

### 4. Активация виртуального окружения
```bash
source venv/bin/activate
```

### 5. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 6. Перезапуск бота
```bash
supervisorctl restart basestom-bot
```

### 7. Проверка статуса
```bash
supervisorctl status basestom-bot
```

## Управление ботом на сервере

### Проверить статус:
```bash
supervisorctl status basestom-bot
```

### Запустить бота:
```bash
supervisorctl start basestom-bot
```

### Остановить бота:
```bash
supervisorctl stop basestom-bot
```

### Перезапустить бота:
```bash
supervisorctl restart basestom-bot
```

### Посмотреть логи:
```bash
supervisorctl tail -f basestom-bot
```

## Проверка после деплоя

1. Откройте Telegram
2. Найдите бота: @sfdtgafvdba_bot
3. Напишите: /start
4. Попробуйте создать заказ: "Плюхин металлокерамика 2шт пациент Иванов"

## Решение проблем

### Если бот не отвечает:
```bash
# Проверить статус
supervisorctl status basestom-bot

# Посмотреть логи
supervisorctl tail -f basestom-bot

# Перезапустить
supervisorctl restart basestom-bot
```

### Если ошибки зависимостей:
```bash
cd /opt/basestom-bot
source venv/bin/activate
pip install -r requirements.txt
```

### Если база данных не работает:
```bash
cd /opt/basestom-bot/data
sqlite3 orders.db "SELECT * FROM orders ORDER BY id DESC LIMIT 5"
```

## Файлы на сервере

### Конфигурация Supervisor:
```
/etc/supervisor/conf.d/basestom-bot.conf
```

### Логи:
```
/var/log/supervisor/basestom-bot-*.log
```

### База данных:
```
/opt/basestom-bot/data/orders.db
```

### Файл с токенами:
```
/opt/basestom-bot/src/.env
```

## Резервное копирование

```bash
# Создать резервную копию базы данных
cp /opt/basestom-bot/data/orders.db /opt/basestom-bot/data/orders.db.backup.$(date +%Y%m%d_%H%M%S)

# Скачать резервную копию на локальную машину
scp root@31.129.99.125:/opt/basestom-bot/data/orders.db.backup.* /local/backup/path/
```

## Быстрая проверка изменений

После изменения кода локально:

1. Закоммитить изменения:
```bash
git add .
git commit -m "Описание изменений"
git push
```

2. На сервере:
```bash
cd /opt/basestom-bot
git pull
supervisorctl restart basestom-bot
```
