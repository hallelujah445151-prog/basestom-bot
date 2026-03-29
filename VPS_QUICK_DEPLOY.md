# ⚡ Быстрое развертывание на VPS

## 🚀 3 шага для запуска бота на VPS

### Шаг 1: Подключитесь к VPS

Откройте терминал (PowerShell или CMD) и выполните:

```bash
ssh root@31.129.99.125
```

**Пароль:** `&PJc52K5gNG4`

### Шаг 2: Скачайте и запустите скрипт

После подключения к VPS выполните:

```bash
cd /opt
curl -o install.sh https://raw.githubusercontent.com/hallelujah445151-prog/basestom-bot/master/install-on-vps.sh
chmod +x install.sh
bash install.sh
```

Или вручную скопируйте содержимое файла `install-on-vps.sh` с вашего компьютера.

### Шаг 3: Проверьте работу бота

1. Найдите бота в Telegram: `@sfdtgafvdba_bot`
2. Напишите `/start`
3. Должно прийти приветственное сообщение

---

## ✅ После развертывания

### Проверка статуса:
```bash
supervisorctl status basestom-bot
```

### Просмотр логов:
```bash
supervisorctl tail -f basestom-bot
```

### Управление ботом:
```bash
# Рестарт
supervisorctl restart basestom-bot

# Остановка
supervisorctl stop basestom-bot

# Запуск
supervisorctl start basestom-bot
```

---

## 🔧 Если что-то не работает

### Проверьте логи:
```bash
tail -100 /var/log/basestom-bot.err.log
```

### Протестируйте запуск вручную:
```bash
cd /opt/basestom-bot
source venv/bin/activate
timeout 5 python src/bot.py
```

### Переустановите зависимости:
```bash
cd /opt/basestom-bot
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## 📞 Поддержка

Если возникнут проблемы:
- Проверьте: [VPS_DEPLOY_MANUAL.md](VPS_DEPLOY_MANUAL.md)
- Логи: `supervisorctl tail -f basestom-bot`
- Email: hallelujah445151@gmail.com

---

**Готово!** Бот будет работать на VPS 24/7 🎉
