from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database import get_session
from repositories.order import OrderRepository
from states.order import OrderStates
from models import OrderStatus

router = Router()

# обрабочик отмены заказа

@router.callback_query(lambda c: c.data == "cancel_order")
async def cancel_order_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Заказ отменен.")
    await callback.answer()

# обработчик подтверждения заказа

@router.callback_query(lambda c: c.data == "confirm_order", OrderStates.confirm_order,)

async def confirm_order_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")

    if not product_id:
        await callback.message.answer("❌ Ошибка при оформлении заказа. Товар не найден.")
        await state.clear()
        return

    async for session in get_session():
        order_repo = OrderRepository(session)
        order = await order_repo.create_order(
            user_id=callback.from_user.id,
            product_id=product_id,
        )

    await callback.message.edit_text(
            f"✅ Заказ оформлен!\n\n"
            f"📦 Номер заказа: `{order.tracking_code}`\n"
            f"📍 Статус: {order.status.value}",
            parse_mode="Markdown",
    )

    await state.clear()
    await callback.answer()