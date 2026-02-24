from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID

from app.infrastructure.database.session import get_db
from app.infrastructure.database.orm_models.order import OrderORM, OrderStatus
from app.infrastructure.database.orm_models.order_item import OrderItemORM
from app.infrastructure.database.orm_models.client import ClientORM
from app.infrastructure.database.orm_models.business_config import BusinessConfigORM
from app.application.schemas.order import Order, OrderCreate, OrderUpdate
from app.presentation.dependencies import get_current_user
from app.infrastructure.database.orm_models.user import UserORM
from app.application.services import pdf_service

router = APIRouter()

@router.get("/", response_model=List[Order])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    """Retrieve all orders for the current Shoper."""
    orders = db.query(OrderORM).filter(
        OrderORM.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return orders

@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    """Create a new order with auto-calculations."""
    # Validate client belongs to user
    client = db.query(ClientORM).filter(
        ClientORM.id == order_in.client_id,
        ClientORM.user_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    new_order = OrderORM(
        client_id=order_in.client_id,
        user_id=current_user.id,
        payment_bank=order_in.payment_bank,
        payment_method=order_in.payment_method,
        date=order_in.date,
        notes=order_in.notes,
        status=OrderStatus.PENDING
    )
    
    db.add(new_order)
    db.flush() # get new_order.id
    
    total_tax = 0.0
    total_commission = 0.0
    total_profit = 0.0
    total_amount = 0.0

    for item_in in order_in.items:
        base_price = item_in.base_price
        qty = item_in.quantity
        
        # Calculations per product
        tax_amount_per_unit = (base_price * (item_in.tax_percent / 100))
        tax_amount_total = tax_amount_per_unit * qty
        
        # Commission is usually on (base_price + tax), according to constraints
        price_with_tax = base_price + tax_amount_per_unit
        commission_per_unit = price_with_tax * (item_in.commission_percent / 100)
        commission_total = commission_per_unit * qty
        
        final_price = (base_price * qty) + tax_amount_total + commission_total
        profit_amount = commission_total # as simple rule
        
        new_item = OrderItemORM(
            order_id=new_order.id,
            name=item_in.name,
            base_price=base_price,
            tax_percent=item_in.tax_percent,
            commission_percent=item_in.commission_percent,
            quantity=qty,
            tax_amount=tax_amount_total,
            commission_amount=commission_total,
            final_price=final_price,
            profit_amount=profit_amount
        )
        db.add(new_item)
        
        total_tax += tax_amount_total
        total_commission += commission_total
        total_profit += profit_amount
        total_amount += final_price

    new_order.total_tax = total_tax
    new_order.total_commission = total_commission
    new_order.total_profit = total_profit
    new_order.total_amount = total_amount

    db.commit()
    db.refresh(new_order)
    return new_order

@router.patch("/{order_id}/status", response_model=Order)
def update_order_status(
    order_id: UUID,
    status_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    order = db.query(OrderORM).filter(
        OrderORM.id == order_id,
        OrderORM.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if status_update.status:
        order.status = status_update.status
    if status_update.notes:
        order.notes = status_update.notes
        
    db.commit()
    db.refresh(order)
    return order

@router.get("/{order_id}/pdf", response_class=Response)
def get_order_pdf(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    """Generate and return a PDF invoice for the given order."""
    order = db.query(OrderORM).filter(
        OrderORM.id == order_id,
        OrderORM.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    business = db.query(BusinessConfigORM).filter(BusinessConfigORM.user_id == current_user.id).first()
    if not business:
        business = BusinessConfigORM(user_id=current_user.id, business_name="My Shopper")

    # Serialize objects to dict for Jinja2 template
    order_data = {
        "id": str(order.id)[:8], # short ID
        "date": order.date.strftime("%Y-%m-%d") if order.date else "",
        "status": order.status.value,
        "payment_method": order.payment_method,
        "notes": order.notes,
        "total_tax": round(float(order.total_tax), 2),
        "total_commission": round(float(order.total_commission), 2),
        "total_amount": round(float(order.total_amount), 2),
        "items": [
            {
                "name": item.name,
                "quantity": item.quantity,
                "base_price": round(float(item.base_price), 2),
                "final_price": round(float(item.final_price), 2)
            }
            for item in order.items
        ]
    }
    
    business_data = {
        "business_name": business.business_name,
        "logo_url": business.logo_url,
        "contact_email": business.contact_email,
        "base_currency": business.base_currency
    }
    
    client_data = {
        "name": order.client.name,
        "last_name": order.client.last_name,
        "email": order.client.email,
        "address": order.client.address
    }
    
    pdf_bytes = pdf_service.generate_order_pdf(order_data, business_data, client_data)
    
    headers = {
        'Content-Disposition': f'attachment; filename="invoice_{order_data["id"]}.pdf"'
    }
    return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")
