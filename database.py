from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from models import Base
from config import DATABASE_URL

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)