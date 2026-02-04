from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    title: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str] = mapped_column(String(255), nullable=True)

    price: Mapped[int] = mapped_column(Integer, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
