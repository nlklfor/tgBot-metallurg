"""
Order status updates for customers who subscribed from the website
(t.me/metallurgTm_bot?start=MTL-XXXXXX → orders.customer_chat_id).

Every CHECK_INTERVAL seconds: find subscribed orders whose "<status>|<ttn>"
differs from orders.notified_state, message the chat, then store the new
state. Works no matter where the change came from (admin panel, Nova Poshta
waybill function, SQL).
"""

import asyncio
import html
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from bot.constants import INTERNATIONAL_ROUTE, LOCAL_ROUTE
from bot.keyboards.tracking import tracking_keyboard
from database.connection import get_connection

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 60  # seconds

SITE_ORDERS_URL = "https://metallurg.vercel.app/orders"

HEADLINES = {
    "waiting_for_payment": ("// PENDING_PAYMENT", "We're waiting for your payment."),
    "paid": ("// PAYMENT_CONFIRMED", "Payment received. Your object is being prepared."),
    "processing": ("// IN_PREPARATION", "Your object is being packed."),
    "shipped": ("// DISPATCHED", "Your object is on its way."),
    "completed": (
        "// ARCHIVED_SUCCESSFULLY",
        "Delivered. Thank you for being part of the archive.",
    ),
    "cancelled": (
        "// ORDER_CANCELLED",
        "This order was cancelled. Questions? Press [ CONTACT_OPERATOR ].",
    ),
}


def state_of(status: str, ttn: str | None) -> str:
    return f"{status}|{ttn or ''}"


def build_message(order: dict, prev_state: str | None) -> str:
    status = order["status"]
    ttn = order.get("tracking_number")
    prev_status, _, prev_ttn = (prev_state or "|").partition("|")

    if status == prev_status and ttn and ttn != prev_ttn:
        title, body = "// TTN_ASSIGNED", "Nova Poshta waybill created for your order."
    else:
        title, body = HEADLINES.get(status, ("// STATUS_UPDATE", "Your order status changed."))

    lines = [f"<b>{title}</b>", "", f"ORDER: <code>{html.escape(order['order_number'])}</code>", body]

    if status != "cancelled":
        route = LOCAL_ROUTE if order.get("shipping_zone") == "Ukraine" else INTERNATIONAL_ROUTE
        idx = max(0, min(int(order.get("current_status_index") or 0), len(route) - 1))
        lines.append(f"STAGE: [ {route[idx]} ]")
    if ttn and status != "cancelled":
        lines.append(f"TTN: <code>{html.escape(ttn)}</code>")
    if status == "completed":
        lines.append("")
        lines.append(f'Leave a field report: <a href="{SITE_ORDERS_URL}">ORDERS &amp; REVIEWS</a>')

    return "\n".join(lines)


async def _pending(limit: int = 50) -> list[dict]:
    conn = await get_connection()
    try:
        rows = await conn.fetch(
            """
            SELECT id, order_number, status::text AS status, tracking_number,
                   shipping_zone, current_status_index, customer_chat_id, notified_state
              FROM public.orders
             WHERE customer_chat_id IS NOT NULL
               AND notified_state IS DISTINCT FROM
                   status::text || '|' || coalesce(tracking_number, '')
             ORDER BY created_at
             LIMIT $1
            """,
            limit,
        )
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def _mark_sent(order_id, old_state: str | None, new_state: str) -> None:
    conn = await get_connection()
    try:
        # Only if nothing else touched it meanwhile (no double sends).
        await conn.execute(
            """
            UPDATE public.orders SET notified_state = $3
             WHERE id = $1 AND notified_state IS NOT DISTINCT FROM $2
            """,
            order_id,
            old_state,
            new_state,
        )
    finally:
        await conn.close()


async def process_once(bot: Bot) -> int:
    sent = 0
    for order in await _pending():
        new_state = state_of(order["status"], order.get("tracking_number"))
        ttn = order.get("tracking_number")
        markup = (
            tracking_keyboard(ttn)
            if ttn and order.get("shipping_zone") == "Ukraine" and order["status"] != "cancelled"
            else None
        )
        try:
            await bot.send_message(
                order["customer_chat_id"],
                build_message(order, order.get("notified_state")),
                reply_markup=markup,
                disable_web_page_preview=True,
            )
            sent += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            # Blocked the bot / chat gone: don't retry this state forever.
            logger.warning("Order %s: chat %s unreachable", order["order_number"], order["customer_chat_id"])
        except Exception:
            logger.exception("Order %s: send failed, will retry", order["order_number"])
            continue
        await _mark_sent(order["id"], order.get("notified_state"), new_state)
    return sent


async def start_order_updates_loop(bot: Bot) -> None:
    logger.info("Order updates loop started (interval: %ss)", CHECK_INTERVAL)
    while True:
        try:
            n = await process_once(bot)
            if n:
                logger.info("Order updates: sent %d message(s)", n)
        except Exception:
            logger.exception("Error in order updates loop")
        await asyncio.sleep(CHECK_INTERVAL)
