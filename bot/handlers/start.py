import html
import logging

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.constants import START_MESSAGE, STATUS_MAP, TOO_MANY_ATTEMPTS, route_for, stage_index
from bot.handlers.status import is_rate_limited
from bot.keyboards.main import main_keyboard
from bot.services.order import subscribe_chat_to_order
from bot.services.users import save_bot_user
from bot.text import normalize_code

logger = logging.getLogger(__name__)
router = Router()


async def _remember_user(message: Message) -> None:
    if message.chat.type == "private":
        await save_bot_user(message.chat.id, message.from_user.username)


# Deep link from the website's order-confirmed screen:
# t.me/metallurgTm_bot?start=MTL-XXXXXX → follow that order's status.
# Registered before the plain /start handler, which would also match.
@router.message(CommandStart(deep_link=True))
async def start_with_order(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    await _remember_user(message)
    code = normalize_code(command.args)
    if not code:
        await start(message, state)
        return

    if is_rate_limited(message.chat.id):
        await message.answer(TOO_MANY_ATTEMPTS, reply_markup=main_keyboard())
        return

    try:
        result, order = await subscribe_chat_to_order(code, message.chat.id)
    except Exception:
        logger.exception("subscribe_chat_to_order(%s) failed", code)
        await message.answer(
            "<b>// SYSTEM_ERROR</b>\n\nCould not link the order right now. Try the link again in a minute.",
            reply_markup=main_keyboard(),
        )
        return

    if result == "missing":
        text = f"<b>// ERROR_404</b>\n\nOrder <code>{code}</code> was not found."
    elif result == "taken":
        text = (
            f"<b>// ACCESS_DENIED</b>\n\nOrder <code>{code}</code> already sends updates "
            "to another Telegram account. Press [ CONTACT_OPERATOR ] if this is your order."
        )
    else:
        route = route_for(order)
        lines = [
            "<b>// UPDATES_LINKED</b>",
            "",
            f"ORDER: <code>{code}</code>",
            f"STATUS: {STATUS_MAP.get(order['status'], '[ UNKNOWN ]')}",
        ]
        if order["status"] != "cancelled":
            lines.append(f"STAGE: [ {route[stage_index(order, route)]} ]")
        if order.get("tracking_number"):
            lines.append(f"TTN: <code>{html.escape(order['tracking_number'])}</code>")
        lines += ["", "You'll get a message here when the status changes or a TTN is assigned."]
        text = "\n".join(lines)

    await message.answer(text, reply_markup=main_keyboard())


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await _remember_user(message)
    await message.answer(START_MESSAGE, reply_markup=main_keyboard(), disable_web_page_preview=True)
