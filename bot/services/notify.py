import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot
from database.connection import get_connection

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 300       # seconds (5 minutes)
NOTIFY_COOLDOWN = 43200    # seconds (12 hours)

NOTIFICATION_TEXT = (
    "<b>// NEW_ARCHIVE_UPDATE</b>\n\n"
    "New items have been added to the archive.\n"
    "Check them out before they're gone.\n\n"
    "<i>Status: AVAILABLE</i>"
)


async def _get_all_chat_ids() -> list[int]:
    conn = await get_connection()
    try:
        rows = await conn.fetch("SELECT chat_id FROM public.bot_users")
        return [row["chat_id"] for row in rows]
    finally:
        await conn.close()


async def _has_new_products(since: datetime) -> bool:
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT 1 FROM public.products WHERE created_at > $1 LIMIT 1",
            since,
        )
        return row is not None
    finally:
        await conn.close()


async def start_notify_loop(bot: Bot) -> None:
    last_checked = datetime.now(timezone.utc)
    last_notified: datetime | None = None
    logger.info("Notification loop started (interval: %ss, cooldown: %ss)", CHECK_INTERVAL, NOTIFY_COOLDOWN)

    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        try:
            now = datetime.now(timezone.utc)
            cooldown_passed = (
                last_notified is None
                or (now - last_notified).total_seconds() >= NOTIFY_COOLDOWN
            )

            if cooldown_passed and await _has_new_products(last_checked):
                last_checked = now
                last_notified = now
                chat_ids = await _get_all_chat_ids()
                logger.info("New products found — notifying %d users", len(chat_ids))
                for chat_id in chat_ids:
                    try:
                        await bot.send_message(chat_id, NOTIFICATION_TEXT)
                    except Exception:
                        logger.warning("Failed to send notification to %s", chat_id)
            else:
                last_checked = now
        except Exception:
            logger.exception("Error in notification loop")
