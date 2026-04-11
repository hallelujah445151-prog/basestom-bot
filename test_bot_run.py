import os
os.environ['BOT_TOKEN']='8592737363:AAGK2R2KxJuGY9-RPZlBq2YBupKz0NAr0H8'

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import bot

try:
    asyncio.run(bot.main_async())
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
