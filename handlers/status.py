"""
Status handlers for checking order status.
"""

import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database import get_session
from repositories.order import OrderRepository
from states.order import OrderStates
from keyboards.common import back_to_start_keyboard

router = Router()
logger = logging.getLogger(__name__)


# ============================================================================
# Status Command
# ============================================================================

@router.message(Command("status"))
async def status_command_handler(message: types.Message, state: FSMContext) -> None:
    """Handle /status command to check order status."""
    try:
        await state.set_state(OrderStates.waiting_tracking_code)
        await message.answer("📦 Введите tracking-код вашего заказа:")
        logger.info(f"User {message.from_user.id} initiated status check")
    except Exception as e:
        logger.error(f"Error in status command: {str(e)}")
        await message.answer("❌ Ошибка при обработке команды.")


# ============================================================================
# Status Check from Keyboard
# ============================================================================

@router.callback_query(lambda c: c.data == "start_check_status")
async def start_check_status_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle status check from keyboard button."""
    try:
        await state.set_state(OrderStates.waiting_tracking_code)
        await callback.message.answer("📦 Введите tracking-код вашего заказа:")
        await callback.answer()
        logger.info(f"User {callback.from_user.id} initiated status check from keyboard")
    except Exception as e:
        logger.error(f"Error in start_check_status: {str(e)}")
        await callback.answer("❌ Ошибка при инициации проверки.", show_alert=True)
 

# ============================================================================
# Process Tracking Code
# ============================================================================

@router.message(OrderStates.waiting_tracking_code)
async def show_order_status_handler(message: types.Message, state: FSMContext) -> None:
    """Process tracking code and show order status."""
    try:
        tracking_code = message.text.strip()
        logger.info(f"User {message.from_user.id} checking status for: {tracking_code}")

        async for session in get_session():
            order_repo = OrderRepository(session)
            order = await order_repo.get_by_tracking_code(tracking_code)

            if not order:
                logger.warning(f"Order not found: {tracking_code}")
                await message.answer(
                    "❌ Заказ с таким tracking-кодом не найден. Пожалуйста, проверьте и попробуйте снова.\n\nВы можете вернуться в главное меню.",
                    reply_markup=back_to_start_keyboard(),
                )
                await state.clear()
                return

            logger.info(f"Order status retrieved: {tracking_code} - {order.status.value}")
            await message.answer(
                f"📦 Статус заказа:\n\n"
                f"🔢 Код: {tracking_code}\n"
                f"📍 Статус: {order.status.value}",
                reply_markup=back_to_start_keyboard(),
            )

        await state.clear()

    except Exception as e:
        logger.error(f"Error showing order status: {str(e)}", exc_info=True)
        await message.answer("❌ Ошибка при проверке статуса заказа. Пожалуйста, попробуйте позже.")
        await state.clear()


# ============================================================================
# Inline Status Check
# ============================================================================

@router.callback_query(lambda c: c.data.startswith("check_status:"))
async def check_status_callback_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handle inline status check from callback button."""
    try:
        tracking_code = callback.data.split(":")[1]
        logger.info(f"User {callback.from_user.id} checking status inline: {tracking_code}")

        async for session in get_session():
            order_repo = OrderRepository(session)
            order = await order_repo.get_by_tracking_code(tracking_code)

            if not order:
                logger.warning(f"Order not found in callback: {tracking_code}")
                await callback.answer(
                    "❌ Заказ не найден. Пожалуйста попробуйте снова.",
                    show_alert=True,
                )
                return

            logger.info(f"Order status retrieved inline: {tracking_code} - {order.status.value}")
            await callback.message.answer(
                f"📦 Статус заказа:\n\n"
                f"🔢 Код: {tracking_code}\n"
                f"📍 Статус: {order.status.value}",
                reply_markup=back_to_start_keyboard(),
            )

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in check_status_callback: {str(e)}")
        await callback.answer("❌ Ошибка при проверке статуса.", show_alert=True)
