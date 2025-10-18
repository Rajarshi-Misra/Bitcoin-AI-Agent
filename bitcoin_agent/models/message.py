from sqlalchemy import String, ForeignKey, Integer, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bitcoin_agent.db.base import Base, TimestampMixin
# from bitcoin_agent.models.conversation import Conversation
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(Base, TimestampMixin):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True)
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole))
    content: Mapped[str] = mapped_column(Text)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")# type: ignore