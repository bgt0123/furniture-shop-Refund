"""Database connection and setup."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.entities import Base

# SQLite database URL
DATABASE_URL = "sqlite:///./refund_service.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create database tables on application startup."""
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Dependency to get database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
