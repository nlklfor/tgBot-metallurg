from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from bot.constants import CHECK_STATUS_BTN, CONTACT_BTN, FAQ_BTN
from config import SITE_URL


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=CHECK_STATUS_BTN)],
            [KeyboardButton(text=FAQ_BTN), KeyboardButton(text=CONTACT_BTN)],
        ],
        resize_keyboard=True,
    )


def alert_keyboard() -> InlineKeyboardMarkup:
    """Under each drop alert: open the shop, or switch alerts off."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="[ OPEN_INVENTORY ]", url=f"{SITE_URL}/inventory")],
        [InlineKeyboardButton(text="[ MUTE_ALERTS ]", callback_data="alerts:off")],
    ])


def alerts_toggle_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    if enabled:
        btn = InlineKeyboardButton(text="[ TURN_OFF ]", callback_data="alerts:off")
    else:
        btn = InlineKeyboardButton(text="[ TURN_ON ]", callback_data="alerts:on")
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])
