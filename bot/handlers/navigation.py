from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.main import main_keyboard
from bot.constants import BACK_BTN

router = Router()


@router.message(lambda message: message.text == BACK_BTN)
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вас вітає Metallurg Assistant 👋\n\nВиберіть дію:",
        reply_markup=main_keyboard()
    )
