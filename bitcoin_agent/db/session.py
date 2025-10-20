from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from bitcoin_agent.config import settings
from typing import Generator

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from bitcoin_agent.db.base import Base
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def enable_pgvector():
    """Enable pgvector extension in PostgreSQL"""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    print("✓ pgvector extension enabled")