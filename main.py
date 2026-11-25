"""
Bot entry point.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.constants import COMMANDS
from bot.handlers import alerts, contact, faq, operator, start, status
from bot.services.notify import start_notify_loop
from bot.services.order_updates import start_order_updates_loop
from config import TOKEN
from database.connection import close_pool, db, init_pool

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def test_db():
    try:
        await init_pool()
        async with db() as conn:
            await conn.fetchval("SELECT 1")
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise


async def main():
    await test_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in COMMANDS])

    # Order matters: status goes last because its "waiting for a code" handler
    # accepts any text.
    dp.include_router(start.router)
    dp.include_router(operator.router)
    dp.include_router(alerts.router)
    dp.include_router(faq.router)
    dp.include_router(contact.router)
    dp.include_router(status.router)

    print("🚀 Bot is starting...")
    tasks = [
        asyncio.create_task(start_notify_loop(bot)),
        asyncio.create_task(start_order_updates_loop(bot)),
    ]
    try:
        await dp.start_polling(bot)
    finally:
        for t in tasks:
            t.cancel()
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
