"""
Start handlers for the bot initialization and product selection.
"""

import logging
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database import get_session
from repositories.product import ProductRepository
from keyboards.order import confirm_order_keyboard
from keyboards.start import start_keyboard
from states.order import OrderStates

router = Router()
logger = logging.getLogger(__name__)


# ============================================================================
# Start Command Handler
# ============================================================================

@router.message(CommandStart())
async def start_command_handler(message: types.Message, state: FSMContext) -> None:
    """Handle /start command with optional product_id parameter."""
    try:
        args = message.text.split()

        # /start - show main menu
        if len(args) == 1:
            await message.answer(
                "Привет! 👋🏻\n\n"
                "Я помогу оформить заказ и отследить его статус.",
                reply_markup=start_keyboard(),
            )
            logger.info(f"User {message.from_user.id} started bot")
            return

        # /start <product_id> - show product
        product_id = args[1]
        logger.info(f"User {message.from_user.id} requesting product: {product_id}")

        async for session in get_session():
            product_repo = ProductRepository(session)
            product = await product_repo.get_product_by_id(product_id)

            if not product or not product.is_active:
                logger.warning(f"Product not found or inactive: {product_id}")
                await message.answer(
                    "❌ Товар не найден или недоступен. Пожалуйста, выберите другой товар."
                )
                return

            await state.update_data(product_id=product.id)
            await state.set_state(OrderStates.confirm_order)

            text = (
                f"🛒 *{product.title}*\n\n"
                f"{product.description or ''}\n\n"
                f"💰 Цена: {product.price} UAH\n\n"
                f"Подтвердите покупку."
            )

            await message.answer(
                text=text,
                reply_markup=confirm_order_keyboard(),
                parse_mode="Markdown",
            )
            logger.info(f"Product {product_id} shown to user {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}", exc_info=True)
        await message.answer(
            "❌ Ошибка при обработке команды. Пожалуйста, попробуйте позже."
        )


# ============================================================================
# Main Menu Navigation
# ============================================================================

@router.callback_query(lambda c: c.data == "go_start")
async def go_start_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to main menu."""
    try:
        await state.clear()
        await callback.message.answer(
            "🏠 Главное меню\n\n"
            "Выберите действие:",
            reply_markup=start_keyboard(),
        )
        await callback.answer()
        logger.info(f"User {callback.from_user.id} returned to main menu")
    except Exception as e:
        logger.error(f"Error returning to start: {str(e)}")
        await callback.answer("❌ Ошибка при возврате в главное меню.", show_alert=True)
