import html
import logging
import time
from collections import defaultdict, deque

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.constants import (
    CHECK_STATUS_BTN,
    INVALID_CODE,
    LOOKUP_PROMPT,
    STATUS_MAP,
    SYSTEM_ERROR,
    TOO_MANY_ATTEMPTS,
    route_for,
    stage_index,
)
from bot.keyboards.main import main_keyboard
from bot.keyboards.tracking import tracking_keyboard
from bot.services.nova_poshta import get_np_status
from bot.services.order import get_order_by_number
from bot.states.orders import OrderStates
from bot.text import build_stepper, format_uah, mask_contact, mask_name, normalize_code

logger = logging.getLogger(__name__)
router = Router()

# Same limit as the website's track-order function: 8 lookups per 10 minutes,
# here per Telegram chat. Stops brute-forcing order codes through the bot.
# Kept in memory, so a restart resets it — fine at this scale.
LOOKUP_WINDOW_SEC = 10 * 60
LOOKUP_MAX_ATTEMPTS = 8
_lookups: dict[int, deque] = defaultdict(deque)


def is_rate_limited(chat_id: int) -> bool:
    now = time.monotonic()
    attempts = _lookups[chat_id]
    while attempts and now - attempts[0] > LOOKUP_WINDOW_SEC:
        attempts.popleft()
    if len(attempts) >= LOOKUP_MAX_ATTEMPTS:
        return True
    attempts.append(now)
    return False


def _np_block(ttn: str | None, np_data: dict | None, is_cancelled: bool) -> str:
    if is_cancelled:
        return ""
    if not ttn:
        return "\n\n<i>// TTN_NOT_ASSIGNED_YET</i>"
    safe_ttn = html.escape(ttn)
    if not np_data:
        return f"\n\n<b>// NOVA_POSHTA</b>\nTTN: <code>{safe_ttn}</code>\n<i>// NP_STATUS_UNAVAILABLE</i>"
    np_status = html.escape(str(np_data.get("status_raw") or np_data.get("status") or "—"))
    city = html.escape(str(np_data.get("city_recipient") or "—"))
    warehouse = html.escape(str(np_data.get("warehouse_recipient") or "—"))
    delivered_at = html.escape(str(np_data.get("actual_date") or np_data.get("scheduled_date") or "—")[:10])
    return (
        f"\n\n<b>// NOVA_POSHTA</b>\n"
        f"NP_STATUS: <b>{np_status}</b>\n"
        f"CITY: {city}\n"
        f"BRANCH: {warehouse}\n"
        f"DELIVERY: {delivered_at}\n"
        f"TTN: <code>{safe_ttn}</code>"
    )


def _items_block(items: list) -> str:
    lines = []
    for item in items or []:
        name = html.escape(str(item.get("name", "?")))
        size = html.escape(str(item.get("selectedSize", "?")))
        line = f"- {name} / {size} / {format_uah(item.get('price', 0))}"
        qty = item.get("cart_quantity", 1) or 1
        if qty > 1:
            line += f" ×{qty}"
        lines.append(line)
    return "\n".join(lines) if lines else "—"


def _address_block(order: dict, is_ukraine: bool) -> str:
    out = ""
    city, branch, country = order.get("city"), order.get("np_branch"), order.get("country")
    if not is_ukraine and country:
        out += f"\nCOUNTRY: {html.escape(country)}"
    if city:
        out += f"\nCITY: {html.escape(city)}"
    if is_ukraine and city and branch:
        out += f"\nBRANCH: {html.escape(branch)}"
    return out


async def send_report(message: Message, code: str) -> None:
    """Looks the order up and sends the tracking report. `code` is already normalized."""
    if is_rate_limited(message.chat.id):
        await message.answer(TOO_MANY_ATTEMPTS, reply_markup=main_keyboard())
        return

    try:
        order = await get_order_by_number(code)
    except Exception:
        logger.exception("get_order_by_number(%s) failed", code)
        await message.answer(SYSTEM_ERROR, reply_markup=main_keyboard())
        return

    if not order:
        await message.answer(
            f"<b>// ERROR_404</b>\n\nOrder <code>{code}</code> was not found.\n"
            "Double-check the code and try again.",
            reply_markup=main_keyboard(),
        )
        return

    is_ukraine = order.get("shipping_zone") == "Ukraine"
    is_cancelled = order.get("status") == "cancelled"
    route = route_for(order)
    if is_cancelled:
        # A cancelled order has no delivery to follow.
        current_stage = "CANCELLED"
        stepper = "<i>// ORDER_CANCELLED / no delivery in progress</i>"
    else:
        idx = stage_index(order, route)
        current_stage = route[idx]
        stepper = build_stepper(route, idx)

    ttn = order.get("tracking_number")
    np_data = await get_np_status(ttn) if ttn and not is_cancelled else None

    text = (
        f"<b>// TRACKING_REPORT: {code}</b>\n\n"
        f"STAGE: [ <b>{current_stage}</b> ]\n"
        f"STATUS: {STATUS_MAP.get(order.get('status', ''), '[ UNKNOWN ]')}\n\n"
        f"<b>// DELIVERY_PIPELINE</b>\n"
        f"{stepper}"
        f"{_np_block(ttn, np_data, is_cancelled)}\n\n"
        f"CUSTOMER: {html.escape(mask_name(order.get('customer_name')))}\n"
        f"CONTACT: {html.escape(mask_contact(order.get('contact')))}\n"
        f"ZONE: {html.escape(str(order.get('shipping_zone') or 'N/A'))}"
        f"{_address_block(order, is_ukraine)}\n\n"
        f"<b>// ORDER_ITEMS</b>\n"
        f"{_items_block(order.get('items'))}\n\n"
        f"TOTAL: {format_uah(order.get('total_price', 0))}"
    )
    # The NP button only makes sense for a Nova Poshta TTN (Ukraine).
    markup = tracking_keyboard(ttn) if ttn and is_ukraine and not is_cancelled else main_keyboard()
    await message.answer(text, reply_markup=markup)


@router.message(Command("track"))
async def track_command(message: Message, command: CommandObject, state: FSMContext):
    """/track MTL-XXXXXX looks it up at once; bare /track asks for the code."""
    if command.args:
        await state.clear()
        code = normalize_code(command.args)
        if not code:
            await message.answer(INVALID_CODE, reply_markup=main_keyboard())
            return
        await send_report(message, code)
        return
    await ask_order_number(message, state)


@router.message(F.text == CHECK_STATUS_BTN)
async def ask_order_number(message: Message, state: FSMContext):
    await message.answer(LOOKUP_PROMPT, reply_markup=main_keyboard())
    await state.set_state(OrderStates.waiting_for_order_number)


# Registered last (status router is included after the others in main.py), so
# menu buttons and commands still work while the bot waits for a code.
@router.message(OrderStates.waiting_for_order_number)
async def show_status(message: Message, state: FSMContext):
    code = normalize_code(message.text)
    if not code:
        # Stay in the lookup state so the next message can be the right code.
        await message.answer(INVALID_CODE, reply_markup=main_keyboard())
        return
    await state.clear()
    await send_report(message, code)


# Anything else typed outside a command: a bare order code is looked up right
# away; other text gets a pointer to the menu.
@router.message(F.text & ~F.text.startswith("/"))
async def free_text(message: Message):
    code = normalize_code(message.text)
    # Only when it clearly is a code (MTL prefix or a digit), so "thanks"
    # isn't looked up as MTL-THANKS.
    raw = message.text.strip().upper()
    if code and (raw.startswith("MTL") or any(ch.isdigit() for ch in raw)):
        await send_report(message, code)
        return
    await message.answer(
        "Use the menu below, or send an order code like <code>MTL-7K2QPX</code>.",
        reply_markup=main_keyboard(),
    )
