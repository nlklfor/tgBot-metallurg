from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.connection import get_connection

router = Router()


STATUS_MAP = {
    "waiting_for_payment": "⏳ Ожидает оплаты",
    "paid": "✅ Оплачен",
    "processing": "📦 Готовится к отправке",
    "shipped": "🚚 Отправлен",
    "completed": "🎉 Завершён",
}


@router.message(Command("status"))
async def get_order_status(message: Message):
    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("Введите номер заказа:\n/status MTL-0001")
        return

    order_number = parts[1]

    try:
        conn = await get_connection()

        result = await conn.fetchrow(
            "SELECT status FROM orders WHERE order_number = $1", order_number
        )

        await conn.close()

        if not result:
            await message.answer("❌ Заказ не найден.")
            return

        raw_status = result["status"]
        pretty_status = STATUS_MAP.get(raw_status, raw_status)

        await message.answer(f"📦 Статус заказа {order_number}:\n\n" f"{pretty_status}")

    except Exception as e:
        await message.answer("⚠ Ошибка при проверке заказа.")
        print(e)
