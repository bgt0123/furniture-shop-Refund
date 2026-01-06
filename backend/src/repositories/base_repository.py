from typing import Type, TypeVar, Generic, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from src.database import SessionLocal, get_db

# Generic type for repository
T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def create(self, entity: T) -> T:
        """Create a new entity"""
        with self.get_session() as session:
            session.add(entity)
            session.flush()
            session.refresh(entity)
            return entity

    def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID"""
        with self.get_session() as session:
            stmt = select(self.model).where(self.model.id == entity_id)
            result = session.execute(stmt)
            return result.scalars().first()

    def find_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Find all entities with pagination"""
        with self.get_session() as session:
            stmt = select(self.model).offset(skip).limit(limit)
            result = session.execute(stmt)
            return result.scalars().all()

    def update(self, entity_id: str, update_data: dict) -> Optional[T]:
        """Update entity by ID"""
        with self.get_session() as session:
            stmt = (
                update(self.model)
                .where(self.model.id == entity_id)
                .values(**update_data)
            )
            result = session.execute(stmt)
            if result.rowcount == 0:
                return None
            return self.find_by_id(entity_id)

    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        with self.get_session() as session:
            stmt = delete(self.model).where(self.model.id == entity_id)
            result = session.execute(stmt)
            return result.rowcount > 0

    def find_by_field(self, field_name: str, field_value: Any) -> Optional[T]:
        """Find entity by any field"""
        with self.get_session() as session:
            stmt = select(self.model).where(
                getattr(self.model, field_name) == field_value
            )
            result = session.execute(stmt)
            return result.scalars().first()

    def find_all_by_field(
        self, field_name: str, field_value: Any, skip: int = 0, limit: int = 100
    ) -> List[T]:
        """Find all entities by field with pagination"""
        with self.get_session() as session:
            stmt = (
                select(self.model)
                .where(getattr(self.model, field_name) == field_value)
                .offset(skip)
                .limit(limit)
            )
            result = session.execute(stmt)
            return result.scalars().all()

    def count(self) -> int:
        """Count all entities"""
        with self.get_session() as session:
            return session.query(self.model).count()


# Repository factory
def create_repository(model: Type[T]) -> BaseRepository[T]:
    """Factory function to create repository instances"""
    return BaseRepository(model)


# Dependency for getting database session
def get_db_session():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
