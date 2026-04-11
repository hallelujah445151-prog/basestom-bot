# БЫСТРЫЕ КОМАНДЫ ДЛЯ ОБНОВЛЕНИЯ БОТА

## Быстрое обновление (ОДНА КОМАНДА)

### С локальной машины:
```bash
scp src/services/dental_terminology_service.py src/services/message_processor.py user@server:/opt/asestom-bot/src/services/ && ssh user@server "cd /opt/asestom-bot && sudo supervisorctl restart basestom-bot"
```

---

## Пошаговые команды (если нужно больше контроля)

### 1. Подключение:
```bash
ssh user@your-server-ip
```

### 2. Переход:
```bash
cd /opt/asestom-bot/src/services
```

### 3. Бекап:
```bash
cp dental_terminology_service.py dental_terminology_service.py.backup
cp message_processor.py message_processor.py.backup
```

### 4. Синтаксис:
```bash
python -m py_compile dental_terminology_service.py
python -m py_compile message_processor.py
```

### 5. Перезапуск:
```bash
sudo supervisorctl restart basestom-bot
```

### 6. Логи:
```bash
sudo tail -f /var/log/supervisor/asestom-bot.log
```

---

## Список чеклист

### Быстрый чеклист:
- [ ] Обновить dental_terminology_service.py
- [ ] Обновить message_processor.py
- [ ] Проверить синтаксис
- [ ] Перезапустить бота
- [ ] Проверить логи
- [ ] Протестировать работу

---

## Обновленные файлы

1. ✅ `src/services/dental_terminology_service.py` - убран timeout
2. ✅ `src/services/message_processor.py` - убран timeout

---

## Статус

| Действие | Статус |
|----------|--------|
| Исправление ошибки | ✅ DONE |
| Синтаксис | ✅ PASS |
| Обновление | ОЖИДАЕТ |

---

**Дата:** 11.04.2026
**Статус:** ✅ **ГОТ К ОБНОВЛЕНИЮ**
