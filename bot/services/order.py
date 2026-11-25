import json
import logging
from typing import Optional

from database.connection import db

logger = logging.getLogger(__name__)


async def get_order_by_number(order_number: str) -> Optional[dict]:
    """Full order by order_number, or None. Raises if the DB is unreachable."""
    async with db() as conn:
        row = await conn.fetchrow(
            """
            SELECT order_number, customer_name, contact, shipping_zone, city,
                   np_branch, country, items, total_price, status::text AS status,
                   current_status_index, tracking_number, created_at
              FROM public.orders
             WHERE order_number = $1
             LIMIT 1
            """,
            order_number,
        )
    if row is None:
        return None
    result = dict(row)
    if isinstance(result.get("items"), str):
        result["items"] = json.loads(result["items"])
    return result


async def subscribe_chat_to_order(order_number: str, chat_id: int) -> tuple[str, Optional[dict]]:
    """
    Links a Telegram chat to an order so the order-updates loop can message it.
    Returns (result, order) where result is one of:
      "ok"      — linked now (or this chat was already linked)
      "taken"   — another chat already follows this order
      "missing" — no such order
    The order code is the secret here, same as for tracking lookups; the first
    chat to claim an order keeps it (the operator can /unlink it).
    """
    async with db() as conn:
        row = await conn.fetchrow(
            """
            UPDATE public.orders
               SET customer_chat_id = $2,
                   notified_state = status::text || '|' || coalesce(tracking_number, '')
             WHERE order_number = $1
               AND (customer_chat_id IS NULL OR customer_chat_id = $2)
         RETURNING order_number, status::text AS status, tracking_number,
                   shipping_zone, current_status_index
            """,
            order_number,
            chat_id,
        )
        if row is not None:
            return "ok", dict(row)
        exists = await conn.fetchval("SELECT 1 FROM public.orders WHERE order_number = $1", order_number)
    return ("taken" if exists else "missing"), None


async def unlink_order(order_number: str) -> bool:
    """Operator command: stop updates for an order. True if the order exists."""
    async with db() as conn:
        result = await conn.execute(
            "UPDATE public.orders SET customer_chat_id = NULL, notified_state = NULL WHERE order_number = $1",
            order_number,
        )
    return result.endswith(" 1")
