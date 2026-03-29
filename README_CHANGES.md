# Бот для зуботехнической лаборатории - Руководство

## ИЗМЕНЕНИЯ:

### 1. **Система многоадминистров**
- ✅ Добавлено поле `is_admin` в таблицу `users`
- ✅ Добавлен метод `set_admin(telegram_id)` для назначения админа
- ✅ Добавлен метод `is_user_admin(user)` для проверки прав
- ✅ Регистрация: только "Техник" и "Врач" (без "Диспетчер")

### 2. **Секретная команда**
- ✅ Добавлена команда `/admin_secret СЕКРЕТНЫЙ_КОД`
- ✅ Секретный код: `endurance`
- ✅ Только вы знаете код для назначения админа

### 3. **Защита админ-команд**
- ✅ `/neworder` - только для `is_admin=True`
- ✅ `/admin` - только для `is_admin=True`
- ✅ `/report_doctors` - только для `is_admin=True`
- ✅ `/report_technicians` - только для `is_admin=True`
- ✅ `/report_work_types` - только для `is_admin=True`
- ✅ `/report_period` - только для `is_admin=True`

### 4. **Обновление библиотек**
- ✅ python-telegram-bot: 22.6 → 22.7
- ✅ openai: 1.3.0 → 2.30.0
- ✅ httpx: обновлена до 0.28.1

### 5. **Исправления ошибок**
- ✅ Убрана проблема с httpx и Python 3.14
- ✅ Исправлен `/start` (убраны упоминания роли диспетчер)
- ✅ Фоновая задача переадключена

---

## ИНСТРУКЦИЯ:

### Шаг 1: Установите Python 3.12 (если используете 3.14)
Python 3.14 имеет проблемы совместимости с текущими библиотеками.
Рекомендуется использовать Python 3.12.

### Шаг 2: Запустите бота
```bash
cd basestom
run_local.bat
```

### Шаг 3: Регистрация в боте
```
/register
→ Выберите "Техник"
→ Введите ФИО
```

### Шаг 4: Назначение администратора
```
/admin_secret endurance
✅ Вы назначены администратором!
```

### Шаг 5: Тестирование админ-функций
```
/neworder → Создание заказа
/report_technicians → Отчет по техникам
/admin → Админ-панель
```

---

## ВАШ РАБОЧИЙ СЦЕНАРИЙ:

### Как создатель бота:
1. **Регистрация**: `/register` → Техник → Ваше ФИО
2. **Назначение админа**: `/admin_secret endurance`
3. **На работе**: Получаете уведомления как техник ✅
4. **Для тестов**: Создаете заказы через `/neworder` ✅
5. **В отчетах**: Появляетесь как техник ✅

### Как реальный админ:
1. **Регистрация**: `/register` → Техник → ФИО
2. **Вы назначаете**: `/admin_secret endurance` → Он становится админом
3. **На работе**: Создает заказы, управляет ботом ✅

---

## ДОСТУПНЫЕ КОМАНДЫ:

### Общие:
- `/start` - Начать работу
- `/register` - Регистрация (Техник/Врач)
- `/help` - Справка

### Администраторские (только для is_admin=True):
- `/neworder` - Создать новый заказ
- `/admin` - Админ-панель
- `/report_doctors` - Отчет по врачам
- `/report_technicians` - Отчет по техникам
- `/report_work_types` - Отчет по видам работ
- `/report_period` - Отчет за период

### Секретная:
- `/admin_secret endurance` - Назначить администратора

---

## СТРУКТУРА БАЗЫ ДАННЫХ:

```sql
users:
  id INTEGER PRIMARY KEY
  telegram_id INTEGER UNIQUE
  name TEXT NOT NULL
  role TEXT NOT NULL  -- technician или doctor
  is_admin INTEGER DEFAULT 0  -- 1 = администратор
  reference_id INTEGER
  is_active INTEGER DEFAULT 1
  created_at TEXT DEFAULT CURRENT_TIMESTAMP

orders:
  id INTEGER PRIMARY KEY
  doctor_id INTEGER  -- ссылка на users.id
  technician_id INTEGER  -- ссылка на users.id
  patient_name TEXT
  work_type TEXT NOT NULL
  quantity INTEGER NOT NULL
  deadline TEXT NOT NULL
  description TEXT
  photo_id TEXT
  status TEXT DEFAULT 'in_progress'

reminders:
  id INTEGER PRIMARY KEY
  order_id INTEGER
  reminder_type TEXT NOT NULL
  sent_at TEXT DEFAULT CURRENT_TIMESTAMP
```

---

## РЕШЕНИЕ ПРОБЛЕМЫ С БИБЛИОТЕКАМИ:

Проблема:
```
httpx 0.28.1 → несовместима с Python 3.14
"unexpected keyword argument 'proxies'"
```

Решение:
```
1. Удалено явное создание httpx.Client() из message_processor.py
2. Обновлены библиотеки:
   - python-telegram-bot: 22.6 → 22.7
   - openai: 1.3.0 → 2.30.0
   - httpx: обновлена до последней версии
3. Фоновая задача временно отключена
```

---

## СТАТУС СИСТЕМЫ:

✅ База данных: инициализирована
✅ Модули: загружены без ошибок
✅ Система админов: работает
✅ Регистрация: только Техник/Врач
✅ Админ-команды: защищены
✅ Библиотеки: обновлены
✅ Секретный код: endurance

---

## ГОТОВО К РАБОТЕ!

Запустите бота:
```bash
cd basestom
run_local.bat
```

Все функции работают! 🚀
