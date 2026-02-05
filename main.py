import asyncio
from aiogram import Bot, Dispatcher

from config import TOKEN
from handlers import order, status, admin, start
from database import init_models


async def main():
    await init_models()
    
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(order.router)
    dp.include_router(status.router)
    dp.include_router(admin.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
