"""
Main bot entry point with initialization and polling setup.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import TOKEN
from handlers import order, status, admin, start
from database import init_models
from models import create_test_product, create_test_order

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main async function for bot initialization and polling."""
    try:
        logger.info("Initializing database...")
        await init_models()
        
        logger.info("Creating test data...")
        await create_test_product()
        await create_test_order()
        
        logger.info("Setting up bot...")
        bot = Bot(token=TOKEN)
        dp = Dispatcher()

        # Register routers
        dp.include_router(start.router)
        dp.include_router(order.router)
        dp.include_router(status.router)
        dp.include_router(admin.router)

        logger.info("✅ Bot started successfully. Polling...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}", exc_info=True)
