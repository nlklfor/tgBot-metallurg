from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Проверить статус заказа",
                    callback_data="start_check_status",
                )
            ]
        ]
    )