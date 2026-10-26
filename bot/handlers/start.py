import html
import re

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message

from bot.constants import INTERNATIONAL_ROUTE, LOCAL_ROUTE, START_MESSAGE, STATUS_MAP
from bot.handlers.status import is_rate_limited
from bot.keyboards.main import main_keyboard
from bot.services.order import save_bot_user, subscribe_chat_to_order

router = Router()

ORDER_CODE = re.compile(r"^MTL-[A-Z0-9]{4,10}$")


async def _remember_user(message: Message) -> None:
    username = message.from_user.username
    if username:
        await save_bot_user(username, message.from_user.id)


# Deep link from the website's order-confirmed screen:
# t.me/metallurgTm_bot?start=MTL-XXXXXX → follow that order's status.
# Registered before the plain /start handler, which would also match.
@router.message(CommandStart(deep_link=True))
async def start_with_order(message: Message, command: CommandObject):
    await _remember_user(message)
    code = (command.args or "").strip().upper()
    if not ORDER_CODE.match(code):
        await start(message)
        return

    if is_rate_limited(message.chat.id):
        await message.answer(
            "<b>// TOO_MANY_ATTEMPTS</b>\n\nPlease wait a few minutes and try again.",
            reply_markup=main_keyboard(),
        )
        return

    try:
        result, order = await subscribe_chat_to_order(code, message.chat.id)
    except Exception:
        await message.answer(
            "<b>// SYSTEM_ERROR</b>\n\nCould not link the order right now. Try the link again in a minute.",
            reply_markup=main_keyboard(),
        )
        return

    safe_code = html.escape(code)
    if result == "missing":
        text = f"<b>// ERROR_404</b>\n\nOrder <code>{safe_code}</code> was not found."
    elif result == "taken":
        text = (
            f"<b>// ACCESS_DENIED</b>\n\nOrder <code>{safe_code}</code> already sends updates "
            "to another Telegram account. Press [ CONTACT_OPERATOR ] if this is your order."
        )
    else:
        route = LOCAL_ROUTE if order["shipping_zone"] == "Ukraine" else INTERNATIONAL_ROUTE
        idx = max(0, min(int(order["current_status_index"] or 0), len(route) - 1))
        lines = [
            "<b>// UPDATES_LINKED</b>",
            "",
            f"ORDER: <code>{safe_code}</code>",
            f"STATUS: {STATUS_MAP.get(order['status'], '[ UNKNOWN ]')}",
        ]
        if order["status"] != "cancelled":
            lines.append(f"STAGE: [ {route[idx]} ]")
        if order.get("tracking_number"):
            lines.append(f"TTN: <code>{html.escape(order['tracking_number'])}</code>")
        lines += ["", "You'll get a message here when the status changes or a TTN is assigned."]
        text = "\n".join(lines)

    await message.answer(text, reply_markup=main_keyboard())


@router.message(CommandStart())
async def start(message: Message):
    await _remember_user(message)
    await message.answer(
        START_MESSAGE.format(user_id=message.from_user.id),
        reply_markup=main_keyboard(),
    )
