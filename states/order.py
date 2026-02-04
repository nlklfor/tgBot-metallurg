from aiogram.fsm.state import StatesGroup, State


class OrderStates(StatesGroup):
    confirm_order = State()
    waiting_tracking_code = State()
