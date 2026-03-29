import os
import time
import re
from openai import OpenAI


class MessageProcessor:
    """Обработка сообщений с помощью ИИ"""

    def __init__(self):
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("WARNING: OPENROUTER_API_KEY not found in environment, using simple parser only")
            self.client = None
        else:
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                    timeout=10.0
                )
            except Exception as e:
                print(f"WARNING: Failed to initialize OpenAI client: {e}, using simple parser only")
                self.client = None

    def parse_message_simple(self, text: str) -> dict:
        """Простой парсер сообщения без AI"""
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
            if 'от' in part_lower:
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

        print(f"[DEBUG parse_message_simple] Result: {result}")
        return result

    def normalize_message(self, text: str) -> dict:
        """Нормализация короткого сообщения в корректный формат"""
        system_prompt = """
        Ты помощник для обработки заказов в зуботехнической лаборатории.
        На вход ты получаешь короткое сообщение с информацией о заказе.
        Твоя задача - распознать структуру данных и вернуть в формате JSON.

        Формат ответа:
        {
            "technician_name": "ФИО техники (фамилия)",
            "doctor_name": "ФИО врача (если есть)",
            "patient_name": "ФИО пациента (если есть)",
            "work_type": "вид работы (короткое название)",
            "quantity": количество (число),
            "deadline": "дата дедлайна (в формате ДД.ММ.ГГГГ или null)",
            "notes": "дополнительные заметки (если есть)"
        }

        Примеры:
        Вход: "Мороков циркон на винте 7шт пациент Иванов"
        Выход: {"technician_name": "Мороков", "work_type": "циркон на винте", "quantity": 7, "deadline": null, "patient_name": "Иванов", "notes": ""}

        Вход: "Сидоров металлокерамика 13шт на завтра пациент Петров"
        Выход: {"technician_name": "Сидоров", "work_type": "металлокерамика", "quantity": 13, "deadline": null, "patient_name": "Петров", "notes": "на завтра"}

        Вход: "Козлов виниры 5шт от Иванова 15.02.2026 пациент Сидоров"
        Выход: {"technician_name": "Козлов", "work_type": "виниры", "quantity": 5, "deadline": "15.02.2026", "doctor_name": "Иванов", "patient_name": "Сидоров"}
        """

        try:
            print(f"[OpenRouter] Starting request for: {text[:50]}...")
            start_time = time.time()

            response = self.client.chat.completions.create(
                model="meta-llama/llama-3-8b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"[OpenRouter] Request completed in {elapsed_time:.2f} seconds")

            import json
            result = json.loads(response.choices[0].message.content)

            print(f"[DEBUG normalize_message] OpenRouter result: {result}")
            return result

        except Exception as e:
            print(f"OpenAI Error: {e}")
            print("Falling back to simple parser...")
            return self.parse_message_simple(text)

    def format_message(self, data: dict) -> str:
        """Форматирование данных в корректное сообщение"""
        parts = []

        if data.get('technician_name'):
            parts.append(f"Техник: {data['technician_name']}")

        if data.get('patient_name'):
            parts.append(f"Пациент: {data['patient_name']}")

        if data.get('work_type'):
            parts.append(f"Вид работы: {data['work_type']}")

        if data.get('quantity'):
            parts.append(f"Количество: {data['quantity']}шт")

        if data.get('deadline'):
            parts.append(f"Срок: {data['deadline']}")

        if data.get('notes'):
            parts.append(f"Заметки: {data['notes']}")

        return ". ".join(parts) + "."
