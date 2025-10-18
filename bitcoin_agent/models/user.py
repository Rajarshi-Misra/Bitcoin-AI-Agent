from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bitcoin_agent.db.base import Base, TimestampMixing
# from bitcoin_agent.models.conversation import Conversation
from typing import List

class User(Base, TimestampMixing):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")# type: ignore