import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

async def test_send_message():
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Replace this with YOUR Telegram user ID
        # You can get your user ID from @userinfobot in Telegram
        test_chat_id = input("Enter your Telegram user ID: ")
        
        await bot.send_message(chat_id=test_chat_id, text="Test message from StomBOT!")
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == '__main__':
    asyncio.run(test_send_message())
