from config import SITE_URL

# Reply-keyboard buttons
CHECK_STATUS_BTN = "[ TRACK_MY_OBJECT ]"
FAQ_BTN = "[ FAQ ]"
CONTACT_BTN = "[ CONTACT_OPERATOR ]"

# Commands shown in Telegram's menu (set in main.py)
COMMANDS = [
    ("start", "Main menu"),
    ("track", "Track an order: /track MTL-XXXXXX"),
    ("faq", "Shipping, returns, payment"),
    ("contact", "Reach the operator"),
    ("alerts", "New-drop alerts on/off"),
]

# Style: WORD_WORD labels, "/" and "//" as separators, no emoji, no "·".
START_MESSAGE = (
    "<b>// ACCESS_GRANTED</b>\n\n"
    "METALLURG™ archive terminal.\n"
    "Track an order, read the FAQ or reach the operator from the menu below.\n\n"
    f'Archive: <a href="{SITE_URL}/inventory">OPEN_INVENTORY</a>'
)

FAQ_MESSAGE = (
    "<b>// FAQ</b>\n\n"
    "<b>01 / SHIPPING</b>\n"
    "Ukraine: Nova Poshta, 1–3 business days.\n"
    "International: 7–14 days.\n"
    "You get the TTN as soon as the object ships.\n\n"
    "<b>02 / RETURNS</b>\n"
    "Exchanges and returns within 14 days. The object must keep its factory tags and original box.\n\n"
    "<b>03 / PAYMENT</b>\n"
    "Card, cash on delivery or crypto.\n\n"
    "<b>04 / AUTHENTICITY</b>\n"
    "Every object is checked before it enters the archive.\n\n"
    f'Full terms: <a href="{SITE_URL}/protocol">PROTOCOL</a>'
)

CONTACT_MESSAGE = (
    "<b>// OPERATOR</b>\n\n"
    "@mtl_support / 24/7, replies as soon as possible.\n\n"
    "Include your order code (<code>MTL-XXXXXX</code>)."
)

LOOKUP_PROMPT = (
    "<b>// ORDER_LOOKUP</b>\n\n"
    "Send your order code.\n"
    "Example: <code>MTL-7K2QPX</code>"
)

INVALID_CODE = (
    "<b>// INVALID_CODE</b>\n\n"
    "That doesn't look like an order code.\n"
    "Format: <code>MTL-XXXXXX</code>"
)

TOO_MANY_ATTEMPTS = "<b>// TOO_MANY_ATTEMPTS</b>\n\nPlease wait a few minutes and try again."

SYSTEM_ERROR = "<b>// SYSTEM_ERROR</b>\n\nDatabase is temporarily unavailable. Try again in a moment."

DROP_ALERT = (
    "<b>// NEW_IN_ARCHIVE</b>\n\n"
    "New objects were added to the archive.\n"
    "Check them before they're gone."
)

ALERTS_ON = "<b>// DROP_ALERTS: ON</b>\n\nYou'll get a message when new objects land in the archive."
ALERTS_OFF = "<b>// DROP_ALERTS: OFF</b>\n\nNo more drop messages. Turn them back on with /alerts."

STATUS_MAP = {
    "waiting_for_payment": "[ PENDING_PAYMENT ]",
    "paid": "[ PAYMENT_CONFIRMED ]",
    "processing": "[ IN_PREPARATION ]",
    "shipped": "[ DISPATCHED_TO_HUB ]",
    "completed": "[ ARCHIVED_SUCCESSFULLY ]",
    "cancelled": "[ CANCELLED ]",
}

INTERNATIONAL_ROUTE = [
    "ORDER_ACCEPTED",
    "PROCESSING",
    "IN_TRANSIT_TO_HUB",
    "BORDER_CROSSING",
    "ARRIVED_IN_UKRAINE",
    "DELIVERED_TO_NP",
]

LOCAL_ROUTE = [
    "ORDER_ACCEPTED",
    "PACKING",
    "READY_FOR_PICKUP",
    "HANDED_TO_RESIDENT",
]


def route_for(order: dict) -> list[str]:
    return LOCAL_ROUTE if order.get("shipping_zone") == "Ukraine" else INTERNATIONAL_ROUTE


def stage_index(order: dict, route: list[str]) -> int:
    return max(0, min(int(order.get("current_status_index") or 0), len(route) - 1))
