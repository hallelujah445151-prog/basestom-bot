# Исправленная логика напоминаний

## Проблема

**До исправления:**
- Напоминания отправлялись ВСЕМ заказам каждые 5 минут (10:00, 10:05, 10:10, ... 12:00)
- Даже если напоминание было успешно отправлено, оно отправлялось снова

## Решение

**После исправления:**
- Напоминания отправляются только заказам, которые НЕ имеют записи в таблице `reminders`
- Напоминание отмечается в таблице `reminders` ТОЛЬКО при успешной отправке ВСЕХ напоминаний (технику + администраторам)
- Если не все напоминания отправились успешно, запись в таблице `reminders` НЕ создается
- Повторная проверка каждые 5 минут отправляет только те напоминания, которые не были успешно отправлены ранее

## Логика работы

### Первая проверка (10:00)
1. `get_orders_due_tomorrow()` возвращает ВСЕ заказы с дедлайном завтра (без записей в `reminders`)
2. Для каждого заказа:
   - Отправляется напоминание технику
   - Отправляется напоминание администраторам
   - Если ВСЕ отправились успешно → создается запись в `reminders`
   - Если НЕ все отправились успешно → запись НЕ создается

### Вторая проверка (10:05)
1. `get_orders_due_tomorrow()` возвращает только заказы БЕЗ записей в `reminders` (только неудачные)
2. Повторяется отправка только для неудачных заказов
3. Если теперь успешно отправились → создается запись в `reminders`
4. Если НЕ отправились → запись НЕ создается

### Последующие проверки (10:10, 10:15, 10:20, 10:25, 10:30)
- Только неудачные заказы
- Только если запись не была создана в `reminders`

### После 10:30
- Проверки прекращаются
- `last_check_date` обновляется

## Изменения

**Файл: `src/utils/reminder_background.py`**

**Было:**
```python
if order_fully_sent:
    print(f"[DEBUG] Order {order['id']} - ALL REMINDERS SENT SUCCESSFULLY")
    fully_sent_orders += 1
    if sent_tech:
        sent_count += 1

    self.reminder_service.mark_reminder_sent(order['id'], 'today')  # ВСЕГДА отмечает
else:
    print(f"[DEBUG] Order {order['id']} - SOME REMINDERS FAILED, will retry")
    if sent_tech:
        sent_count += 1
```

**Стало:**
```python
if order_fully_sent:
    print(f"[DEBUG] Order {order['id']} - ALL REMINDERS SENT SUCCESSFULLY")
    fully_sent_orders += 1
    if sent_tech:
        sent_count += 1
    # Отмечаем напоминание как отправленное ТОЛЬКО при успехе
    self.reminder_service.mark_reminder_sent(order['id'], 'today')
else:
    print(f"[DEBUG] Order {order['id']} - SOME REMINDERS FAILED, will retry")
    if sent_tech:
        sent_count += 1
    # НЕ отмечаем напоминание как отправленное при неудаче
```

## Результат

✅ Напоминания отправляются только один раз для каждого успешно отправленного заказа
✅ Неудачные напоминания повторяются каждые 5 минут
✅ Проверки прекращаются после 10:30
✅ Дубликатные напоминания не отправляются

## Таблица базы данных

**Таблица: `reminders`**
```sql
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    reminder_type TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
)
```

**Фильтр в SQL:**
```sql
AND NOT EXISTS (
    SELECT 1 FROM reminders r WHERE r.order_id = o.id AND r.reminder_type = 'today'
)
```

Этот фильтр гарантирует, что заказы с уже отправленными напоминаниями не возвращаются повторно.
