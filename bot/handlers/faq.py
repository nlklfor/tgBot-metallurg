from aiogram import Router
from aiogram.types import Message
from bot.constants import FAQ_BTN
from bot.keyboards.main import main_keyboard

router = Router()


@router.message(lambda message: message.text == FAQ_BTN)
async def show_faq(message: Message):
    faq_text = (
        "<b>// MTLLRG // ARCHIVE_INFO</b>\n"
        "--------------------------------\n"
        "<b>[01] SHIPPING:</b>\n"
        "Dispatch via express protocols (Nova Post).\n"
        "Estimated delivery: 1-3 business days.\n\n"
        "<b>[02] EXCHANGES & RETURNS:</b>\n"
        "Available within 14 days if the item remains in its original condition.\n\n"
        "<b>[03] PAYMENT:</b>\n"
        "Secure transactions only. Card or cash on delivery (COD).\n"
        "--------------------------------\n"
        "<i>Status: DATA_ACCESSIBLE</i>"
    )
    await message.answer(faq_text, reply_markup=main_keyboard())
