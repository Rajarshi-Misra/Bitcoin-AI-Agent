from sqlalchemy.orm import Session
from bitcoin_agent.models.conversation import Conversation
from bitcoin_agent.models.message import Message, MessageRole
from typing import List, Optional

def create_conversation(db: Session, user_id: int, title: Optional[str] = None) -> Conversation:
    conversation = Conversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_user_conversations(db: Session, user_id: int) -> List[Conversation]:
    return db.query(Conversation).filter(Conversation.user_id == user_id).all()

def get_conversation(db: Session, conversation_id: int, user_id: int) -> Optional[Conversation]:
    return db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()

def add_message(db: Session, conversation_id: int, role: MessageRole, content: str) -> Message:
    message = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_conversation_history(db: Session, conversation_id: int, limit: int = 50) -> List[Message]:
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).limit(limit).all()