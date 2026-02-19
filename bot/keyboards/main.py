from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.constants import CHECK_STATUS_BTN, FAQ_BTN, CONTACT_BTN


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=CHECK_STATUS_BTN)],
            [KeyboardButton(text=FAQ_BTN)],
            [KeyboardButton(text=CONTACT_BTN)],
        ],
        resize_keyboard=True
    )
