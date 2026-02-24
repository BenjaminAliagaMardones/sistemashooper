from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import List, Optional
from app.infrastructure.database.orm_models.order import OrderStatus

# Shared Order Item properties
class OrderItemBase(BaseModel):
    name: str
    base_price: float
    tax_percent: float = 0.0
    commission_percent: float = 0.0
    quantity: int = 1

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemInDBBase(OrderItemBase):
    id: UUID
    order_id: UUID
    tax_amount: float
    commission_amount: float
    final_price: float
    profit_amount: float

    class Config:
        from_attributes = True

class OrderItem(OrderItemInDBBase):
    pass

# Shared Order properties
class OrderBase(BaseModel):
    payment_bank: Optional[str] = None
    payment_method: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    client_id: UUID
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_bank: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class OrderInDBBase(OrderBase):
    id: UUID
    client_id: UUID
    user_id: UUID
    status: OrderStatus
    total_tax: float
    total_commission: float
    total_profit: float
    total_amount: float
    created_at: datetime

    class Config:
        from_attributes = True

class Order(OrderInDBBase):
    items: List[OrderItem] = []
