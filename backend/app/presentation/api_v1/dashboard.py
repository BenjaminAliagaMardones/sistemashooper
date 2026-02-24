from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any, List
from datetime import datetime

from app.infrastructure.database.session import get_db
from app.infrastructure.database.orm_models.order import OrderORM
from app.infrastructure.database.orm_models.client import ClientORM
from app.presentation.dependencies import get_current_user
from app.infrastructure.database.orm_models.user import UserORM

router = APIRouter()

@router.get("/metrics", response_model=Dict[str, Any])
def get_dashboard_metrics(
    month: int = None,
    year: int = None,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    if not month:
        month = datetime.now().month
    if not year:
        year = datetime.now().year
        
    # Aggregate queries
    orders_query = db.query(OrderORM).filter(
        OrderORM.user_id == current_user.id
        # Note: Proper date filtering requires extract() from SQLAlchemy, 
        # simplifying here to show structure. Needs SQLAlchemy extract('month', OrderORM.date) == month
    )
    
    # Simple workaround for date
    orders = orders_query.all()
    filtered_orders = [o for o in orders if o.date and o.date.month == month and o.date.year == year]

    total_revenue = sum(o.total_amount for o in filtered_orders)
    total_profit = sum(o.total_profit for o in filtered_orders)
    order_count = len(filtered_orders)
    ticket_promedio = (total_revenue / order_count) if order_count > 0 else 0.0

    return {
        "month": month,
        "year": year,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "order_count": order_count,
        "ticket_promedio": ticket_promedio
    }

@router.get("/best-clients", response_model=List[Dict[str, Any]])
def get_best_clients(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    # This requires a JOIN and GROUP BY
    results = db.query(
        ClientORM,
        func.count(OrderORM.id).label("total_orders"),
        func.sum(OrderORM.total_amount).label("total_spent")
    ).outerjoin(
        OrderORM, ClientORM.id == OrderORM.client_id
    ).filter(
        ClientORM.user_id == current_user.id
    ).group_by(
        ClientORM.id
    ).order_by(
        desc("total_spent")
    ).limit(limit).all()

    best_clients = []
    for client, count, spent in results:
        best_clients.append({
            "client_id": client.id,
            "name": f"{client.name} {client.last_name}",
            "email": client.email,
            "total_orders": count or 0,
            "total_spent": float(spent) if spent else 0.0
        })
        
    return best_clients
