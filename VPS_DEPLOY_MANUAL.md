# 🚀 Развертывание бота на VPS

## ✅ Текущий статус

- ✅ Все изменения закоммичены
- ✅ VPS доступен (31.129.99.125)
- ✅ Скрипты развертывания готовы
- ⚠️ Требуется ручное развертывание (SSH требует пароль)

## 📋 Данные VPS

- **IP:** 31.129.99.125
- **Логин:** root
- **Пароль:** &PJc52K5gNG4
- **Проект:** /opt/basestom-bot

## 🚀 Пошаговая инструкция

### Способ 1: Автоматический (рекомендуется)

**На Windows:**
```cmd
cd C:\Users\crush\AppData\Roaming\projects\basestom
deploy-to-vps.bat
```

**Введите пароль:** &PJc52K5gNG4

### Способ 2: Вручную через терминал

**Шаг 1: Подключитесь к VPS**
```bash
ssh root@31.129.99.125
# Пароль: &PJc52K5gNG4
```

**Шаг 2: Обновите систему**
```bash
apt update && apt upgrade -y
```

**Шаг 3: Установите зависимости**
```bash
apt install -y python3 python3-pip python3-venv git supervisor
```

**Шаг 4: Удалите старый проект (если есть)**
```bash
rm -rf /opt/basestom-bot
```

**Шаг 5: Клонируйте проект с GitHub**
```bash
cd /opt
git clone https://github.com/hallelujah445151-prog/basestom-bot.git
cd basestom-bot
```

**Шаг 6: Создайте файл .env**
```bash
nano src/.env
```

Вставьте:
```
BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8
OPENROUTER_API_KEY=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
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

**Шаг 7: Создайте виртуальное окружение**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Шаг 8: Установите зависимости**
```bash
pip install -r requirements.txt
```

**Шаг 9: Настройте Supervisor**
```bash
cat supervisor.conf | sed 's|your_username|root|g' > /etc/supervisor/conf.d/basestom-bot.conf
supervisorctl reread
supervisorctl update
```

**Шаг 10: Создайте логи**
```bash
touch /var/log/basestom-bot.out.log /var/log/basestom-bot.err.log
chmod 644 /var/log/basestom-bot.*.log
```

**Шаг 11: Запустите бота**
```bash
supervisorctl start basestom-bot
```

**Шаг 12: Проверьте статус**
```bash
supervisorctl status basestom-bot
```

## ✅ Проверка работы

1. Найдите бота в Telegram: `@sfdtgafvdba_bot`
2. Напишите `/start`
3. Должно прийти приветственное сообщение

## 🔧 Управление ботом

**На VPS:**
```bash
# Запуск
supervisorctl start basestom-bot

# Остановка
supervisorctl stop basestom-bot

# Рестарт
supervisorctl restart basestom-bot

# Статус
supervisorctl status basestom-bot

# Логи в реальном времени
supervisorctl tail -f basestom-bot

# Посмотреть последние 50 строк логов
supervisorctl tail -n 50 basestom-bot

# Логи ошибок
tail -f /var/log/basestom-bot.err.log

# Логи вывода
tail -f /var/log/basestom-bot.out.log
```

## 🔄 Обновление бота

**Способ 1: Через GitHub**
```bash
cd /opt/basestom-bot
git pull
supervisorctl restart basestom-bot
```

**Способ 2: Скрипт с Windows**
```cmd
cd C:\Users\crush\AppData\Roaming\projects\basestom
deploy-to-vps.bat
```

## 🔍 Диагностика проблем

**Бот не запускается:**
```bash
# Проверьте статус
supervisorctl status basestom-bot

# Проверьте логи
supervisorctl tail -n 100 basestom-bot

# Проверьте ошибки
cat /var/log/basestom-bot.err.log

# Проверьте наличие файлов
ls -la /opt/basestom-bot/src/bot.py
ls -la /opt/basestom-bot/venv/bin/python

# Протестируйте запуск вручную
cd /opt/basestom-bot
source venv/bin/activate
timeout 5 python src/bot.py
```

**Проблемы с зависимостями:**
```bash
cd /opt/basestom-bot
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 📊 Мониторинг ресурсов

```bash
# Использование CPU и памяти
htop

# Дисковое пространство
df -h

# Память
free -m
```

## 🎉 Что было сделано

### Изменения в коде:

1. ✅ **`/report_period` исправлен**
   - Создан ConversationHandler
   - Правильное управление состояниями
   - Фикс с возвратом состояний

2. ✅ **Нечеткое сопоставление имен**
   - Добавлен `difflib.get_close_matches()`
   - AI ошибки в именах теперь исправляются
   - Врач "Гаспарйанидзе" найдет "Гаспарянидзе"

3. ✅ **Улучшенные уведомления админа**
   - Показывает, кому отправлено
   - Показывает, кому НЕ отправлено и почему
   - Подробная информация о статусе

4. ✅ **Background task включен**
   - Напоминания работают каждый день 9:50-10:30
   - Автоматическая проверка заказов
   - Уведомления техникам и админам

5. ✅ **Улучшена обработка ошибок**
   - Автоматический retry при ошибках сети
   - Increased timeout to 180 seconds
   - Graceful shutdown

### Структура проекта:

```
basestom-bot/
├── src/
│   ├── bot.py                    # Главный файл бота
│   ├── database.py               # База данных
│   ├── handlers/
│   │   ├── registration.py       # Регистрация
│   │   ├── admin.py             # Админ-панель
│   │   ├── orders.py            # Заказы
│   │   ├── reports.py           # Отчеты
│   │   └── change_role.py       # Изменение роли
│   ├── services/
│   │   ├── user_manager.py      # Управление пользователями
│   │   ├── notification_service.py  # Уведомления
│   │   ├── message_processor.py  # AI обработка
│   │   ├── report_service.py   # Отчеты
│   │   └── reminder_service.py  # Напоминания
│   └── utils/
│       └── reminder_background.py # Фоновые задачи
├── data/
│   └── orders.db               # База данных SQLite
├── supervisor.conf             # Конфигурация Supervisor
├── deploy-to-vps.bat          # Скрипт деплоя Windows
└── requirements.txt           # Зависимости
```

## 💡 Поддерживаемые команды

### Общие команды:
- `/start` - Запуск бота
- `/register` - Регистрация
- `/help` - Справка

### Для администратора:
- `/neworder` - Создать заказ
- `/admin` - Админ-панель
- `/report_doctors` - Отчет по врачам
- `/report_technicians` - Отчет по техникам
- `/report_work_types` - Отчет по видам работ
- `/report_period` - Отчет за период
- `/admin_secret endurance` - Назначить админа

## 🔐 Безопасность

- **BOT_TOKEN** уже в `.env` на VPS
- **ADMIN_SECRET_CODE** установлен как "endurance"
- SSH доступ защищен паролем
- Supervisor автоматически перезапускает бота

## 📞 Поддержка

Если возникнут проблемы:

1. **Проверьте логи:** `supervisorctl tail -f basestom-bot`
2. **Проверьте статус:** `supervisorctl status basestom-bot`
3. **Перезапустите:** `supervisorctl restart basestom-bot`
4. **Свяжитесь с разработчиком:** hallelujah445151@gmail.com

---

**Готово к развертыванию!** 🚀

Следуйте инструкции выше для развертывания на VPS.
