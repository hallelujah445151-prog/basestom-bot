# КОМАНДЫ ДЛЯ ДЕПЛОЯ БОТА НА СЕРВЕР

## Быстрый деплой (ОДИН КОПИ-ПАСТ)

### Сервер: Linux (Ubuntu/Debian)

```bash
# 1. Подключение к серверу
ssh user@your-server-ip

# 2. Установка Python и зависимостей
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

# 3. Создание директории проекта
cd /opt
sudo git clone <your-repo-url> basestom-bot
cd basestom-bot
sudo chown -R $USER:$USER .

# 4. Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# 5. Установка зависимостей
pip install -r requirements.txt

# 6. Настройка .env файла
nano .env
# Добавить:
# BOT_TOKEN=your_bot_token
# OPENROUTER_API_KEY=your_api_key

# 7. Создание директории данных
mkdir -p data

# 8. Запуск бота
python src/bot.py
```

---

## Пошаговый деплой

### Шаг 1: Подключение к серверу
```bash
ssh user@your-server-ip
```

### Шаг 2: Установка зависимостей
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git supervisor
```

### Шаг 3: Загрузка проекта

#### Вариант A: Через Git
```bash
cd /opt
sudo git clone <your-repo-url> basestom-bot
cd basestom-bot
sudo chown -R $USER:$USER .
```

#### Вариант B: Через SCP
```bash
# С локальной машины
scp -r basestom/ user@server-ip:/opt/

# На сервере
cd /opt/basestom
```

### Шаг 4: Настройка окружения
```bash
cd /opt/basestom-bot

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate
```

### Шаг 5: Установка зависимостей
```bash
pip install -r requirements.txt
```

### Шаг 6: Настройка .env файла
```bash
# Создание файла .env
nano .env

# Содержание файла:
BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8
OPENROUTER_API_KEY=your_api_key

# Сохранить: Ctrl+O, Enter
# Выйти: Ctrl+X
```

### Шаг 7: Создание директории данных
```bash
mkdir -p data
```

### Шаг 8: Запуск бота
```bash
python src/bot.py
```

---

## Деплой с Supervisor (рекомендуется для продакшена)

### Установка Supervisor
```bash
sudo apt install -y supervisor
```

### Создание конфигурации
```bash
sudo nano /etc/supervisor/conf.d/basestom-bot.conf
```

### Содержание конфигурации:
```ini
[program:basestom-bot]
command=/opt/basestom-bot/venv/bin/python /opt/basestom-bot/src/bot.py
directory=/opt/basestom-bot
user=your-username
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
redirect_stderr=true
stdout_logfile=/var/log/supervisor/basestom-bot.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/opt/basestom-bot/venv/bin"
```

### Перезагрузка Supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start basestom-bot
```

### Управление ботом через Supervisor
```bash
# Статус
sudo supervisorctl status basestom-bot

# Старт
sudo supervisorctl start basestom-bot

# Стоп
sudo supervisorctl stop basestom-bot

# Перезапуск
sudo supervisorctl restart basestom-bot

# Логи
sudo tail -f /var/log/supervisor/basestom-bot.log
```

---

## Деплой с Systemd (альтернатива Supervisor)

### Создание service файла
```bash
sudo nano /etc/systemd/system/basestom-bot.service
```

### Содержание service файла:
```ini
[Unit]
Description=Basestom Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/basestom-bot
Environment="PATH=/opt/basestom-bot/venv/bin"
ExecStart=/opt/basestom-bot/venv/bin/python src/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Перезагрузка systemd и запуск
```bash
sudo systemctl daemon-reload
sudo systemctl enable basestom-bot
sudo systemctl start basestom-bot
```

### Управление ботом через systemd
```bash
# Статус
sudo systemctl status basestom-bot

# Старт
sudo systemctl start basestom-bot

# Стоп
sudo systemctl stop basestom-bot

# Перезапуск
sudo systemctl restart basestom-bot

# Логи
sudo journalctl -u basestom-bot -f
```

---

## Полезные команды

### Проверка работы бота
```bash
# Проверить, что процесс запущен
ps aux | grep bot.py

# Проверить логи (если запущен с сохранением в файл)
tail -f data/bot.log

# Или использовать Supervisor
sudo tail -f /var/log/supervisor/basestom-bot.log
```

### Обновление бота
```bash
cd /opt/basestom-bot

# Остановить бота
sudo supervisorctl stop basestom-bot

# Обновить код
git pull

# Обновить зависимости
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Запустить бота
sudo supervisorctl start basestom-bot
```

### Проверка логов ошибок
```bash
# Supervisor
sudo tail -100 /var/log/supervisor/basestom-bot.log | grep ERROR

# Systemd
sudo journalctl -u basestom-bot --since "1 hour ago" | grep ERROR
```

---

## Проверка соединения с Telegram

```bash
# С сервера
curl https://api.telegram.org

# Или проверка работы бота
curl https://api.telegram.org/bot8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8/getMe
```

---

## Быстрый старт (ВСЁ В ОДНОМ)

### Скопируйте и вставьте:

```bash
# Подключение
ssh user@server-ip

# Установка и запуск
cd /opt && sudo git clone <repo> basestom-bot && cd basestom-bot && sudo chown -R $USER:$USER . && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && echo "BOT_TOKEN=your_token" > .env && echo "OPENROUTER_API_KEY=your_key" >> .env && mkdir -p data && python src/bot.py
```

---

## Стратегии деплоя

### Стратегия 1: Быстрый деплой (рекомендуется)
```bash
# 1. Скопировать команды выше
# 2. Вставить в терминал
# 3. Вводить данные (IP, repo, токены)
# 4. Бот запущен!
```

### Стратегия 2: Пошаговый (для новичков)
```bash
# Выполнять команды пошагово
# Из раздела "Пошаговый деплой"
```

### Стратегия 3: Supervisor (для продакшена)
```bash
# Настроить Supervisor
# Автоматический перезапуск при падении
# Логирование
```

---

## Частые проблемы

### Проблема: ImportError
```bash
# Решение:
source venv/bin/activate
pip install -r requirements.txt
```

### Проблема: Permission denied
```bash
# Решение:
sudo chown -R $USER:$USER /opt/basestom-bot
```

### Проблема: Бот не запускается
```bash
# Решение:
# Проверить логи
sudo tail -f /var/log/supervisor/basestom-bot.log

# Проверить .env файл
cat .env
```

### Проблема: Таймаут соединения
```bash
# Решение:
# Не актуально на сервере вне РФ
# Бот должен работать стабильно
```

---

## Структура директорий на сервере

```
/opt/basestom-bot/
├── venv/                    # Виртуальное окружение
├── src/
│   ├── bot.py
│   ├── database.py
│   └── ...
├── data/                    # База данных
├── requirements.txt
├── .env                     # Конфигурация (Создайте вручную!)
└── logs/                    # Логи (если настроено)
```

---

## Резюме команд

### Минимум (для быстрого запуска):
```bash
ssh user@server
cd /opt && sudo git clone <repo> basestom-bot && cd basestom-bot && sudo chown -R $USER:$USER . && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && nano .env && mkdir -p data && python src/bot.py
```

### Рекомендовано (для продакшена):
```bash
# Установка
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git supervisor

# Деплой
cd /opt
sudo git clone <repo> basestom-bot
cd basestom-bot
sudo chown -R $USER:$USER .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nano .env  # настроить токены

# Supervisor
sudo nano /etc/supervisor/conf.d/basestom-bot.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start basestom-bot
```

---

**Дата:** 11.04.2026
**Статус:** ✅ **ГОТ К ДЕПЛОЮ**
