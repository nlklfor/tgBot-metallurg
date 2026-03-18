from typing import Optional
from database.connection import get_connection


async def get_order_by_number(order_number: str) -> Optional[dict]:
    """
    Fetches a full order from Supabase (via direct Postgres connection)
    by order_number. Returns a dict or None if not found.
    """
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            """
            SELECT
                order_number,
                customer_name,
                contact,
                shipping_zone,
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
    finally:
        await conn.close()


async def save_bot_user(tg_username: str, chat_id: int) -> None:
    """
    Saves or updates a Telegram user's chat_id mapped to their @username.
    Called on /start so we can send PDFs after order placement.
    """
    conn = await get_connection()
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
    finally:
        await conn.close()