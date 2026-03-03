from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from bot.constants import START_MESSAGE
from bot.keyboards.main import main_keyboard

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        START_MESSAGE.format(user_id=message.from_user.id),
        reply_markup=main_keyboard(),
    )
