import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.infrastructure.database.orm_models.base import Base

class OrderItemORM(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    
    name = Column(String, nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    tax_percent = Column(Numeric(5, 2), nullable=False, default=0.0)
    commission_percent = Column(Numeric(5, 2), nullable=False, default=0.0)
    quantity = Column(Integer, nullable=False, default=1)

    # Autocalculated
    tax_amount = Column(Numeric(10, 2), default=0.0)
    commission_amount = Column(Numeric(10, 2), default=0.0)
    final_price = Column(Numeric(10, 2), default=0.0)
    profit_amount = Column(Numeric(10, 2), default=0.0)

    # Relationships
    order = relationship("OrderORM", back_populates="items")
