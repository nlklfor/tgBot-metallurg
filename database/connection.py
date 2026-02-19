import asyncpg
from config import DATABASE_URL


async def get_connection():
    return await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
