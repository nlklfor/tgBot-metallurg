"""
Small key/value store in public.bot_state, so loop timestamps survive
restarts (Railway restarts the worker on every deploy).
"""

from datetime import datetime

from database.connection import db


async def get_time(key: str) -> datetime | None:
    async with db() as conn:
        return await conn.fetchval("SELECT value::timestamptz FROM public.bot_state WHERE key = $1", key)


async def set_time(key: str, value: datetime) -> None:
    async with db() as conn:
        await conn.execute(
            """
            INSERT INTO public.bot_state (key, value, updated_at) VALUES ($1, $2, now())
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()
            """,
            key,
            value.isoformat(),
        )
