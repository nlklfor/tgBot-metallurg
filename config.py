import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Website address used in every link the bot sends. Change it here (or in
# Railway → Variables) when the custom domain goes live.
SITE_URL = os.getenv("SITE_URL", "https://metallurg.vercel.app").rstrip("/")

# Telegram chat ids allowed to run operator commands (/unlink), comma-separated.
OPERATOR_CHAT_IDS = {
    int(x) for x in os.getenv("OPERATOR_CHAT_IDS", "").replace(" ", "").split(",") if x.lstrip("-").isdigit()
}
