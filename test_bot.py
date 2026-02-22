import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

async def test_bot():
    try:
        bot = Bot(token=BOT_TOKEN)
        bot_info = await bot.get_me()
        print(f"Bot info: {bot_info}")
        print(f"Bot name: {bot_info.first_name}")
        print(f"Bot username: @{bot_info.username}")
        print("Bot token is VALID and working!")
    except Exception as e:
        print(f"Error: {e}")
        print("Bot token is INVALID or there's a connection issue!")

if __name__ == '__main__':
    asyncio.run(test_bot())
