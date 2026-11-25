"""
Operator-only commands, allowed for the chat ids in OPERATOR_CHAT_IDS.
Anyone else sending them gets no answer.

/unlink MTL-XXXXXX — stop status updates for that order, so the right
customer can link it again from the website.
"""

import html

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.services.order import unlink_order
from bot.text import normalize_code
from config import OPERATOR_CHAT_IDS

router = Router()
router.message.filter(F.chat.id.in_(OPERATOR_CHAT_IDS))


@router.message(Command("unlink"))
async def unlink(message: Message, command: CommandObject):
    code = normalize_code(command.args)
    if not code:
        await message.answer("Usage: <code>/unlink MTL-XXXXXX</code>")
        return
    found = await unlink_order(code)
    if found:
        await message.answer(f"<b>// UNLINKED</b>\n\n<code>{code}</code> no longer sends updates to any chat.")
    else:
        await message.answer(f"<b>// ERROR_404</b>\n\nOrder <code>{html.escape(code)}</code> was not found.")
