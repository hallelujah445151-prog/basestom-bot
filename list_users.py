import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
from services.user_manager import UserManager

print("=== Technicians ===")
users = UserManager.get_users_by_role('technician')
for u in users:
    print(f"{u['name']}")

print("\n=== Doctors ===")
users = UserManager.get_users_by_role('doctor')
for u in users:
    print(f"{u['name']}")
