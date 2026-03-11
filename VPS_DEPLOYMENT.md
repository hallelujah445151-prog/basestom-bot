# Как развернуть бота на VPS

## Инструкция по деплою на VPS (Linux)

### Шаг 1: Подготовка VPS

1. Подключитесь к вашему VPS по SSH:
```bash
ssh user@your-vps-ip
```

2. Обновите систему:
```bash
sudo apt update && sudo apt upgrade -y
```

3. Установите Python 3, pip, git и supervisor:
```bash
sudo apt install python3 python3-pip git supervisor -y
```

### Шаг 2: Создание проекта

1. Создайте директорию для проекта:
```bash
sudo mkdir -p /opt/basestom-bot
sudo chown $USER:$USER /opt/basestom-bot
cd /opt/basestom-bot
```

2. Склонируйте или загрузите файлы проекта:
```bash
# Если используете git:
git clone https://github.com/hallelujah44/basestom-bot.git .

# ИЛИ загрузите файлы вручную через SCP:
# scp -r basestom/* user@your-vps-ip:/opt/basestom-bot/
```

3. Создайте виртуальное окружение:
```bash
cd /opt/basestom-bot
python3 -m venv venv
source venv/bin/activate
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

### Шаг 3: Настройка переменных окружения

1. Создайте файл `.env` в папке `src/`:
```bash
nano src/.env
```

2. Добавьте следующие переменные (замените на свои токены):
```
BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8
OPENROUTER_API_KEY=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
```

3. Сохраните файл (Ctrl+O, Enter, Ctrl+X)

### Шаг 4: Настройка Supervisor для автозапуска

1. Создайте конфигурационный файл для Supervisor:
```bash
sudo nano /etc/supervisor/conf.d/basestom-bot.conf
```

2. Добавьте следующее содержимое:
```ini
[program:basestom-bot]
command=/opt/basestom-bot/venv/bin/python /opt/basestom-bot/src/bot.py
directory=/opt/basestom-bot
user=your_username
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/basestom-bot.err.log
stdout_logfile=/var/log/basestom-bot.out.log
environment=PYTHONUNBUFFERED="1"
```

**Замените `your_username` на ваше имя пользователя на VPS**

3. Сохраните файл (Ctrl+O, Enter, Ctrl+X)

4. Перезагрузите Supervisor и запустите бота:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start basestom-bot
```

### Шаг 5: Проверка работы

1. Проверьте статус бота:
```bash
sudo supervisorctl status basestom-bot
```

Должно быть: `basestom-bot                    RUNNING   pid 1234, uptime 0:00:05`

2. Посмотрите логи, если есть проблемы:
```bash
# Логи вывода
tail -f /var/log/basestom-bot.out.log

# Логи ошибок
tail -f /var/log/basestom-bot.err.log
```

3. Проверьте работу бота в Telegram:
   - Найдите бота: @sfdtgafvdba_bot
   - Напишите `/start`
   - Должно прийти приветственное сообщение

### Шаг 6: Управление ботом через Supervisor

**Запуск:**
```bash
sudo supervisorctl start basestom-bot
```

**Остановка:**
```bash
sudo supervisorctl stop basestom-bot
```

**Перезапуск:**
```bash
sudo supervisorctl restart basestom-bot
```

**Просмотр статуса:**
```bash
sudo supervisorctl status basestom-bot
```

**Просмотр логов в реальном времени:**
```bash
sudo supervisorctl tail -f basestom-bot
```

### Шаг 7: Обновление бота

При обновлении кода:

1. Обновите файлы проекта:
```bash
cd /opt/basestom-bot
git pull
# ИЛИ загрузите новые файлы вручную
```

2. Обновите зависимости (если нужно):
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

3. Перезапустите бота:
```bash
sudo supervisorctl restart basestom-bot
```

### Файлы, которые должны быть на VPS:

✅ **Обязательно:**
- `src/bot.py` - главный файл бота
- `src/database.py` - работа с базой данных
- `src/handlers/` - обработчики команд
- `src/services/` - бизнес-логика
- `src/utils/` - утилиты
- `data/references.json` - реестры врачей, техников и видов работ
- `requirements.txt` - зависимости Python
- `src/.env` - переменные окружения

❌ **Не обязательно:**
- `.replit` - конфигурация Replit (не нужна)
- `REPLIT_DEPLOYMENT.md` - инструкция для Replit (не нужна)
- `data/orders.db` - создастся автоматически
- `test_bot.py`, `test_send.py` - тестовые файлы

### Возможные проблемы:

❌ **Бот не запускается:**
```bash
# Проверьте логи
sudo supervisorctl tail basestom-bot

# Частые причины:
# - Неверный токен в .env
# - Не установлены зависимости
# - Неверный путь к Python в supervisor.conf
```

❌ **Ошибка импорта модулей:**
```bash
# Убедитесь, что находитесь в виртуальном окружении
source /opt/basestom-bot/venv/bin/activate
pip install -r requirements.txt
```

❌ **Проблемы с правами доступа:**
```bash
# Убедитесь, что пользователь имеет права на директорию
sudo chown -R your_username:your_username /opt/basestom-bot
```

### Резервное копирование:

⚠️ **ВАЖНО:** Регулярно делайте бэкап базы данных!

**Создание бэкапа:**
```bash
cp /opt/basestom-bot/data/orders.db /opt/basestom-bot/data/orders.db.backup.$(date +%Y%m%d)
```

**Восстановление из бэкапа:**
```bash
cp /opt/basestom-bot/data/orders.db.backup.YYYYMMDD /opt/basestom-bot/data/orders.db
sudo supervisorctl restart basestom-bot
```

### Мониторинг:

**Автоматический бэкап (добавьте в crontab):**
```bash
crontab -e
```

Добавьте строку для ежедневного бэкапа в 2:00 ночи:
```
0 2 * * * cp /opt/basestom-bot/data/orders.db /opt/basestom-bot/data/orders.db.backup.$(date +\%Y\%m\%d)
```

**Мониторинг ресурсов:**
```bash
htop  # Просмотр использования CPU и памяти
df -h # Просмотр дискового пространства
```

### Дополнительно:

🔒 **Безопасность:**
- Используйте сложные пароли для SSH
- Настройте Firewall (ufw)
- Регулярно обновляйте систему

📊 **Мониторинг:**
- Установите `htop` для мониторинга ресурсов
- Настройте оповещения о критических ошибках

🔄 **Автоматизация:**
- Настройте автоматический бэкап БД
- Настройте автоматическое обновление зависимостей

## Краткое резюме:

1. Установите Python, pip, git, supervisor
2. Скопируйте файлы проекта на VPS
3. Создайте виртуальное окружение и установите зависимости
4. Настройте `.env` с токенами
5. Настройте Supervisor для автозапуска
6. Запустите бота через Supervisor
7. Проверьте работу в Telegram

Готово! 🎉
