from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.infrastructure.database.session import get_db
from app.infrastructure.database.orm_models.client import ClientORM
from app.application.schemas.client import Client, ClientCreate, ClientUpdate
from app.presentation.dependencies import get_current_user
from app.infrastructure.database.orm_models.user import UserORM

router = APIRouter()

@router.get("/", response_model=List[Client])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    """Retrieve all clients for the current Shoper."""
    clients = db.query(ClientORM).filter(ClientORM.user_id == current_user.id).offset(skip).limit(limit).all()
    return clients

@router.post("/", response_model=Client, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: ClientCreate,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    """Create a new client."""
    client = ClientORM(
        **client_in.model_dump(),
        user_id=current_user.id
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@router.get("/{client_id}", response_model=Client)
def read_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    """Get specific client."""
    client = db.query(ClientORM).filter(
        ClientORM.id == client_id,
        ClientORM.user_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put("/{client_id}", response_model=Client)
def update_client(
    client_id: UUID,
    client_in: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    """Update a client."""
    client = db.query(ClientORM).filter(
        ClientORM.id == client_id,
        ClientORM.user_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = client_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
        
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserORM = Depends(get_current_user)
):
    """Delete a client."""
    client = db.query(ClientORM).filter(
        ClientORM.id == client_id,
        ClientORM.user_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(client)
    db.commit()
    return None
