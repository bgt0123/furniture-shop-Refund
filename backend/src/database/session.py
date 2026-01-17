from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Database base class
Base = declarative_base()

# Database engine
import os
from pathlib import Path

# Use absolute path to avoid multiple database files
db_path = Path(__file__).parent.parent.parent.parent / "support_refund.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database."""
    # Create all tables
    Base.metadata.create_all(engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
