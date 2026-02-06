import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.enum import OrderStatus


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    tracking_code: Mapped[str] = mapped_column(String(50), unique=True)
    user_id: Mapped[int] = mapped_column(nullable=False)

    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus), default=OrderStatus.CREATED, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    product = relationship("Product")


async def create_test_order():
    """Create a test order for testing status functionality"""
    from database import SessionLocal
    
    try:
        async with SessionLocal() as session:
            result = await session.execute(
                select(Order).where(Order.tracking_code == "TEST123456")
            )
            existing = result.scalars().first()
            
            if existing:
                return  
            
            test_order = Order(
                id=uuid.uuid4(),
                tracking_code="TEST123456",
                user_id=123456789,
                product_id="test_metal_001",
                status=OrderStatus.PAID,
            )
            session.add(test_order)
            await session.commit()
            print("✅ Test order created successfully")
    except Exception as e:
        print(f"❌ Error creating test order: {e}")
