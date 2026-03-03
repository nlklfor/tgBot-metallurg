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
        "<b>[01] ДОСТАВКА:</b>\n"
        "Відправка здійснюється через express-протоколи (Нова Пошта).\n"
        "Термін: 1-3 робочих дні.\n\n"
        "<b>[02] ОБМІН ТА ПОВЕРНЕННЯ:</b>\n"
        "Можливий протягом 14 днів, якщо об'єкт зберіг свій первозданний стан.\n\n"
        "<b>[03] ОПЛАТА:</b>\n"
        "Secure transactions only. Картка або післяплата (накладений платіж).\n"
        "--------------------------------\n"
        "<i>Status: DATA_ACCESSIBLE</i>"
    )
    await message.answer(faq_text, reply_markup=main_keyboard())
