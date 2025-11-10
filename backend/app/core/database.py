from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings
import os

# Use processed database URL from config (handles Railway PostgreSQL URLs and SSL)
DATABASE_URL = settings.database_url_processed

# Create engine with appropriate configuration
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    # PostgreSQL/TimescaleDB - use connection pooling for production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=settings.DEBUG
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


