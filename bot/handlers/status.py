from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.orders import OrderStates
from bot.constants import BACK_BTN, CHECK_STATUS_BTN, FAQ_BTN, CONTACT_BTN, STATUS_MAP
from bot.keyboards.main import main_keyboard
from bot.keyboards.tracking import tracking_keyboard
from bot.services.order import get_order_by_number
from bot.services.nova_poshta import get_np_status

router = Router()

INTERNATIONAL_ROUTE = [
    "ORDER_ACCEPTED",
    "PROCESSING",
    "IN_TRANSIT_TO_HUB",
    "BORDER_CROSSING",
    "ARRIVED_IN_UKRAINE",
    "DELIVERED_TO_NP",
]

LOCAL_ROUTE = [
    "ORDER_ACCEPTED",
    "PACKING",
    "READY_FOR_PICKUP",
    "HANDED_TO_RESIDENT",
]


def build_stepper(route: list[str], current_index: int) -> str:
    lines = []
    for i, step in enumerate(route):
        if i < current_index:
            lines.append(f"▪️ <s>{step}</s>")       # completed
        elif i == current_index:
            lines.append(f"▶️ <b>{step}</b>")        # active
        else:
            lines.append(f"▫️ {step}")               # future
    return "\n".join(lines)


@router.message(lambda message: message.text == CHECK_STATUS_BTN)
async def ask_order_number(message: Message, state: FSMContext):
    await message.answer(
        "<b>// ORDER_LOOKUP_INITIATED</b>\n\n"
        "Enter your <b>[ORDER_ID]</b> below:\n"
        "Example: <code>MTL-1234</code>",
        reply_markup=main_keyboard(),
    )
    await state.set_state(OrderStates.waiting_for_order_number)


@router.message(OrderStates.waiting_for_order_number)
async def show_status(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Please send a text order number, e.g. <code>MTL-1234</code>")
        return

    if message.text in (BACK_BTN, CHECK_STATUS_BTN, FAQ_BTN, CONTACT_BTN):
        await state.clear()
        if message.text == FAQ_BTN:
            from bot.handlers.faq import show_faq
            await show_faq(message)
        elif message.text == CONTACT_BTN:
            from bot.handlers.contact import contact_manager
            await contact_manager(message)
        else:
            await message.answer("Select operational command:", reply_markup=main_keyboard())
        return

    order_number = message.text.strip().upper()
    try:
        order = await get_order_by_number(order_number)
    except Exception:
        await message.answer(
            "<b>// SYSTEM_ERROR</b>\n\n"
            "Database is temporarily unavailable.\n"
            "Please try again in a moment."
        )
        return

    if not order:
        await message.answer(
            "<b>// ERROR_404</b>\n\n"
            f"Order <code>{order_number}</code> was not found.\n"
            "Double-check your ID and try again.\n\n"
            "Format: <code>MTL-XXXX</code>",
        )
        return

    contact_field = (order.get("contact") or "").strip()
    requester_username = (message.from_user.username or "").lower()
    if contact_field.startswith("@"):
        order_username = contact_field.lstrip("@").lower()
        if requester_username and order_username != requester_username:
            await message.answer(
                "<b>// ACCESS_DENIED</b>\n\n"
                f"Order <code>{order_number}</code> does not belong to your account."
            )
            return

    is_international = order.get("is_international", False)
    current_index = order.get("current_status_index", 0)
    route = INTERNATIONAL_ROUTE if is_international else LOCAL_ROUTE
    current_stage = route[current_index] if current_index < len(route) else "UNKNOWN"
    stepper = build_stepper(route, current_index)

    ttn = order.get("tracking_number")
    np_data = await get_np_status(ttn) if ttn else None

    if ttn and np_data:
        np_status = np_data.get("status_raw") or np_data.get("status", "—")
        city = np_data.get("city_recipient", "—")
        warehouse = np_data.get("warehouse_recipient", "—")
        delivered_at = (np_data.get("actual_date") or np_data.get("scheduled_date") or "—")[:10]
        np_block = (
            f"\n\n<b>// NOVA_POSHTA_STATUS</b>\n"
            f"NP_STATUS: <b>{np_status}</b>\n"
            f"CITY: {city}\n"
            f"BRANCH: {warehouse}\n"
            f"DELIVERED: {delivered_at}\n"
            f"TTN: <code>{ttn}</code>"
        )
    elif ttn:
        np_block = (
            f"\n\n<b>// NOVA_POSHTA_STATUS</b>\n"
            f"TTN: <code>{ttn}</code>\n"
            f"<i>// NP_STATUS_UNAVAILABLE</i>"
        )
    else:
        np_block = "\n\n<i>// TTN_NOT_ASSIGNED_YET</i>"

    reply_markup = tracking_keyboard(ttn) if ttn else None

    items = order.get("items") or []
    items_lines = []
    for item in items:
        qty = item.get("cart_quantity", 1)
        line = f"  · {item.get('name', '?')} / {item.get('selectedSize', '?')} — {item.get('price', 0):,} UAH"
        if qty > 1:
            line += f" x{qty}"
        items_lines.append(line)
    items_block = "\n".join(items_lines) if items_lines else "  —"

    is_ukraine = order.get("is_international", False)
    city = order.get("city")
    np_branch = order.get("np_branch")
    delivery_address_block = ""
    if is_ukraine and city:
        delivery_address_block = f"\nCITY: {city}"
        if np_branch:
            delivery_address_block += f"\nBRANCH: {np_branch}"

    contact = order.get("contact", "—")

    await message.answer(
        f"<b>// TRACKING_REPORT: {order_number}</b>\n"
        f"\n"
        f"CURRENT_STAGE: [ <b>{current_stage}</b> ]\n"
        f"PAYMENT: {STATUS_MAP.get(order.get('status', ''), '[ UNKNOWN ]')}\n"
        f"\n"
        f"<b>// DELIVERY_PIPELINE</b>\n"
        f"{stepper}"
        f"{np_block}\n"
        f"\n"
        f"CUSTOMER: {order.get('customer_name', 'N/A')}\n"
        f"CONTACT: {contact}\n"
        f"ZONE: {order.get('shipping_zone', 'N/A')}"
        f"{delivery_address_block}\n"
        f"\n"
        f"<b>// ORDER_ITEMS</b>\n"
        f"{items_block}\n"
        f"\n"
        f"TOTAL: {order.get('total_price', 0):,} UAH",
        reply_markup=reply_markup,
    )

    await state.clear()
    await message.answer("// SELECT_NEXT_COMMAND:", reply_markup=main_keyboard())