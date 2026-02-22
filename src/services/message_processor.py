import os
import time
from openai import OpenAI
from .reference_manager import ReferenceManager


class MessageProcessor:
    """Обработка сообщений с помощью ИИ"""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1",
            timeout=10.0
        )
        self.ref_manager = ReferenceManager()

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

            return self.enhance_with_references(result)

        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")
            return None

    def enhance_with_references(self, data: dict) -> dict:
        """Улучшение данных с помощью реестров"""
        enhanced = data.copy()

        if data.get('technician_name'):
            technician = self.ref_manager.find_technician(data['technician_name'])
            if technician:
                enhanced['technician_id'] = technician['id']
                enhanced['technician_name'] = technician['name']

        if data.get('doctor_name'):
            doctor = self.ref_manager.find_doctor(data['doctor_name'])
            if doctor:
                enhanced['doctor_id'] = doctor['id']
                enhanced['doctor_name'] = doctor['name']

        if data.get('work_type'):
            work_type = self.ref_manager.find_work_type(data['work_type'])
            if work_type:
                enhanced['work_type'] = work_type['name']

        return enhanced

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
