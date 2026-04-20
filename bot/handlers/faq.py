from aiogram import Router
from aiogram.types import Message
from bot.constants import FAQ_BTN
from bot.keyboards.main import main_keyboard

router = Router()


@router.message(lambda message: message.text == FAQ_BTN)
async def show_faq(message: Message):
    faq_text = (
        "<b>// METALLURG // LOGISTICS_AND_SUPPORT</b>\n"
        "----------------------------------\n\n"
        "<b>[01] SHIPPING_LOGISTICS:</b>\n"
        "• <b>SECTOR_UA:</b> Nova Post (1-3 business days).\n"
        "• <b>SECTOR_INT:</b> EU Hub dispatch (7-14 days).\n"
        "<i>Tracking ID is assigned upon object release.</i>\n\n"
        "<b>[02] OBJECT_INTEGRITY:</b>\n"
        "Exchanges and returns are active for 14 days.\n"
        "Unit must retain <b>FACTORY_SEALS</b> and original housing.\n\n"
        "<b>[03] SETTLEMENT_SYSTEM:</b>\n"
        "Secure protocols only: Card, Cash on Delivery (COD),\n"
        "or encrypted Digital Assets.\n\n"
        "<b>[04] AUTHENTICITY:</b>\n"
        "Every item is registered with a unique serial number\n"
        "verified at <b>NODE_UA</b> or <b>BASE_CH</b>.\n\n"
        "----------------------------------\n"
        "<b>Status: SYSTEM_READY_FOR_DISPATCH</b>"
    )
    await message.answer(faq_text, reply_markup=main_keyboard(), parse_mode="HTML")
