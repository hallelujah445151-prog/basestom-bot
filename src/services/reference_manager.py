import json
import os
from typing import Dict, List, Optional


REFERENCES_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'references.json')


class ReferenceManager:
    """Управление реестрами"""

    def __init__(self):
        self.data = self.load_references()

    def load_references(self) -> dict:
        """Загрузка реестров из JSON"""
        with open(REFERENCES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def find_doctor(self, search: str) -> Optional[dict]:
        """Поиск врача по названию"""
        for doctor in self.data['doctors']:
            if search.lower() in doctor['name'].lower() or search.lower() in doctor['full_name'].lower():
                return doctor
        return None

    def find_technician(self, search: str) -> Optional[dict]:
        """Поиск техника по названию"""
        for technician in self.data['technicians']:
            if search.lower() in technician['name'].lower() or search.lower() in technician['full_name'].lower():
                return technician
        return None

    def find_work_type(self, search: str) -> Optional[dict]:
        """Поиск вида работы по названию"""
        for work_type in self.data['work_types']:
            if search.lower() in work_type['name'].lower() or search.lower() in work_type['short_name'].lower():
                return work_type
        return None

    def get_all_doctors(self) -> List[dict]:
        """Получить всех врачей"""
        return self.data['doctors']

    def get_all_technicians(self) -> List[dict]:
        """Получить всех техников"""
        return self.data['technicians']

    def get_all_work_types(self) -> List[dict]:
        """Получить все виды работ"""
        return self.data['work_types']
