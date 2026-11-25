"""/alerts and the [ MUTE_ALERTS ] / [ TURN_ON ] buttons."""

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.constants import ALERTS_OFF, ALERTS_ON, SYSTEM_ERROR
from bot.keyboards.main import alerts_toggle_keyboard
from bot.services.users import get_alerts, set_alerts

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("alerts"))
async def alerts_status(message: Message, state: FSMContext):
    await state.clear()
    try:
        enabled = await get_alerts(message.chat.id)
    except Exception:
        logger.exception("alerts_status failed")
        await message.answer(SYSTEM_ERROR)
        return
    await message.answer(ALERTS_ON if enabled else ALERTS_OFF, reply_markup=alerts_toggle_keyboard(enabled))


@router.callback_query(F.data.in_({"alerts:on", "alerts:off"}))
async def alerts_toggle(callback: CallbackQuery):
    enabled = callback.data == "alerts:on"
    try:
        await set_alerts(callback.message.chat.id, enabled)
    except Exception:
        logger.exception("alerts_toggle failed")
        await callback.answer("// SYSTEM_ERROR — try again", show_alert=True)
        return
    await callback.answer("DROP_ALERTS: ON" if enabled else "DROP_ALERTS: OFF")
    await callback.message.answer(
        ALERTS_ON if enabled else ALERTS_OFF, reply_markup=alerts_toggle_keyboard(enabled)
    )
