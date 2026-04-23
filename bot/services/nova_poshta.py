import logging
import aiohttp
from config import SUPABASE_URL, SUPABASE_ANON_KEY

logger = logging.getLogger(__name__)


async def get_np_status(ttn: str) -> dict | None:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    url = f"{SUPABASE_URL}/functions/v1/nova-poshta-track"
    headers = {
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"ttn": ttn}, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                print("DEBUG NP response:", data)
                return data
    except Exception:
        return None
