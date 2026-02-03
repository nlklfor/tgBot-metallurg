from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Product

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_product_by_id(self, product_id: str) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()