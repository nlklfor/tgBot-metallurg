"""
Bot entry point.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from database.connection import get_connection
from bot.handlers import start, status

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def test_db():
    try:
        conn = await get_connection()
        print("✅ Database connected successfully")
        await conn.close()
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        raise


async def main():
    await test_db()
    dp.include_router(start.router)
    dp.include_router(status.router)
    print("🚀 Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
