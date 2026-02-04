import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
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
