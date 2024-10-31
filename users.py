# users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal  # Import your database session
from models import User  # Import your User model
from schemas import UserCreate, UserOut  # Import your user schemas
from typing import List
from utils import trim_string
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise HTTPException(status_code=500, detail="Database session error")
    finally:
        db.close()

# Example endpoint for user registration
@router.post("/register", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Trim whitespace from relevant fields
    user.username = trim_string(user.username)

    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            logger.warning(f"Username already registered: {user.username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        new_user = User(**user.dict())  # Assuming your User model supports this
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User created successfully: {new_user.username}")
        return new_user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

# Get all users (admin only)
@router.get("/users/", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()  # Admin can see all users
        logger.info("Retrieved all users successfully")
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")
