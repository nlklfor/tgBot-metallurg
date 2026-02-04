from aiogram import Router, types
from aiogram.filters import Command

from database import get_session
from models.enum import OrderStatus
from repositories.order import OrderRepository

from config import ADMINS

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


@router.message(Command("orders"))
async def list_orders_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Доступ запрещён.")
        return

    async for session in get_session():
        order_repo = OrderRepository(session)
        orders = await order_repo.get_last_orders(limit=10)

        if not orders:
            await message.answer("📦 Нет заказов.")
            return

        response = "📦 *Последние 10 заказов*:\n\n"
        for order in orders:
            response += (
                f"🔑 Трек-код: `{order.tracking_code}`\n"
                f"👤 Пользователь ID: {order.user_id}\n"
                f"📍 Статус: {order.status.value}\n\n"
            )

        await message.answer(response, parse_mode="Markdown")


@router.message(Command("set_status"))
async def set_status_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Доступ запрещён.")
        return

    parts = message.text.split()
    if len(parts) != 3:
        await message.answer(
            "❌ Неверный формат команды. Используйте: /set_status <tracking_code> <new_status>",
            parse_mode="Markdown",
        )
        return

    tracking_code = parts[1]
    new_status_str = parts[2]

    try:
        status_enum = OrderStatus(new_status_str.upper())
    except KeyError:
        await message.answer(
            "❌ Неверный статус заказа. Пожалуйста, используйте корректный статус."
        )
        return

    async for session in get_session():
        order_repo = OrderRepository(session)
        order = await order_repo.get_by_tracking_code(tracking_code)

        if not order:
            await message.answer("❌ Заказ с таким tracking-кодом не найден.")
            return

        order.status = status_enum
        await session.commit()

        await message.answer(
            f"✅ Статус заказа `{order.tracking_code}` обновлен ->: *{status_enum.value}*",
            parse_mode="Markdown",
        )
