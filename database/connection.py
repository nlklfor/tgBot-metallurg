"""
One asyncpg pool for the whole bot (opened in main.py, closed on shutdown).

statement_cache_size=0 because DATABASE_URL points at Supabase's pooler
(Supavisor, transaction mode), which can't keep prepared statements.
"""

from contextlib import asynccontextmanager

import asyncpg

from config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def init_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL, min_size=1, max_size=5, statement_cache_size=0
        )
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


@asynccontextmanager
async def db():
    """`async with db() as conn:` — borrows a connection from the pool."""
    pool = await init_pool()
    async with pool.acquire() as conn:
        yield conn
