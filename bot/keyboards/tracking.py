from urllib.parse import quote

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def tracking_keyboard(ttn: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="[ TRACK_ON_NP ]",
            url=f"https://novaposhta.ua/tracking/?cargo_number={quote(ttn)}",
        ),
    ]])
