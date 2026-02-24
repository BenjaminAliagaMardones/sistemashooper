from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.infrastructure.database.session import get_db
from app.infrastructure.database.orm_models.business_config import BusinessConfigORM
from app.application.schemas.business_config import BusinessConfig, BusinessConfigUpdate
from app.presentation.dependencies import get_current_user
from app.infrastructure.database.orm_models.user import UserORM

router = APIRouter()

@router.get("/", response_model=BusinessConfig)
def get_business_config(
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    """Retrieve or create business config for the current Shoper."""
    config = db.query(BusinessConfigORM).filter(
        BusinessConfigORM.user_id == current_user.id
    ).first()
    
    # Auto-create if not exists
    if not config:
        config = BusinessConfigORM(user_id=current_user.id)
        db.add(config)
        db.commit()
        db.refresh(config)
        
    return config

@router.put("/", response_model=BusinessConfig)
def update_business_config(
    config_in: BusinessConfigUpdate,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    """Update business config."""
    config = db.query(BusinessConfigORM).filter(
        BusinessConfigORM.user_id == current_user.id
    ).first()
    
    if not config:
        # Should normally exist by getting it first
        config = BusinessConfigORM(user_id=current_user.id)
        db.add(config)
    
    update_data = config_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
        
    db.commit()
    db.refresh(config)
    return config
