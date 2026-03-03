from os import sync
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


from bot.states.orders import OrderStates
from bot.constants import BACK_BTN, CHECK_STATUS_BTN, STATUS_MAP
from bot.keyboards.main import main_keyboard
from bot.services.order import get_order_by_number

router = Router()


@router.message(lambda message: message.text == CHECK_STATUS_BTN)
async def ask_order_number(message: Message, state: FSMContext):
    await message.answer(
        "<b>// SYSTEM_LOG:</b> Initializing tracking sequence...\n"
        "Please enter your <b>[ORDER_ID]</b> for synchronization:",
        reply_markup=main_keyboard(),
    )
    await state.set_state(OrderStates.waiting_for_order_number)


@router.message(OrderStates.waiting_for_order_number)
async def show_status(message: Message, state: FSMContext):
    order_number = message.text.strip()

    order = await get_order_by_number(order_number)

    if not order:
        await message.answer(
            "<b>// ACCESS_DENIED:</b> Order not found.\n"
            "Check your <b>[ORDER_ID]</b> and try again.\n"
            "If the error persists, contact <b>MTL // INTERFACE</b>.",
        )
        return

    pretty_status = STATUS_MAP.get(order["status"], order["status"])
    order_name = order.get("product_name", "N/A")
    order_size = order.get("size", "N/A")

    await message.answer(
        f"<b>// ORDER_FOUND_IN_ARCHIVE</b>\n"
        f"--------------------------------\n"
        f"<b>ID:</b> <code>{order_number}</code>\n"
        f"<b>OBJECT:</b> {order_name.upper()}\n"
        f"<b>SIZE_SPEC:</b> {order_size}\n"
        f"<b>CURRENT_STATUS:</b> <code>{pretty_status}</code>\n"
        f"--------------------------------\n"
        f"<i>// Last database update: 2026</i>",
    )

    await state.clear()

    await message.answer(BACK_BTN, reply_markup=main_keyboard())
