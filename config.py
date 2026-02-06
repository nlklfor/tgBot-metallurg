import os
from dotenv import load_dotenv

load_dotenv()

_admins_str = os.getenv("ADMINS", "")
ADMINS = {int(admin_id.strip()) for admin_id in _admins_str.split(",") if admin_id.strip()}

DATABASE_URL = "sqlite+aiosqlite:///db.sqlite3"

TOKEN = os.getenv("BOT_TOKEN")