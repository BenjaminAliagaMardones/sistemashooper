import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Shooper SaaS API"
    # To run locally: postgresql://devuser:devpassword@localhost:5432/shooper_db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://devuser:devpassword@localhost:5432/shooper_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    class Config:
        case_sensitive = True

settings = Settings()
