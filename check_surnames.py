import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
from services.user_manager import UserManager
from collections import Counter

print("=== Checking for duplicate surnames ===")

for role in ['doctor', 'technician']:
    users = UserManager.get_users_by_role(role)
    surnames = []

    for u in users:
        surname = u['name'].split()[0] if u['name'].split() else u['name']
        surnames.append(surname.lower())

    surname_counts = Counter(surnames)
    duplicate_surnames = {surname for surname, count in surname_counts.items() if count > 1}

    print(f"\n=== {role.upper()} ===")
    print(f"Total users: {len(users)}")
    print(f"Duplicate surnames: {duplicate_surnames}")

    if duplicate_surnames:
        print(f"  Details:")
        for surname in duplicate_surnames:
            users_with_surname = [u for u in users if u['name'].split()[0].lower() == surname]
            print(f"    {surname}: {len(users_with_surname)} users")
            for u in users_with_surname:
                print(f"      - {u['name']}")
