from pydantic import BaseModel, HttpUrl
from uuid import UUID
from typing import Optional
from datetime import datetime

class BusinessConfigBase(BaseModel):
    business_name: Optional[str] = "My Shopper"
    logo_url: Optional[str] = None
    base_currency: Optional[str] = "USD"
    contact_email: Optional[str] = None

class BusinessConfigUpdate(BusinessConfigBase):
    pass

class BusinessConfigInDBBase(BusinessConfigBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BusinessConfig(BusinessConfigInDBBase):
    pass
