from os import sync
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


from bot.states.orders import OrderStates
from bot.constants import BACK_BTN, CHECK_STATUS_BTN
from bot.keyboards.main import main_keyboard
from bot.services.order import get_order_by_number

router = Router()


STATUS_MAP = {
    "waiting_for_payment": "⏳ Очікує оплати",
    "paid": "✅ Оплачено",
    "processing": "📦 Готується до відправки",
    "shipped": "🚚 Відправлено",
    "completed": "🎉 Завершено",
}


@router.message(lambda message: message.text == "📦 Перевірити статус")
async def ask_order_number(message: Message, state: FSMContext):
    await message.answer("Введіть номер замовлення:")
    await state.set_state(OrderStates.waiting_for_order_number)


@router.message(OrderStates.waiting_for_order_number)
async def show_status(message: Message, state: FSMContext):
    order_number = message.text.strip()

    order = await get_order_by_number(order_number)

    if not order:
        await message.answer("❌ Замовлення не знайдено.")
        return

    pretty_status = STATUS_MAP.get(order["status"], order["status"])
    order_name = order.get("product_name", "N/A")
    order_size = order.get("size", "N/A")

    await message.answer(
        f"📦 Статус замовлення {order_number}:\n\n"
        f"📝 Назва: {order_name}\n"
        f"📐 Розмір: {order_size}\n"
        f"📊 Статус: {pretty_status}"
    )

    await state.clear()
    
    await message.answer(
    "Оберіть наступну дію:",
    reply_markup=main_keyboard()
)


@router.message(lambda message: message.text == CHECK_STATUS_BTN)
async def ask_order_number(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BACK_BTN)]],
    resize_keyboard=True
    )

    await message.answer(
        "Введіть номер замовлення:",
        reply_markup=keyboard
    )

    await state.set_state(OrderStates.waiting_for_order_number)

