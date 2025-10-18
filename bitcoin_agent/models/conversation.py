from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bitcoin_agent.db.base import Base, TimestampMixin
from typing import List, Optional

class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")# type: ignore
    messages: Mapped[List["Message"]] = relationship(# type: ignore
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )