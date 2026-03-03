from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.main import main_keyboard
from bot.constants import BACK_BTN, START_MESSAGE

router = Router()


@router.message(lambda message: message.text == BACK_BTN)
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        START_MESSAGE.format(user_id=message.from_user.id), 
        reply_markup=main_keyboard()
    )
