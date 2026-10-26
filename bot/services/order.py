import json
import logging
from typing import Optional
from database.connection import get_connection

logger = logging.getLogger(__name__)


async def get_order_by_number(order_number: str) -> Optional[dict]:
    """
    Fetches a full order from Supabase (via direct Postgres connection)
    by order_number. Returns a dict or None if not found.
    """
    try:
        conn = await get_connection()
    except Exception:
        logger.exception("DB connection failed for get_order_by_number(%s)", order_number)
        raise
    try:
        row = await conn.fetchrow(
            """
            SELECT
                order_number,
                customer_name,
                contact,
                shipping_zone,
                city,
                np_branch,
                country,
                items,
                total_price,
                status,
                current_status_index,
                is_international,
                tracking_number,
                created_at
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
    except Exception:
        logger.exception("Query failed for order %s", order_number)
        raise
    finally:
        await conn.close()


async def save_bot_user(tg_username: str, chat_id: int) -> None:
    try:
        conn = await get_connection()
    except Exception:
        logger.exception("DB connection failed for save_bot_user(%s)", tg_username)
        return
    try:
        await conn.execute(
            """
            INSERT INTO public.bot_users (tg_username, chat_id)
            VALUES ($1, $2)
            ON CONFLICT (tg_username) DO UPDATE
              SET chat_id = EXCLUDED.chat_id
            """,
            tg_username.lower(),
            chat_id,
        )
    except Exception:
        logger.exception("Failed to save bot user %s", tg_username)
    finally:
        await conn.close()


async def subscribe_chat_to_order(order_number: str, chat_id: int) -> tuple[str, Optional[dict]]:
    """
    Links a Telegram chat to an order so the order-updates loop can message it.
    Returns (result, order) where result is one of:
      "ok"      — linked now (or this chat was already linked)
      "taken"   — another chat already follows this order
      "missing" — no such order
    The order code is the secret here, same as for tracking lookups; the first
    chat to claim an order keeps it.
    """
    conn = await get_connection()
    try:
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
        exists = await conn.fetchval(
            "SELECT 1 FROM public.orders WHERE order_number = $1", order_number
        )
        return ("taken" if exists else "missing"), None
    finally:
        await conn.close()
