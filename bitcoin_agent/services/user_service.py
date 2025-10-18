from sqlalchemy.orm import Session
from bitcoin_agent.models.user import User
from bitcoin_agent.utils.password import hash_password
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    
    class Config:
        from_attributes = True

def create_user(db: Session, user_data: UserCreate) -> User:
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise ValueError("Email already registered")
    
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()