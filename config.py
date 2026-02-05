import os
from dotenv import load_dotenv

load_dotenv()

ADMINS = {
    748959905,  # Nikita
}

DATABASE_URL = "sqlite+aiosqlite:///db.sqlite3"

TOKEN = os.getenv("BOT_TOKEN")