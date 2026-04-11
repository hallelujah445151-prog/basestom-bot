import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print('[TEST] Testing reminder_service.py...')
    from services.reminder_service import ReminderService
    print('[OK] ReminderService imported')
    
    print('[TEST] Testing get_orders_due_tomorrow()...')
    orders = ReminderService.get_orders_due_tomorrow()
    print(f'[OK] Returned {len(orders)} orders')
    
    print('[TEST] Testing get_orders_due_today()...')
    orders_today = ReminderService.get_orders_due_today()
    print(f'[OK] Returned {len(orders_today)} orders')
    
    print('[SUCCESS] All tests passed!')
except Exception as e:
    print(f'[ERROR] {e}')
    import traceback
    traceback.print_exc()
