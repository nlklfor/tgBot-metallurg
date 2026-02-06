from sqlalchemy import Boolean, Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    title: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str] = mapped_column(String(255), nullable=True)

    price: Mapped[int] = mapped_column(Integer, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


async def create_test_product():
    """Create a test product for testing bot functionality"""
    from database import SessionLocal
    
    try:
        async with SessionLocal() as session:
            result = await session.execute(
                select(Product).where(Product.id == "test_metal_001")
            )
            existing = result.scalars().first()
            
            if existing:
                return  
            
            test_product = Product(
                id="test_metal_001",
                title="Тестовый металл",
                description="Металл для тестирования функционала бота",
                price=5000,
                is_active=True,
            )
            session.add(test_product)
            await session.commit()
            print("✅ Test product created successfully")
    except Exception as e:
        print(f"❌ Error creating test product: {e}")
