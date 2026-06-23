from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def tracking_keyboard(ttn: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="[ TRACK ON NP ]",
            url=f"https://novaposhta.ua/tracking/?cargo_number={ttn}",
        ),
    ]])
