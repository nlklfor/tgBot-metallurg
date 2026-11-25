"""Pure text helpers (no Telegram, no DB) — covered by tests/test_text.py."""

import re

# Order codes look like MTL-7K2QPX. Older ones can be 4–10 characters.
_CODE = re.compile(r"^(?:MTL[\s\-_]*)?([A-Z0-9]{4,10})$")


def normalize_code(text: str | None) -> str | None:
    """'mtl-7k2qpx', 'MTL 7K2QPX', '7k2qpx' -> 'MTL-7K2QPX'. None if it isn't a code."""
    if not text:
        return None
    m = _CODE.match(text.strip().upper())
    return f"MTL-{m.group(1)}" if m else None


def mask_contact(contact: str | None) -> str:
    """@nikita_sl -> @nik***, +380671234567 -> +380*****4567."""
    if not contact:
        return "—"
    c = contact.strip()
    if c.startswith("@"):
        return c[:4] + "***"
    digits = [ch for ch in c if ch.isdigit()]
    if len(digits) >= 7:
        return c[:4] + "*****" + "".join(digits[-4:])
    return c[:2] + "***"


def mask_name(name: str | None) -> str:
    """Nikita Slieptsov -> Nikita S."""
    if not name or not name.strip():
        return "N/A"
    parts = name.split()
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} {parts[-1][0]}."


def build_stepper(route: list[str], current_index: int) -> str:
    """Done steps struck through, the current one bold, the rest plain."""
    lines = []
    for i, step in enumerate(route):
        if i < current_index:
            lines.append(f"■ <s>{step}</s>")
        elif i == current_index:
            lines.append(f"▸ <b>{step}</b>")
        else:
            lines.append(f"□ {step}")
    return "\n".join(lines)


def format_uah(amount) -> str:
    """7299 -> '7,299 UAH'."""
    try:
        return f"{int(amount):,} UAH"
    except (TypeError, ValueError):
        return "— UAH"
