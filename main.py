"""
Bot entry point.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import TOKEN
from database.connection import get_connection
from bot.handlers import contact, start, status, faq
from bot.handlers import tracking_details
from bot.services.notify import start_notify_loop

logging.basicConfig(level=logging.INFO, stream=__import__("sys").stdout)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
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
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(start.router)
    dp.include_router(status.router)
    dp.include_router(faq.router)
    dp.include_router(contact.router)
    dp.include_router(tracking_details.router)
    print("🚀 Bot is starting...")
    asyncio.create_task(start_notify_loop(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
