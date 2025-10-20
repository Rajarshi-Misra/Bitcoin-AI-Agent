from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from bitcoin_agent.db.session import get_db
from bitcoin_agent.services.auth_service import create_access_token, authenticate_user, get_current_user
from bitcoin_agent.services.user_service import create_user
from bitcoin_agent.services.conversation_service import (
    create_conversation, get_user_conversations, get_conversation, 
    get_conversation_history
)
from bitcoin_agent.services.vector_service import vector_service
from bitcoin_agent.agent import process_user_input
from bitcoin_agent.models.user import User

app = FastAPI(title="Bitcoin AI Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)
security = HTTPBearer()

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int

class PredictionRequest(BaseModel):
    crypto: str = "bitcoin"
    horizon_hours: int = 24

# Dependency to get current user
async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    user = get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Authentication Endpoints
@app.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user and return JWT token"""
    try:
        user = create_user(db, user_data)
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user_dependency)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "is_active": current_user.is_active
    }

# Chat Endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response"""
    
    # Create new conversation if none provided
    if not request.conversation_id:
        conversation = create_conversation(db, current_user.id)
        conversation_id = conversation.id
    else:
        # Verify conversation belongs to user
        conversation = get_conversation(db, request.conversation_id, current_user.id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation_id = request.conversation_id
    
    # Process user input with RAG
    response = process_user_input(request.message, db, conversation_id)
    
    return ChatResponse(response=response, conversation_id=conversation_id)

@app.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get all conversations for current user"""
    conversations = get_user_conversations(db, current_user.id)
    return [
        {
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "message_count": len(conv.messages)
        }
        for conv in conversations
    ]

@app.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get messages for a specific conversation"""
    conversation = get_conversation(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = get_conversation_history(db, conversation_id)
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at
        }
        for msg in reversed(messages)  # Return in chronological order
    ]

# RAG Endpoints
@app.get("/search")
async def search_documents(
    query: str,
    limit: int = 5,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Search documents using RAG"""
    chunks = vector_service.search_similar(db, query, limit)
    return [
        {
            "content": chunk,
            "document_title": chunk.document.title,
            "similarity_score": "N/A"
        }
        for chunk in chunks
    ]

# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Bitcoin AI Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }