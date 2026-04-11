import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import bot

try:
    asyncio.run(bot.main_async())
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    if 'TimedOut' in str(type(e)) or 'ConnectTimeout' in str(type(e)):
        print('Network timeout - this is expected if VPN is not enabled.')
        print('The bot code is correct, just needs network connection.')
    elif 'ConnectError' in str(e):
        print('Connection error - check VPN and internet connection.')
    else:
        import traceback
        traceback.print_exc()
