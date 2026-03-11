# 🚀 Деплой на VPS

## ✅ Готово

- ✅ GitHub обновлен (commit: d87bca9)
- ✅ Файлы деплоя созданы
- ✅ Скрипт автоматического деплоя готов

## 📦 Файлы для деплоя

1. **`deploy-to-vps.bat`** - Скрипт для Windows (двойной клик)
2. **`deploy-to-vps.sh`** - Скрипт для Linux/Mac
3. **`VPS_DEPLOYMENT.md`** - Полная инструкция по деплою

## 🚀 Быстрый старт

### Способ 1: Автоматический (рекомендуется)

**На Windows:**
```cmd
cd C:\Users\crush\AppData\Roaming\projects\basestom
deploy-to-vps.bat
```

**На Linux/Mac:**
```bash
cd C:\Users\crush\AppData\Roaming\projects\basestom
bash deploy-to-vps.sh
```

**Что делает скрипт:**
1. ✅ Создает архив проекта
2. ✅ Загружает на VPS через SCP
3. ✅ Устанавливает зависимости на VPS
4. ✅ Настраивает Supervisor
5. ✅ Запускает бота

**Требуется:**
- Проверьте, что файл `src/.env` существует с токенами
- При запросе введите пароль: `&PJc52K5gNG4`

### Способ 2: Вручную

Если автоматический скрипт не работает, следуйте инструкциям:

**1. Подключитесь к VPS:**
```bash
ssh root@31.129.99.125
# Пароль: &PJc52K5gNG4
```

**2. Установите зависимости:**
```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip git supervisor
```

**3. Скачайте проект с GitHub:**
```bash
cd /opt
git clone https://github.com/hallelujah445151-prog/basestom-bot.git
cd basestom-bot
```

**4. Создайте виртуальное окружение и установите зависимости:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**5. Создайте файл `.env` в папке `src/`:**
```bash
nano src/.env
```

Добавьте:
```
BOT_TOKEN=8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8
OPENROUTER_API_KEY=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
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

**6. Настройте Supervisor:**
```bash
sed 's/your_username/root/g' supervisor.conf > /etc/supervisor/conf.d/basestom-bot.conf
supervisorctl reread
supervisorctl update
supervisorctl start basestom-bot
```

**7. Проверьте статус:**
```bash
supervisorctl status basestom-bot
```

## ✅ Проверка работы

После деплоя проверьте бота в Telegram:
1. Найдите бота: `@sfdtgafvdba_bot`
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

# Логи ошибок
tail -f /var/log/basestom-bot.err.log

# Логи вывода
tail -f /var/log/basestom-bot.out.log
```

## 📊 Мониторинг

**Просмотр ресурсов:**
```bash
htop  # Установка: apt install htop
df -h # Дисковое пространство
```

**Логи:**
```bash
# Последние 50 строк логов
supervisorctl tail -n 50 basestom-bot
```

## 🔐 Данные VPS

- **IP:** 31.129.99.125
- **Логин:** root
- **Пароль:** &PJc52K5gNG4
- **Проект:** /opt/basestom-bot

## 🔄 Обновление бота

**Автоматическое:**
```cmd
cd C:\Users\crush\AppData\Roaming\projects\basestom
deploy-to-vps.bat
```

**Вручную на VPS:**
```bash
cd /opt/basestom-bot
git pull
supervisorctl restart basestom-bot
```

## 📞 Поддержка

Если возникли проблемы:

1. **Проверьте логи:** `supervisorctl tail -f basestom-bot`
2. **Проверьте статус:** `supervisorctl status basestom-bot`
3. **Проверьте подключение:** `ping 31.129.99.125`
4. **Попробуйте перезапустить:** `supervisorctl restart basestom-bot`

## 📝 Что было сделано

- ✅ GitHub обновлен (commit d87bca9)
- ✅ Созданы файлы деплоя:
  - `deploy-to-vps.bat` - скрипт для Windows
  - `deploy-to-vps.sh` - скрипт для Linux/Mac
  - `VPS_DEPLOYMENT.md` - инструкция
  - `DEPLOYMENT_FILES.md` - список файлов
  - `supervisor.conf` - конфиг Supervisor
  - `.gitignore` - Git исключения
  - `.env.example` - пример переменных
  - `README.md` - обновлена документация

## 🎉 Готово к деплою!

Запустите `deploy-to-vps.bat` для автоматического деплоя.
