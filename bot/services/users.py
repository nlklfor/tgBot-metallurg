"""
public.bot_users: everyone who opened the bot in a private chat.

Keyed by chat_id (= the Telegram user id in a private chat), so people without
an @username are included and a renamed account keeps its row.
drop_alerts — wants "new in archive" messages; blocked_at — set when Telegram
says the user blocked the bot, cleared when they write again.
"""

import logging

from database.connection import db

logger = logging.getLogger(__name__)


async def save_bot_user(chat_id: int, username: str | None) -> None:
    uname = username.lower() if username else None
    try:
        async with db() as conn:
            async with conn.transaction():
                if uname:
                    # A username can move to another account; free it first.
                    await conn.execute(
                        "UPDATE public.bot_users SET tg_username = NULL WHERE tg_username = $1 AND chat_id <> $2",
                        uname,
                        chat_id,
                    )
                await conn.execute(
                    """
                    INSERT INTO public.bot_users (chat_id, tg_username)
                    VALUES ($1, $2)
                    ON CONFLICT (chat_id) DO UPDATE
                      SET tg_username = EXCLUDED.tg_username,
                          blocked_at = NULL
                    """,
                    chat_id,
                    uname,
                )
    except Exception:
        logger.exception("Failed to save bot user %s", chat_id)


async def get_alerts(chat_id: int) -> bool:
    async with db() as conn:
        value = await conn.fetchval("SELECT drop_alerts FROM public.bot_users WHERE chat_id = $1", chat_id)
    return bool(value) if value is not None else True


async def set_alerts(chat_id: int, enabled: bool) -> None:
    async with db() as conn:
        await conn.execute(
            """
            INSERT INTO public.bot_users (chat_id, drop_alerts) VALUES ($1, $2)
            ON CONFLICT (chat_id) DO UPDATE SET drop_alerts = EXCLUDED.drop_alerts
            """,
            chat_id,
            enabled,
        )


async def alert_recipients() -> list[int]:
    async with db() as conn:
        rows = await conn.fetch(
            "SELECT chat_id FROM public.bot_users WHERE drop_alerts AND blocked_at IS NULL ORDER BY created_at"
        )
    return [r["chat_id"] for r in rows]


async def mark_blocked(chat_id: int) -> None:
    async with db() as conn:
        await conn.execute("UPDATE public.bot_users SET blocked_at = now() WHERE chat_id = $1", chat_id)
