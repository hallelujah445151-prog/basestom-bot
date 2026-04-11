import os
import sys
import httpx
from openai import OpenAI

# Загружаем переменные окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class MessageProcessor:
    """Обработка сообщений с помощью ИИ"""

    def __init__(self):
        # Минимальная конфигурация для совместимости
        api_key = os.getenv('OPENROUTER_API_KEY')

        if not api_key:
            print("WARNING: OPENROUTER_API_KEY not found, using simple parser only")
            self.client = None
        else:
            try:
                # Создаем кастомный httpx клиент без прокси
                http_client = httpx.Client(
                    timeout=30.0,
                    follow_redirects=True
                )

                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                    http_client=http_client
                )
                print(f"[OpenAI] Client initialized successfully")
            except Exception as e:
                print(f"ERROR: Failed to initialize OpenAI client: {e}")
                print(f"Falling back to simple parser")
                self.client = None

        from services.dental_terminology_service import DentalTerminologyService
        self.dental_service = DentalTerminologyService()
        self.dental_cache = {}

    def parse_message_simple(self, text: str) -> dict:
        """Простой парсер сообщения без ИИ"""
        print(f"[DEBUG parse_message_simple] Parsing: '{text}'")
        result = {
            'technician_name': None,
            'doctor_name': None,
            'patient_name': None,
            'work_type': None,
            'quantity': None,
            'deadline': None,
            'notes': None
        }

        text_lower = text.lower()

        try:
            quantity_match = re.search(r'(\d+)\s*шт', text)
            if quantity_match:
                result['quantity'] = int(quantity_match.group(1))
        except:
            pass

        try:
            deadline_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', text)
            if deadline_match:
                result['deadline'] = deadline_match.group(0)
        except:
            pass

        parts = text.split()

        work_types = [
            'циркон', 'винт', 'металлокерамика', 'виниры', 'коронки',
            'мост', 'протез', 'брекеты', 'отбеливание'
        ]

        for i, part in enumerate(parts):
            part_lower = part.lower().strip('.,;')
            if part_lower in work_types or any(wt in part_lower for wt in work_types):
                end_idx = i + 1
                while end_idx < len(parts) and not any(wt in parts[end_idx].lower() for wt in work_types):
                    end_idx += 1
                result['work_type'] = ' '.join(parts[i:end_idx]).strip('.,;')

                if i > 0:
                    result['technician_name'] = parts[i-1].strip('.,;')
                break

        patient_keywords = ['пациент', 'для']
        for i, part in enumerate(parts):
            part_lower = part.lower()
            if any(kw in part_lower for kw in patient_keywords):
                if i + 1 < len(parts):
                    patient_parts = []
                    j = i + 1
                    while j < len(parts) and not any(wt in parts[j].lower() for wt in work_types) and parts[j].lower() not in ['шт', 'на', 'от']:
                        patient_parts.append(parts[j].strip('.,;'))
                        j += 1
                    if patient_parts:
                        result['patient_name'] = ' '.join(patient_parts)
                break

        doctor_keywords = ['от', 'врач']
        for i, part in enumerate(parts):
            part_lower = part.lower()
            if any(keyword in part_lower for keyword in doctor_keywords):
                if i + 1 < len(parts):
                    result['doctor_name'] = parts[i+1].strip('.,;')
                break

        if not result['technician_name'] and parts:
            result['technician_name'] = parts[0].strip('.,;')

        if not result['work_type']:
            for part in parts:
                part_lower = part.lower().strip('.,;')
                if any(wt in part_lower for wt in work_types):
                    result['work_type'] = part
                    break

        if not result['work_type']:
            result['work_type'] = 'Не указано'

        if result.get('work_type') and result['work_type'] != 'Не указано':
            result['work_type'] = self.normalize_dental_terminology(result['work_type'])

        print(f"[DEBUG parse_message_simple] Result: {result}")
        return result

    def normalize_message(self, text: str) -> dict:
        """Нормализация короткого сообщения в корректный формат с использованием стоматологической терминологии"""
        if not self.client:
            print("[OpenRouter] OpenAI client not available, using simple parser")
            return self.parse_message_simple(text)

        system_prompt = """
        Ты эксперт-помощник для обработки заказов в зуботехнической лаборатории со знанием стоматологической терминологии.
        На вход ты получаешь короткое сообщение с информацией о заказе.
        Твоя задача - распознать структуру данных и вернуть в формате JSON, используя ПРАВИЛЬНУЮ стоматологическую терминологию.

        ПРАВИЛЬНАЯ ТЕРМИНОЛОГИЯ:

        1. Материалы (правильное написание):
           - "циркон" → "из диоксида циркония"
           - "металлокерамика" → "металлокерамическая коронка"
           - "керамика" → "безметалловая керамическая коронка"
           - "пластмасса" → "пластмассовая коронка"

        2. Виды работ:
           - "циркон на винте" → "цельнометаллическая коронка на винте"
           - "металлокерамика" → "металлокерамическая коронка"
           - "виниры циркон" → "керамические виниры из диоксида циркония"
           - "мост циркон" → "мост из диоксида циркония"
           - "бюгельный протез" → "бюгельный протез"

        Формат ответа:
        {
            "technician_name": "ФИО техники (фамилия)",
            "doctor_name": "ФИО врача (если есть)",
            "patient_name": "ФИО пациента (если есть)",
            "work_type": "вид работы (С ПРАВИЛЬНОЙ терминологией)",
            "quantity": количество (число),
            "deadline": "дата дедлайна (в формате ДД.ММ.ГГГГ или null)",
            "notes": "дополнительные заметки (если есть)"
        }

        Примеры:

        Вход: "Мороков циркон на винте 7шт пациент Иванов"
        Выход: {"technician_name": "Мороков", "work_type": "цельнометаллическая коронка на винте", "quantity": 7, "deadline": null, "patient_name": "Иванов", "notes": ""}

        Вход: "Сидоров металлокерамика 13шт на завтра пациент Петров"
        Выход: {"technician_name": "Сидоров", "work_type": "металлокерамическая коронка", "quantity": 13, "deadline": null, "patient_name": "Петров", "notes": "на завтра"}

        Вход: "Козлов виниры 5шт от Иванова 15.02.2026 пациент Сидоров"
        Выход: {"technician_name": "Козлов", "work_type": "керамические виниры из диоксида циркония", "quantity": 5, "deadline": "15.02.2026", "doctor_name": "Иванов", "patient_name": "Сидоров"}

        Вход: "Плюхин металлокерамика 2 шт на 02.04.2026 врач Гаспарянидзе пациент Анохин"
        Выход: {"technician_name": "Плюхин", "work_type": "металлокерамическая коронка", "quantity": 2, "deadline": "02.04.2026", "doctor_name": "Гаспарянидзе", "patient_name": "Анохин", "notes": ""}
        """

        try:
            print(f"[OpenRouter] Starting request for: {text[:50]}...")
            response = self.client.chat.completions.create(
                model="meta-llama/llama-3-8b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )

            corrected_text = response.choices[0].message.content.strip()
            print(f"[OpenRouter] Raw response: {corrected_text[:200]}")

            # Парсим JSON
            import json
            try:
                result = json.loads(corrected_text)

                if result.get('work_type'):
                    normalized_work_type = self.normalize_dental_terminology(result['work_type'])
                    result['work_type'] = normalized_work_type

                print(f"[OpenRouter] Parsed result: {result}")
                return result

            except json.JSONDecodeError as e:
                print(f"[OpenRouter] JSON decode error: {e}")
                print("[OpenRouter] Falling back to simple parser...")
                return self.parse_message_simple(text)

        except Exception as e:
            print(f"OpenAI Error: {e}")
            print("Falling back to simple parser...")
            return self.parse_message_simple(text)

    def normalize_dental_terminology(self, work_type: str) -> str:
        """Нормализация стоматологической терминологии с кэшированием"""
        if not work_type:
            return work_type

        work_type_lower = work_type.lower().strip()

        if work_type_lower in self.dental_cache:
            print(f"[Dental Cache HIT] '{work_type}' -> '{self.dental_cache[work_type_lower]}'")
            return self.dental_cache[work_type_lower]

        try:
            normalized = self.dental_service.normalize_work_type(work_type)
            self.dental_cache[work_type_lower] = normalized
            return normalized
        except Exception as e:
            print(f"[Dental Error] {e}, using original: {work_type}")
            return work_type

    def format_message(self, data: dict) -> str:
        """Форматирование данных в корректное сообщение"""
        parts = []

        if data.get('technician_name'):
            parts.append(f"Техник: {data['technician_name']}")

        if data.get('patient_name'):
            parts.append(f"Пациент: {data['patient_name']}")

        if data.get('work_type'):
            # Работа уже нормализована в normalize_message, не нужно повторной нормализации
            parts.append(f"Вид работы: {data['work_type']}")

        if data.get('quantity'):
            parts.append(f"Количество: {data['quantity']}шт")

        if data.get('deadline'):
            parts.append(f"Срок: {data['deadline']}")

        if data.get('notes'):
            parts.append(f"Заметки: {data['notes']}")

        return ". ".join(parts) + "."
