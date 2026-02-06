"""
Admin handlers module for managing orders and user notifications.

Provides admin commands for:
- Viewing and filtering orders
- Changing order status
- Notifying users about order updates
"""

from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_session
from models.enum import OrderStatus
from repositories.order import OrderRepository

from config import ADMINS, TOKEN

router = Router()


# ============================================================================
# States
# ============================================================================

class AdminStates(StatesGroup):
    """Admin FSM states for different admin operations."""
    
    # Set Status flow
    waiting_set_status_tracking_code = State()
    waiting_set_status_value = State()
    
    # Notify User flow
    waiting_notify_tracking_code = State()
    waiting_notify_message = State()
    
    # Order Info flow
    waiting_order_info_code = State()


# ============================================================================
# Utilities
# ============================================================================

def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    return user_id in ADMINS


async def check_admin_access(message: types.Message) -> bool:
    """Verify admin access and send denial message if not admin."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Доступ запрещён. Только администраторы могут использовать эту команду.")
        return False
    return True


# ============================================================================
# Admin Help Command
# ============================================================================

@router.message(Command("admin_help"))
async def admin_help_handler(message: types.Message):
    """Display all available admin commands."""
    if not await check_admin_access(message):
        return

    help_text = (
        "🛠️ КОМАНДЫ АДМИНИСТРАТОРА\n\n"
        "📋 Просмотр заказов:\n"
        "/orders - показать последние 20 заказов\n"
        "/order_info - получить информацию о заказе\n\n"
        "✏️ Управление заказами:\n"
        "/set_status - изменить статус заказа\n"
        "/notify_user - отправить сообщение пользователю\n\n"
        "📊 Статусы заказов:\n"
        "• CREATED - создан\n"
        "• PAID - оплачен\n"
        "• IN_TRANSIT - в пути\n"
        "• DELIVERED - доставлен\n"
        "• CANCELLED - отменён"
    )
    await message.answer(help_text)


# ============================================================================
# List Orders Command
# ============================================================================

@router.message(Command("orders"))
async def list_orders_handler(message: types.Message):
    """Display the last 20 orders with details."""
    if not await check_admin_access(message):
        return

    async for session in get_session():
        order_repo = OrderRepository(session)
        orders = await order_repo.get_last_orders(limit=20)

        if not orders:
            await message.answer("📦 Нет заказов в системе.")
            return

        response = "📦 ПОСЛЕДНИЕ 20 ЗАКАЗОВ\n" + "=" * 40 + "\n\n"
        for idx, order in enumerate(orders, 1):
            response += (
                f"{idx}. 🔑 Трек-код: {order.tracking_code}\n"
                f"   👤 ID пользователя: {order.user_id}\n"
                f"   📍 Статус: {order.status.value}\n"
                f"   ⏰ Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            )

        await message.answer(response)


# ============================================================================
# Order Info Command (FSM Flow)
# ============================================================================

@router.message(Command("order_info"))
async def order_info_start_handler(message: types.Message, state: FSMContext):
    """Start the order info flow."""
    if not await check_admin_access(message):
        return

    args = message.text.split(maxsplit=1)
    
    # If tracking code provided in command
    if len(args) == 2:
        tracking_code = args[1].strip()
        await _show_order_info(message, state, tracking_code)
    else:
        # Ask for tracking code
        await message.answer(
            "🔍 Введите tracking-код заказа:"
        )
        await state.set_state(AdminStates.waiting_order_info_code)


@router.message(AdminStates.waiting_order_info_code)
async def order_info_process_handler(message: types.Message, state: FSMContext):
    """Process the tracking code and show order info."""
    if not await check_admin_access(message):
        await state.clear()
        return

    tracking_code = message.text.strip()
    await _show_order_info(message, state, tracking_code)


async def _show_order_info(message: types.Message, state: FSMContext, tracking_code: str):
    """Helper function to display order information."""
    async for session in get_session():
        order_repo = OrderRepository(session)
        order = await order_repo.get_by_tracking_code(tracking_code)

        if not order:
            await message.answer(
                f"❌ Заказ с кодом {tracking_code} не найден."
            )
            await state.clear()
            return

        info = (
            f"📦 ИНФОРМАЦИЯ О ЗАКАЗЕ\n"
            f"{'=' * 40}\n\n"
            f"🔑 Трек-код: {order.tracking_code}\n"
            f"👤 ID пользователя: {order.user_id}\n"
            f"🏷️ ID товара: {order.product_id}\n"
            f"📍 Статус: {order.status.value}\n"
            f"⏰ Дата создания: {order.created_at.strftime('%d.%m.%Y %H:%M:%S')}\n"
        )
        await message.answer(info)
        await state.clear()


# ============================================================================
# Set Status Command (FSM Flow)
# ============================================================================

@router.message(Command("set_status"))
async def set_status_start_handler(message: types.Message, state: FSMContext):
    """Start the set status flow."""
    if not await check_admin_access(message):
        return

    args = message.text.split(maxsplit=1)
    
    # If both tracking code and status provided in command
    if len(args) == 2:
        parts = args[1].split()
        if len(parts) == 2:
            await _process_set_status(message, state, parts[0], parts[1].upper())
            return

    # Ask for tracking code
    await message.answer(
        "🔍 Введите tracking-код заказа:"
    )
    await state.set_state(AdminStates.waiting_set_status_tracking_code)


@router.message(AdminStates.waiting_set_status_tracking_code)
async def set_status_tracking_code_handler(message: types.Message, state: FSMContext):
    """Process tracking code and ask for new status."""
    if not await check_admin_access(message):
        await state.clear()
        return

    tracking_code = message.text.strip()
    
    # Verify order exists
    async for session in get_session():
        order_repo = OrderRepository(session)
        order = await order_repo.get_by_tracking_code(tracking_code)

        if not order:
            await message.answer(
                f"❌ Заказ с кодом {tracking_code} не найден."
            )
            await state.clear()
            return

    await state.update_data(tracking_code=tracking_code)
    
    # Show available statuses
    available_statuses = ", ".join([s.name for s in OrderStatus])
    await message.answer(
        f"📋 Выберите новый статус:\n{available_statuses}"
    )
    await state.set_state(AdminStates.waiting_set_status_value)


@router.message(AdminStates.waiting_set_status_value)
async def set_status_value_handler(message: types.Message, state: FSMContext):
    """Process the new status value."""
    if not await check_admin_access(message):
        await state.clear()
        return

    data = await state.get_data()
    tracking_code = data.get("tracking_code")
    new_status_str = message.text.strip().upper()

    await _process_set_status(message, state, tracking_code, new_status_str)


async def _process_set_status(message: types.Message, state: FSMContext, tracking_code: str, status_str: str):
    """Helper function to update order status."""
    try:
        status_enum = OrderStatus[status_str]
    except KeyError:
        available_statuses = ", ".join([s.name for s in OrderStatus])
        await message.answer(
            f"❌ Неверный статус. Доступные: {available_statuses}"
        )
        await state.clear()
        return

    async for session in get_session():
        order_repo = OrderRepository(session)
        order = await order_repo.update_order_status(tracking_code, status_enum)

        if not order:
            await message.answer(
                f"❌ Заказ с кодом {tracking_code} не найден."
            )
            await state.clear()
            return

        await message.answer(
            f"✅ Статус заказа {order.tracking_code} обновлен\n"
            f"Новый статус: {order.status.value}"
        )
        await state.clear()


# ============================================================================
# Notify User Command (FSM Flow)
# ============================================================================

@router.message(Command("notify_user"))
async def notify_user_start_handler(message: types.Message, state: FSMContext):
    """Start the notify user flow."""
    if not await check_admin_access(message):
        return

    args = message.text.split(maxsplit=1)
    
    # If tracking code provided in command
    if len(args) == 2:
        tracking_code = args[1].strip()
        await _prepare_notification(message, state, tracking_code)
    else:
        # Ask for tracking code
        await message.answer(
            "🔍 Введите tracking-код заказа:"
        )
        await state.set_state(AdminStates.waiting_notify_tracking_code)


@router.message(AdminStates.waiting_notify_tracking_code)
async def notify_user_tracking_code_handler(message: types.Message, state: FSMContext):
    """Process tracking code for notification."""
    if not await check_admin_access(message):
        await state.clear()
        return

    tracking_code = message.text.strip()
    await _prepare_notification(message, state, tracking_code)


async def _prepare_notification(message: types.Message, state: FSMContext, tracking_code: str):
    """Helper function to prepare notification flow."""
    async for session in get_session():
        order_repo = OrderRepository(session)
        order = await order_repo.get_by_tracking_code(tracking_code)

        if not order:
            await message.answer(
                f"❌ Заказ с кодом {tracking_code} не найден."
            )
            await state.clear()
            return

        await state.update_data(user_id=order.user_id, tracking_code=order.tracking_code)
        await message.answer(
            f"📝 Введите сообщение для пользователя (ID: {order.user_id}):"
        )
        await state.set_state(AdminStates.waiting_notify_message)


@router.message(AdminStates.waiting_notify_message)
async def notify_user_message_handler(message: types.Message, state: FSMContext):
    """Process the notification message."""
    if not await check_admin_access(message):
        await state.clear()
        return

    data = await state.get_data()
    user_id = data.get("user_id")
    tracking_code = data.get("tracking_code")
    user_message = message.text

    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"📦 Обновление по вашему заказу\n"
                f"Трек-код: {tracking_code}\n\n"
                f"{user_message}"
            )
        )
        await message.answer(
            f"✅ Сообщение успешно отправлено пользователю (ID: {user_id})"
        )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при отправке сообщения:\n{str(e)}"
        )

    await state.clear()
