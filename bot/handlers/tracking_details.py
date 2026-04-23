from aiogram import Router
from aiogram.types import CallbackQuery
from bot.services.order import get_order_by_number

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("order_details:"))
async def show_order_details(callback: CallbackQuery):
    order_number = callback.data.split(":", 1)[1]
    order = await get_order_by_number(order_number)

    if not order:
        await callback.answer("// ERROR_404: ORDER_NOT_FOUND", show_alert=True)
        return

    items = order.get("items") or []
    if not items:
        await callback.answer("// NO_ITEMS_REGISTERED", show_alert=True)
        return

    lines = [f"<b>// ITEMS_MANIFEST: {order_number}</b>\n"]
    for i, item in enumerate(items, 1):
        name = item.get("name", "N/A")
        size = item.get("selectedSize", "N/A")
        price = item.get("price", 0)
        lines.append(f"<b>[{i:02d}]</b> {name}\n     SIZE: {size} | PRICE: {price:,} UAH")

    lines.append(f"\n<b>TOTAL:</b> {order.get('total_price', 0):,} UAH")
    lines.append(f"<b>CUSTOMER:</b> {order.get('customer_name', 'N/A')}")

    await callback.message.answer("\n".join(lines))
    await callback.answer()
