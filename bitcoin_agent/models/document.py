from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from bitcoin_agent.db.base import Base, TimestampMixin
from typing import Optional

class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    doc_type: Mapped[str] = mapped_column(String(50))  # pdf, txt, etc.
    vector_collection: Mapped[str] = mapped_column(String(100), default="bitcoin_docs")
    chunk_count: Mapped[int] = mapped_column(default=0)