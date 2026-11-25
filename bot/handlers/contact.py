from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.constants import CONTACT_BTN, CONTACT_MESSAGE
from bot.keyboards.main import main_keyboard

router = Router()


@router.message(Command("contact"))
@router.message(F.text == CONTACT_BTN)
async def contact_manager(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(CONTACT_MESSAGE, reply_markup=main_keyboard())
