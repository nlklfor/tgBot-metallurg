from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def confirm_order_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Купить",
                    callback_data="confirm_order"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="cancel_order"
                )
            ]
        ]
    )
    return keyboard