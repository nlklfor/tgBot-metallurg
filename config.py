import os
from dotenv import load_dotenv

load_dotenv()

# Parse admin IDs from comma-separated string in .env
# Example: ADMINS=123456789,987654321
_admins_str = os.getenv("ADMINS", "")
ADMINS = {int(admin_id.strip()) for admin_id in _admins_str.split(",") if admin_id.strip()}

DATABASE_URL = "sqlite+aiosqlite:///db.sqlite3"

TOKEN = os.getenv("BOT_TOKEN")