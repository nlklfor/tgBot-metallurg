from aiogram.type import InlineKeyboardMarkup, InlineKeyboardButton

def check_status_keyboard(tracking_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Проверить статус заказа",
                    callback_data=f"check_status:{tracking_code}",
                )
            ]
        ]
    )