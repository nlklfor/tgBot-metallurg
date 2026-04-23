from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def tracking_keyboard(ttn: str, order_number: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="[ ВІДСТЕЖИТИ НА НП ]",
            url=f"https://novaposhta.ua/tracking/?cargo_number={ttn}",
        ),
        InlineKeyboardButton(
            text="[ ДЕТАЛІ ЗАМОВЛЕННЯ ]",
            callback_data=f"order_details:{order_number}",
        ),
    ]])


def no_ttn_keyboard(order_number: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="[ ДЕТАЛІ ЗАМОВЛЕННЯ ]",
            callback_data=f"order_details:{order_number}",
        ),
    ]])
