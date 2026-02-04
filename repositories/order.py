from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

import uuid

from models import Order, OrderStatus


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(
        self, user_id: int, product_id: str, tracking_code: str | None = None
    ) -> Order:
        if not tracking_code:
            tracking_code = str(uuid.uuid4().replace("-", "")[:10])
        new_order = Order(
            tracking_code=tracking_code,
            user_id=user_id,
            product_id=product_id,
            status=OrderStatus.CREATED,
        )
        self.session.add(new_order)
        await self.session.commit()
        await self.session.refresh(new_order)
        return new_order

    async def get_by_tracking_code(self, tracking_code: str) -> Order | None:
        result = await self.session.execute(
            select(Order).where(Order.tracking_code == tracking_code)
        )
        return result.scalar_one_or_none()

    async def update_order_status(
        self, tracking_code: str, new_status: OrderStatus
    ) -> Order | None:
        order = await self.get_by_tracking_code(tracking_code)
        if not order:
            return None
        order.status = new_status
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def get_last_orders(self, limit: int = 10):
        result = await self.session.execute(
            select(Order).order_by(Order.created_at.desc()).limit(limit)
        )
        return result.scalars().all()
