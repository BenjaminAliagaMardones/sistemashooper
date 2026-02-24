import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

# Add the parent directory to the path so we can import 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.orm_models.user import UserORM
from app.infrastructure.database.orm_models.business import BusinessConfigORM
from app.core.security import get_password_hash
from app.core.config import settings

def create_admin():
    print("=== Creating Initial Admin User ===")
    email = input("Enter admin email (e.g., admin@shopper.com): ")
    password = input("Enter admin password: ")
    business_name = input("Enter Business Name (e.g., Mi Shopper): ")

    # Connect to DB
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if user already exists
        user = db.query(UserORM).filter(UserORM.email == email).first()
        if user:
            print(f"User {email} already exists!")
            return

        # Create user
        new_user = UserORM(
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create an associated Business Configuration explicitly with the generated UUID, or default it
        # Note: the relationship might automatically generate this depending on our triggers, 
        # but let's safely ensure the minimum config exists so the frontend doesn't crash on /settings
        try:
            config = BusinessConfigORM(
                user_id=new_user.id,
                business_name=business_name,
                base_currency='USD',
                contact_email=email
            )
            db.add(config)
            db.commit()
        except Exception as e:
            # Maybe the DB trigger already created it, rollback this part safely
            db.rollback()
            print("Business config already existed or failed to create via script:", e)

        print(f"\n✅ Success! User '{email}' created.")
        print("You can now login in your frontend with these credentials.")

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
