import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.infrastructure.database.orm_models.base import Base

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PURCHASED = "PURCHASED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class OrderORM(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True) # Redundant but good for quick tenant filtering

    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_bank = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    date = Column(Date, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    # Autocalculated totals
    total_tax = Column(Numeric(10, 2), default=0.0)
    total_commission = Column(Numeric(10, 2), default=0.0)
    total_profit = Column(Numeric(10, 2), default=0.0)
    total_amount = Column(Numeric(10, 2), default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    client = relationship("ClientORM", back_populates="orders")
    items = relationship("OrderItemORM", back_populates="order", cascade="all, delete-orphan")
