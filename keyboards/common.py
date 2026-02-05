from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def back_to_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 В главное меню",
                    callback_data="go_start",
                )
            ]
        ]
    )