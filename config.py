import os
from dotenv import load_dotenv

load_dotenv()

_admins_str = os.getenv("ADMINS", "")
ADMINS = {int(admin_id.strip()) for admin_id in _admins_str.split(",") if admin_id.strip()}

DATABASE_URL = os.getenv("DATABASE_URL")
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")