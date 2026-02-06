"""
Order handlers for managing order creation and cancellation.
"""

import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from database import get_session
from repositories.order import OrderRepository
from states.order import OrderStates
from keyboards.status import check_status_keyboard

router = Router()
logger = logging.getLogger(__name__)


# ============================================================================
# Cancel Order Handler
# ============================================================================

@router.callback_query(lambda c: c.data == "cancel_order")
async def cancel_order_handler(callback: CallbackQuery, state: FSMContext):
    """Handle order cancellation."""
    try:
        await state.clear()
        await callback.message.edit_text("❌ Заказ отменен.")
        await callback.answer()
        logger.info(f"Order cancelled by user {callback.from_user.id}")
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        await callback.answer("❌ Ошибка при отмене заказа.", show_alert=True)


# ============================================================================
# Confirm Order Handler
# ============================================================================

@router.callback_query(
    lambda c: c.data == "confirm_order",
    StateFilter(OrderStates.confirm_order),
)
async def confirm_order_handler(callback: CallbackQuery, state: FSMContext):
    """Handle order confirmation."""
    try:
        data = await state.get_data()
        product_id = data.get("product_id")

        if not product_id:
            logger.warning(f"Confirm order attempt without product_id by user {callback.from_user.id}")
            await callback.message.answer(
                "❌ Ошибка при оформлении заказа. Товар не найден."
            )
            await state.clear()
            await callback.answer()
            return

        # Create order
        async for session in get_session():
            order_repo = OrderRepository(session)
            order = await order_repo.create_order(
                user_id=callback.from_user.id,
                product_id=product_id,
            )

        logger.info(f"Order created: {order.tracking_code} by user {callback.from_user.id}")

        await callback.message.edit_text(
            f"✅ Заказ оформлен!\n\n"
            f"📦 Номер заказа: `{order.tracking_code}`\n"
            f"📍 Статус: {order.status.value}",
            parse_mode="Markdown",
            reply_markup=check_status_keyboard(order.tracking_code),
        )

        await state.clear()
        await callback.answer()

    except ValueError as e:
        logger.error(f"Validation error confirming order: {str(e)}")
        await callback.message.answer("❌ Ошибка: товар не найден или недоступен.")
        await callback.answer()
    except Exception as e:
        logger.error(f"Unexpected error confirming order: {str(e)}")
        await callback.message.answer("❌ Ошибка при оформлении заказа. Пожалуйста, попробуйте позже.")
        await callback.answer(show_alert=True)
        await state.clear()
