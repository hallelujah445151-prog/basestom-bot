# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_reminder_time_logic():
    """Тестирование логики времени напоминаний"""

    print("=" * 70)
    print(" TESTING REMINDER TIME LOGIC WITH RETRY WINDOW")
    print("=" * 70)
    print()

    tz = ZoneInfo('Europe/Moscow')

    reminder_start_time = time(10, 0, 0)   # 10:00
    reminder_end_time = time(10, 30, 0)    # 10:30

    test_times = [
        ("09:59", datetime(2026, 4, 7, 9, 59, 0, tzinfo=tz)),
        ("10:00", datetime(2026, 4, 7, 10, 0, 0, tzinfo=tz)),
        ("10:05", datetime(2026, 4, 7, 10, 5, 0, tzinfo=tz)),
        ("10:10", datetime(2026, 4, 7, 10, 10, 0, tzinfo=tz)),
        ("10:15", datetime(2026, 4, 7, 10, 15, 0, tzinfo=tz)),
        ("10:20", datetime(2026, 4, 7, 10, 20, 0, tzinfo=tz)),
        ("10:25", datetime(2026, 4, 7, 10, 25, 0, tzinfo=tz)),
        ("10:30", datetime(2026, 4, 7, 10, 30, 0, tzinfo=tz)),
        ("10:31", datetime(2026, 4, 7, 10, 31, 0, tzinfo=tz)),
        ("12:01", datetime(2026, 4, 7, 12, 1, 0, tzinfo=tz)),
    ]

    for time_str, test_time in test_times:
        current_time = test_time.time()
        current_date = test_time.date()

        print(f"Time: {time_str} ({current_time.strftime('%H:%M')})")

        if current_time < reminder_start_time:
            result = "SKIP - Too early"
        elif current_time > time(12, 0, 0):
            result = "SKIP - Too late"
        elif reminder_start_time <= current_time <= reminder_end_time:
            result = "PROCESS - In retry window (10:00-10:30)"
        else:
            result = "PROCESS - After retry window but before 12:00"

        print(f"  Result: {result}")
        print()

    print("=" * 70)
    print(" RETRY WINDOW SCENARIOS")
    print("=" * 70)
    print()

    scenarios = [
        ("Scenario 1: 10:00 - First check", time(10, 0, 0), False),
        ("Scenario 2: 10:05 - First retry", time(10, 5, 0), True),
        ("Scenario 3: 10:10 - Second retry", time(10, 10, 0), True),
        ("Scenario 4: 10:15 - Third retry", time(10, 15, 0), True),
        ("Scenario 5: 10:20 - Fourth retry", time(10, 20, 0), True),
        ("Scenario 6: 10:25 - Fifth retry", time(10, 25, 0), True),
        ("Scenario 7: 10:30 - Sixth retry", time(10, 30, 0), True),
        ("Scenario 8: 10:31 - Too late for retry", time(10, 31, 0), True),
    ]

    for scenario_name, test_time, retry_mode in scenarios:
        print(f"{scenario_name}:")
        print(f"  Time: {test_time.strftime('%H:%M')}")

        if test_time < reminder_start_time:
            action = "Skip - Too early"
        elif test_time > time(12, 0, 0):
            action = "Skip - Too late"
        elif reminder_start_time <= test_time <= reminder_end_time:
            if retry_mode:
                action = "RETRY MODE - Resend failed reminders"
            else:
                action = "FIRST CHECK - Process all orders"
        else:
            if retry_mode:
                action = "Skip - Retry window ended"
            else:
                action = "Skip - Retry window ended"

        print(f"  Action: {action}")
        print()


if __name__ == "__main__":
    test_reminder_time_logic()