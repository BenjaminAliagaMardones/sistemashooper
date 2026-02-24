from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.infrastructure.database.session import get_db
from app.infrastructure.database.orm_models.user import UserORM
from app.application.schemas.token import Token
from app.core import security
from app.core.config import settings
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from app.infrastructure.database.orm_models.business import BusinessConfigORM

router = APIRouter()

class SetupAdminRequest(BaseModel):
    email: EmailStr
    password: str
    business_name: str

@router.post("/setup-admin", status_code=status.HTTP_201_CREATED)
def setup_first_admin(data: SetupAdminRequest, db: Session = Depends(get_db)):
    """
    Creates the first admin user securely.
    This endpoint ONLY works if there are NO users in the database.
    """
    if db.query(UserORM).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Setup already completed. At least one user exists."
        )

    # 1. Create the user
    new_user = UserORM(
        email=data.email,
        hashed_password=security.get_password_hash(data.password),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 2. Create default business config
    new_config = BusinessConfigORM(
        user_id=new_user.id,
        business_name=data.business_name,
        base_currency="USD",
        contact_email=data.email
    )
    db.add(new_config)
    db.commit()

    return {"message": f"Admin user {data.email} created successfully!"}


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(UserORM).filter(UserORM.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
