# 📦 Файлы для деплоя на VPS

## ✅ Обязательные файлы (должны быть на сервере)

### 📂 Корневая директория
```
basestom-bot/
├── requirements.txt           # Зависимости Python
├── VPS_DEPLOYMENT.md         # Инструкция по деплою на VPS
├── supervisor.conf           # Конфигурация Supervisor (копировать в /etc/supervisor/conf.d/)
└── deploy.sh                 # Скрипт автоматической установки (опционально)
```

### 📂 src/
```
src/
├── bot.py                    # Главный файл бота
├── database.py               # Работа с SQLite базой данных
├── .env                      # Переменные окружения (токены)
├── handlers/                 # Обработчики команд
│   ├── registration.py       # Регистрация пользователей
│   ├── admin.py              # Админ-панель диспетчера
│   ├── orders.py             # Обработка заказов
│   ├── reports.py            # Обработка запросов отчетов
│   └── change_role.py        # Смена роли для тестирования
├── services/                 # Бизнес-логика
│   ├── user_manager.py       # Управление пользователями
│   ├── reference_manager.py  # Управление реестрами
│   ├── message_processor.py  # ИИ обработка сообщений
│   ├── notification_service.py # Отправка уведомлений
│   ├── reminder_service.py   # Проверка сроков выполнения заказов
│   └── report_service.py     # Сбор статистики и отчетов
└── utils/                    # Утилиты
    └── reminder_background.py # Фоновый процесс напоминаний
```

### 📂 data/
```
data/
├── references.json           # Реестры врачей, техников и видов работ
└── orders.db                # База данных заказов (создается автоматически)
```

---

## ❌ НЕ нужны для деплоя

### 🗑️ Можно удалить или не загружать:
```
├── .replit                  # Конфигурация Replit (нужна только для Replit)
├── REPLIT_DEPLOYMENT.md     # Инструкция для Replit (нужна только для Replit)
├── test_bot.py              # Тестовый файл
├── test_send.py             # Тестовый файл
├── AGENTS.md                # Документация для ИИ агента
└── references.md            # Требования к проекту (архивный файл)
```

---

## 📋 Порядок действий для деплоя

### 1. Подготовка файлов на локальной машине

1. Убедитесь, что в `src/.env` есть токены:
   ```env
   BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8
   OPENROUTER_API_KEY=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
   ```

2. Убедитесь, что `data/references.json` существует

### 2. Загрузка файлов на VPS

**Вариант А: Через SCP (загрузка с локальной машины)**
```bash
# С локальной Windows машины:
scp -r basestom/* user@your-vps-ip:/tmp/basestom-bot/

# С локальной Linux/Mac машины:
scp -r basestom/* user@your-vps-ip:/tmp/basestom-bot/
```

**Вариант Б: Через Git (загрузка из репозитория)**
```bash
# На VPS:
git clone https://github.com/hallelujah44/basestom-bot.git /tmp/basestom-bot
```

**Вариант В: Создать архив и загрузить**
```bash
# На локальной машине (в папке basestom):
tar -czf basestom-bot.tar.gz \
  requirements.txt \
  VPS_DEPLOYMENT.md \
  supervisor.conf \
  deploy.sh \
  src/ \
  data/references.json

# Загрузите archive на VPS через SCP или SFTP
```

### 3. Настройка на VPS

```bash
# Подключитесь к VPS
ssh user@your-vps-ip

# Переместите файлы в нужную директорию
sudo mkdir -p /opt/basestom-bot
sudo mv /tmp/basestom-bot/* /opt/basestom-bot/
sudo chown -R $USER:$USER /opt/basestom-bot

# Продолжите по инструкции в VPS_DEPLOYMENT.md
cd /opt/basestom-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создайте .env, если его нет
nano src/.env
# Добавьте токены

# Настройте Supervisor
sudo cp supervisor.conf /etc/supervisor/conf.d/basestom-bot.conf
sudo sed -i "s/your_username/$(whoami)/g" /etc/supervisor/conf.d/basestom-bot.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start basestom-bot
```

---

## 🔍 Проверка структуры файлов

### На VPS после развертывания:

```bash
# Проверьте структуру файлов
ls -la /opt/basestom-bot/
# Должно быть:
# requirements.txt
# VPS_DEPLOYMENT.md
# supervisor.conf
# deploy.sh (опционально)
# src/
# data/

ls -la /opt/basestom-bot/src/
# Должно быть:
# bot.py
# database.py
# .env
# handlers/
# services/
# utils/

ls -la /opt/basestom-bot/data/
# Должно быть:
# references.json
# orders.db (создается автоматически)
```

---

## 📊 Размеры файлов (ориентировочно)

- `src/` - ~50-100 KB (весь код)
- `data/references.json` - ~1 KB
- `requirements.txt` - ~1 KB
- `VPS_DEPLOYMENT.md` - ~10 KB
- `supervisor.conf` - ~1 KB

**Итого:** ~60-120 KB (без БД)

---

## 🔐 Безопасность

⚠️ **ВАЖНО:** Файл `.env` содержит секретные токены!

1. **НЕ коммитить** `.env` в публичный репозиторий
2. **НЕ передавать** `.env` через незащищенные каналы
3. Создать `.env.example` без токенов для публичного доступа:
   ```env
   BOT_TOKEN=your_bot_token_here
   OPENROUTER_API_KEY=your_api_key_here
   ```

### .gitignore (добавьте в проект):

```gitignore
# Секреты
.env

# Python
__pycache__/
*.pyc
venv/
.venv/

# База данных
data/orders.db

# Логи
*.log

# IDE
.vscode/
.idea/

# Тестовые файлы
test_bot.py
test_send.py
```

---

## 🔄 Обновление бота

### При обновлении кода:

1. Обновите файлы на VPS:
   ```bash
   cd /tmp/basestom-bot
   git pull  # ИЛИ загрузите новые файлы через SCP
   ```

2. Скопируйте обновленные файлы:
   ```bash
   cp -r /tmp/basestom-bot/* /opt/basestom-bot/
   ```

3. Обновите зависимости (если нужно):
   ```bash
   cd /opt/basestom-bot
   source venv/bin/activate
   pip install -r requirements.txt --upgrade
   ```

4. Перезапустите бота:
   ```bash
   sudo supervisorctl restart basestom-bot
   ```

---

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи: `sudo supervisorctl tail -f basestom-bot`
2. Проверьте статус: `sudo supervisorctl status basestom-bot`
3. Смотрите `VPS_DEPLOYMENT.md` для подробной инструкции
