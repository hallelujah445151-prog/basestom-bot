# КОМАНДЫ ДЛЯ ОБНОВЛЕНИЯ БОТА НА СЕРВЕРЕ

## Быстрое обновление (С ЛОКАЛЬНОЙ МАШИНЫ)

### Шаг 1: Подключение к серверу
```bash
ssh user@your-server-ip
```

### Шаг 2: Переход в директорию проекта
```bash
cd /opt/basestom-bot
```

### Шаг 3: Обновление файлов

#### Вариант A: Через SCP (рекомендуется)

```bash
# С локальной машины (новое окно терминала)
scp src/services/dental_terminology_service.py user@server:/opt/basestom-bot/src/services/
scp src/services/message_processor.py user@server:/opt/basestom-bot/src/services/
```

#### Вариант B: Через git

```bash
# Если используете git
git pull
```

#### Вариант C: Ручное копирование (если нет git)

```bash
# С локальной машины скопируйте содержимое файлов
# Затем на сервере:
nano src/services/dental_terminology_service.py
# Вставьте новое содержимое
# Ctrl+O для сохранения
# Ctrl+X для выхода

# Повторите для message_processor.py
```

### Шаг 4: Перезапуск бота

```bash
# Если используете Supervisor
sudo supervisorctl restart basestom-bot

# Или если systemd
sudo systemctl restart basestom-bot

# Или если запущен вручную
# Найдите процесс и убейте его
pkill -f bot.py
# Затем запустите заново
python src/bot.py
```

---

## Одной командой (Быстрый способ)

### С локальной машины:
```bash
scp src/services/dental_terminology_service.py src/services/message_processor.py user@server:/opt/basestom-bot/src/services/ && ssh user@server "cd /opt/basestom-bot && sudo supervisorctl restart basestom-bot"
```

---

## Пошаговое обновление (НА СЕРВЕРЕ)

### Шаг 1: Проверка текущих файлов
```bash
# На сервере
cd /opt/basestom-bot
head -50 src/services/dental_terminology_service.py
```

### Шаг 2: Создание бекапа (рекомендуется)
```bash
# На сервере
cd /opt/basestom-bot
cp src/services/dental_terminology_service.py src/services/dental_terminology_service.py.backup
cp src/services/message_processor.py src/services/message_processor.py.backup
```

### Шаг 3: Обновление dental_terminology_service.py
```bash
nano src/services/dental_terminology_service.py

# Замените содержимое на новое
# Ctrl+O для сохранения
# Ctrl+X для выхода
```

Или через cat (если у вас есть файлы на сервере):
```bash
cat > src/services/dental_terminology_service.py << 'EOF'
# Вставьте новое содержимое файла сюда
EOF
```

### Шаг 4: Обновление message_processor.py
```bash
nano src/services/message_processor.py

# Замените содержимое на новое
# Ctrl+O для сохранения
# Ctrl+X для выхода
```

### Шаг 5: Проверка синтаксиса
```bash
python -m py_compile src/services/dental_terminology_service.py
python -m py_compile src/services/message_processor.py

echo "Синтаксис проверен успешно!"
```

### Шаг 6: Перезапуск бота

```bash
# Supervisor
sudo supervisorctl restart basestom-bot

# Проверить статус
sudo supervisorctl status basestom-bot

# Посмотреть логи
sudo tail -f /var/log/supervisor/basestom-bot.log
```

---

## Обновление через Git (ПРОЩЕ)

### Если используете git на сервере:

```bash
# 1. На локальной машине
git add src/services/dental_terminology_service.py
git add src/services/message_processor.py
git commit -m "Улучшение ИИ обработки текста с стоматологической терминологией"
git push

# 2. На сервере
cd /opt/basestom-bot
git pull
sudo supervisorctl restart basestom-bot
```

---

## Обновление через Docker (ЕСЛИ ИСПОЛЬЗУЕТЕ)

```bash
# 1. Скопируйте файлы в docker-директорию
docker cp src/services/dental_terminology_service.py basestom-bot:/app/src/services/
docker cp src/services/message_processor.py basestom-bot:/app/src/services/

# 2. Перезапустите контейнер
docker restart basestom-bot

# Или пересоздайте образ
docker-compose down
docker-compose up -d --build
```

---

## Проверка работы

### 1. Проверьте логи
```bash
# Supervisor
sudo tail -50 /var/log/supervisor/basestom-bot.log

# Systemd
sudo journalctl -u basestom-bot --since "5 minutes ago"
```

### 2. Протестируйте бота
```
1. Найдите бота в Telegram
2. Нажмите /start
3. Создайте тестовый заказ:
   "Иванов циркон на винте 7шт пациент Петров"
4. Проверьте, что ИИ правильно обработал текст
```

---

## Откат изменений (ЕСЛИ НУЖНО)

### Если что-то пошло не так:

```bash
# Восстановление из бекапа
cp src/services/dental_terminology_service.py.backup src/services/dental_terminology_service.py
cp src/services/message_processor.py.backup src/services/message_processor.py

# Перезапуск бота
sudo supervisorctl restart basestom-bot
```

---

## Быстрый чеклист

### Для локальной машины:
- [ ] Скопировать файлы с локальной машины
- [ ] Подключиться к серверу
- [ ] Обновить dental_terminology_service.py
- [ ] Обновить message_processor.py
- [ ] Проверить синтаксис
- [ ] Перезапустить бота
- [ ] Проверить логи
- [ ] Протестировать работу

### Для сервера:
- [ ] Создать бекап файлов
- [ ] Обновить файлы
- [ ] Проверить синтаксис
- [ ] Перезапустить бота
- [ ] Проверить логи
- [ ] Протестировать работу

---

## Полезные команды

### Проверка работы бота
```bash
# Проверить, запущен ли процесс
ps aux | grep bot.py

# Проверить статус
sudo supervisorctl status basestom-bot

# Посмотреть последние 100 строк лога
sudo tail -100 /var/log/supervisor/basestom-bot.log
```

### Мониторинг
```bash
# Посмотреть логи в реальном времени
sudo tail -f /var/log/supervisor/basestom-bot.log

# Фильтрация ошибок
sudo tail -f /var/log/supervisor/basestom-bot.log | grep ERROR
```

---

## Сравнение файлов

### Чтобы убедиться, что файлы обновлены:

```bash
# На сервере
cd /opt/basestom-bot/src/services

# Проверить дату изменения файла
ls -la dental_terminology_service.py
ls -la message_processor.py

# Проверить размер файла
wc -l dental_terminology_service.py
wc -l message_processor.py

# Посмотреть первые строки
head -30 dental_terminology_service.py
head -30 message_processor.py
```

---

## Статистика обновления

### Файлов обновлено: 2
### Директория: src/services/
### Сервис: basestom-bot
### Метод: SCP/Manual

---

## Рекомендации

### Для быстрого обновления:
1. ✅ Используйте SCP для копирования файлов
2. ✅ Создавайте бекап перед обновлением
3. ✅ Проверяйте синтаксис после обновления
4. ✅ Перезапускайте бота через Supervisor
5. ✅ Проверяйте логи после обновления

### Для стабильности:
1. ✅ Протестируйте локально перед обновлением на сервере
2. ✅ Используйте git для отслеживания изменений
3. ✅ Делайте бекапы перед обновлениями
4. ✅ Следите за логами после обновления

---

## Полные команды для копирования

### С локальной машины (Windows):
```powershell
# PowerShell
scp src\services\dental_terminology_service.py user@server:/opt/basestom-bot/src/services/
scp src\services\message_processor.py user@server:/opt/basestom-bot/src/services/
```

### С локальной машины (Linux/Mac):
```bash
# Bash
scp src/services/dental_terminology_service.py user@server:/opt/basestom-bot/src/services/
scp src/services/message_processor.py user@server:/opt/basestom-bot/src/services/
```

### После копирования (на сервере):
```bash
ssh user@server "cd /opt/basestom-bot && sudo supervisorctl restart basestom-bot"
```

---

## Итог

### Самый быстрый способ:
```bash
# ОДНА КОМАНДА:
scp src/services/dental_terminology_service.py src/services/message_processor.py user@server:/opt/basestom-bot/src/services/ && ssh user@server "cd /opt/basestom-bot && sudo supervisorctl restart basestom-bot"
```

### Файлов для обновления:
1. `src/services/dental_terminology_service.py`
2. `src/services/message_processor.py`

---

**Дата:** 11.04.2026
**Статус:** ✅ **ГОТ К ОБНОВЛЕНИЮ**
