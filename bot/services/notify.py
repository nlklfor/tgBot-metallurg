"""
"New in archive" alerts.

Every CHECK_INTERVAL: if products were added since the last check, message
everyone with drop_alerts on (at most once per NOTIFY_COOLDOWN). Both times
live in public.bot_state, so a restart neither re-sends nor misses a drop.
"""

import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from bot.constants import DROP_ALERT
from bot.keyboards.main import alert_keyboard
from bot.services.state import get_time, set_time
from bot.services.users import alert_recipients, mark_blocked
from database.connection import db

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 300  # seconds (5 minutes)
NOTIFY_COOLDOWN = 43200  # seconds (12 hours)
SEND_PAUSE = 0.05  # seconds between messages (Telegram allows ~30/s)

CHECKED_KEY = "drop_alert_checked_at"
SENT_KEY = "drop_alert_sent_at"


async def _has_new_products(since: datetime) -> bool:
    async with db() as conn:
        return await conn.fetchval("SELECT EXISTS (SELECT 1 FROM public.products WHERE created_at > $1)", since)


async def _send(bot: Bot, chat_id: int) -> bool:
    for attempt in (1, 2):
        try:
            await bot.send_message(chat_id, DROP_ALERT, reply_markup=alert_keyboard())
            return True
        except TelegramRetryAfter as e:
            if attempt == 2:
                break
            await asyncio.sleep(e.retry_after + 1)
        except TelegramForbiddenError:
            await mark_blocked(chat_id)  # blocked the bot: skip them from now on
            return False
        except Exception:
            logger.warning("Drop alert to %s failed", chat_id, exc_info=True)
            return False
    return False


async def broadcast(bot: Bot) -> int:
    sent = 0
    for chat_id in await alert_recipients():
        if await _send(bot, chat_id):
            sent += 1
        await asyncio.sleep(SEND_PAUSE)
    return sent


async def check_once(bot: Bot) -> None:
    now = datetime.now(timezone.utc)
    checked = await get_time(CHECKED_KEY)
    if checked is None:
        # First run ever: start counting from now, don't alert about old products.
        await set_time(CHECKED_KEY, now)
        return

    sent_at = await get_time(SENT_KEY)
    if sent_at and (now - sent_at).total_seconds() < NOTIFY_COOLDOWN:
        # Keep `checked` where it is: products added during the cooldown
        # still trigger an alert once it ends.
        return

    if await _has_new_products(checked):
        await set_time(SENT_KEY, now)
        n = await broadcast(bot)
        logger.info("Drop alert sent to %d chat(s)", n)
    await set_time(CHECKED_KEY, now)


async def start_notify_loop(bot: Bot) -> None:
    logger.info("Drop alert loop started (interval: %ss, cooldown: %ss)", CHECK_INTERVAL, NOTIFY_COOLDOWN)
    while True:
        try:
            await check_once(bot)
        except Exception:
            logger.exception("Error in drop alert loop")
        await asyncio.sleep(CHECK_INTERVAL)
