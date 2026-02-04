from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import get_session
from repositories.order import OrderRepository
from states.order import OrderStates

router = Router()


@router.message(Command("status"))
async def status_command_handler(message: types.Message, state: FSMContext):
    await state.set_state(OrderStates.waiting_tracking_code)
    await message.answer("📦 Введите tracking-код вашего заказа:")


@router.message(OrderStates.waiting_tracking_code)
async def show_order_status_handler(message: types.Message, state: FSMContext):
    tracking_code = message.text.strip()

    async for session in get_session():
        order_repo = OrderRepository(session)
        order = await order_repo.get_by_tracking_code(tracking_code)

        if not order:
            await message.answer(
                "❌ Заказ с таким tracking-кодом не найден. Пожалуйста, проверьте и попробуйте снова."
            )
            return

        await message.answer(
            f"📦 Статус вашего заказа:\n\n"
            f"🔑 Трек-код: `{order.tracking_code}`\n"
            f"📍 Статус: {order.status.value}",
            parse_mode="Markdown",
        )

    await state.clear()
