from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database import get_session
from repositories.product import ProductRepository
from keyboards.order import confirm_order_keyboard
from states.order import OrderState

router = Router()


@router.message(CommandStart())
async def start_command_handler(message: types.Message, state: FSMContext):
    args = message.text.split()

    # /start без аргументов, отправляем приветственное сообщение
    if len(args) == 1:
        await message.answer(
            "Привет! 👋🏻\nПерейдите на сайт и выберите твоар для заказа."
        )
        return

    # /start <product_id>
    product_id = args[1]

    async for session in get_session():
        product_repo = ProductRepository(session)
        product = await product_repo.get_by_id(product_id)

        if not product or not product.is_active:
            await message.answer(
                "❌ Товар не найден или недоступен. Пожалуйста, выберите другой товар."
            )
            return

        text = (
            f"🛒 *{product.title}* \n\n"
            f"{product.description or ''}\n\n"
            f"💰 Цена: {product.price} UAH."
            f"Подтвердите покупку."
        )

        await message.answer(
            text=text,
            reply_markup=confirm_order_keyboard(),
            parse_mode="Markdown",
        )

        await state.update_data(product_id=product.id)
        await state.set_state(OrderState.confirm_order)
