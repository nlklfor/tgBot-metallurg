from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from bot.constants import START_MESSAGE
from bot.keyboards.main import main_keyboard
from bot.services.order import save_bot_user

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    username = message.from_user.username
    if username:
        await save_bot_user(username, message.from_user.id)

    await message.answer(
        START_MESSAGE.format(user_id=message.from_user.id),
        reply_markup=main_keyboard(),
    )