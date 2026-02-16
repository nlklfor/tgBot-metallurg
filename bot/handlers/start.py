"""
Start handlers for the bot initialization.
"""

import logging
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_command_handler(message: types.Message, state: FSMContext) -> None:
    """Handle /start command."""
    try:
        await message.answer(
            "Привет! 👋🏻\n\n"
            "Я помогу оформить заказ и отследить его статус."
        )
        logger.info(f"User {message.from_user.id} started bot")
    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}", exc_info=True)
        await message.answer("❌ Ошибка при обработке команды.")


@router.callback_query(lambda c: c.data == "go_start")
async def go_start_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to main menu."""
    try:
        await state.clear()
        await callback.message.answer("🏠 Главное меню")
        await callback.answer()
        logger.info(f"User {callback.from_user.id} returned to main menu")
    except Exception as e:
        logger.error(f"Error returning to start: {str(e)}")
        await callback.answer("❌ Ошибка при возврате в главное меню.", show_alert=True)
