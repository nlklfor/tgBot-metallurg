from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database import get_session
from repositories.order import OrderRepository
from states.order import OrderStates
from keyboards.common import back_to_start_keyboard


router = Router()


@router.message(Command("status"))
async def status_command_handler(message: types.Message, state: FSMContext):
    await state.set_state(OrderStates.waiting_tracking_code)
    await message.answer("📦 Введите tracking-код вашего заказа:")


@router.callback_query(lambda c: c.data == "start_check_status")
async def start_check_status(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.waiting_tracking_code)
    await callback.message.answer("📦 Введите tracking code вашего заказа:")
    await callback.answer()


@router.message(OrderStates.waiting_tracking_code)
async def show_order_status_handler(message: types.Message, state: FSMContext):
    tracking_code = message.text.strip()

    async for session in get_session():
        order_repo = OrderRepository(session)
        order = await order_repo.get_by_tracking_code(tracking_code)

        if not order:
            await message.answer(
                "❌ Заказ с таким tracking-кодом не найден. Пожалуйста, проверьте и попробуйте снова.\n\nВы можете вернуться в главное меню.",
                reply_markup=back_to_start_keyboard(),
            )
            await state.clear()
            return

        await message.answer(
            f"📦 Статус заказа:\n\n"
            f"🔢 Код: `{order.tracking_code}`\n"
            f"📍 Статус: *{order.status.value}*",
            parse_mode="Markdown",
            reply_markup=back_to_start_keyboard(),
        )

    await state.clear()


@router.callback_query(lambda c: c.data.startswith("check_status:"))
async def check_status_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    tracking_code = callback.data.split(":")[1]

    async for session in get_session():
        order_repo = OrderRepository(session)
        order = await order_repo.get_by_tracking_code(tracking_code)

        if not order:
            await callback.answer(
                "❌ Заказ не найден. Пожалуйста попробуйте снова.",
                show_alert=True,
            )
            return

        await callback.message.answer(
            f"📦 Статус заказа:\n\n"
            f"🔢 Код: `{order.tracking_code}`\n"
            f"📍 Статус: *{order.status.value}*",
            parse_mode="Markdown",
            reply_markup=back_to_start_keyboard(),
        )

    await callback.answer()
