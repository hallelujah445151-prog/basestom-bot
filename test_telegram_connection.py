# -*- coding: utf-8 -*-
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

async def test_telegram_connection():
    """Тестирование подключения к Telegram API"""

    print("=" * 70)
    print(" TESTING TELEGRAM API CONNECTION")
    print("=" * 70)
    print()

    bot_token = os.getenv('BOT_TOKEN')

    if not bot_token:
        print("ERROR: BOT_TOKEN not found in .env file")
        return

    print(f"Bot token: {bot_token[:10]}...")
    print()

    try:
        print("Initializing bot...")
        bot = Bot(token=bot_token)

        print("Getting bot info...")
        me = await bot.get_me()

        print(f"SUCCESS: Connected to Telegram API!")
        print()
        print(f"Bot name: {me.full_name}")
        print(f"Bot username: @{me.username}")
        print(f"Bot ID: {me.id}")
        print()

        print("=" * 70)
        print(" CONNECTION TEST PASSED")
        print("=" * 70)
        print()
        print("Bot is ready to start!")

        return True

    except Exception as e:
        print(f"ERROR: Failed to connect to Telegram API")
        print()
        print(f"Error details: {e}")
        print()
        print("POSSIBLE REASONS:")
        print("1. VPN is not enabled or not working")
        print("2. Internet connection is down")
        print("3. Telegram API is blocked in your region")
        print("4. Bot token is invalid or expired")
        print()
        print("SOLUTIONS:")
        print("1. Enable VPN and try again")
        print("2. Check internet connection")
        print("3. Try accessing https://api.telegram.org in browser")
        print("4. Regenerate bot token if needed")
        print()

        print("=" * 70)
        print(" CONNECTION TEST FAILED")
        print("=" * 70)

        return False


if __name__ == "__main__":
    result = asyncio.run(test_telegram_connection())

    if result:
        print("\nNext: Run 'python src/bot.py' to start the bot")
    else:
        print("\nNext: Fix connection issues and try again")