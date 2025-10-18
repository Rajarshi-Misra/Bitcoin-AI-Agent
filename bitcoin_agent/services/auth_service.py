from datetime import datetime, timedelta
from jose import JWTError, jwt
from bitcoin_agent.config import settings
from typing import Optional
from bitcoin_agent.models.user import User
from bitcoin_agent.utils.password import verify_password
from sqlalchemy.orm import Session

def create_access_token(data: dict)->str:
    to_encode = data.copy()
    expire = datetime.utcnow()+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(to_encode, settings.SECRET_KEY)
    return encoded_token

def verify_token(token: str)->Optional[User]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        return payload
    except JWTError:
        return None
    
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):  # ← Use utility
        return None
    return user

def get_current_user(db: Session, token: str) -> Optional[User]:
    """Get current user from JWT token"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    user_id: int = payload.get("sub")
    if user_id is None:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user