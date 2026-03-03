from aiogram import Router
from aiogram.types import Message
from bot.constants import CONTACT_BTN
from bot.keyboards.main import main_keyboard

router = Router()


@router.message(lambda message: message.text == CONTACT_BTN)
async def contact_manager(message: Message):
    contact_text = (
        "<b>// CONNECTING_TO_HUMAN_INTERFACE...</b>\n\n"
        "Для вирішення технічних або логістичних питань звертайтесь до нашого оператора:\n\n"
        "<b>OPERATOR:</b> @mtl_support\n"
        "<b>AVAILABILITY:</b> 10:00 - 20:00\n\n"
        "<i>// При зверненні вказуйте свій [ORDER_ID]</i>"
    )
    await message.answer(contact_text, reply_markup=main_keyboard())
