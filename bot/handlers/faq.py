from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.constants import FAQ_BTN, FAQ_MESSAGE
from bot.keyboards.main import main_keyboard

router = Router()


@router.message(Command("faq"))
@router.message(F.text == FAQ_BTN)
async def show_faq(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(FAQ_MESSAGE, reply_markup=main_keyboard(), disable_web_page_preview=True)
