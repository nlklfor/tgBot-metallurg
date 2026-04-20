CHECK_STATUS_BTN = "[ TRACK_MY_OBJECT ]"
FAQ_BTN = "[ FAQ ]"
CONTACT_BTN = "[ CONTACT_OPERATOR ]"
BACK_BTN = "[ BACK_TO_MENU ]"
START_MESSAGE = (
    "<b>[SYSTEM_BOOT]... OK</b>\n"
    "<b>[IDENTIFICATION_SUCCESSFUL]</b>\n\n"
    "Welcome to <b>MTL // PROTOCOL [v.2.026]</b>\n"
    "Terminal session: active\n"
    "User_ID: <code>{user_id}</code>\n"
    "--------------------------------\n"
    "Select operational command:"
)
STATUS_MAP = {
    "waiting_for_payment": "[ PENDING_PAYMENT ]",
    "paid": "[ PAYMENT_CONFIRMED ]",
    "processing": "[ IN_PREPARATION ]",
    "shipped": "[ DISPATCHED_TO_HUB ]",
    "completed": "[ ARCHIVED_SUCCESSFULLY ]",
}
