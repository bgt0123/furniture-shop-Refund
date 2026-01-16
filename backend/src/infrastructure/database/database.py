"""Database connection and setup."""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Import all entities

# SQLite database URL
DATABASE_URL = "sqlite+aiosqlite:///./refund_service.db"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def create_tables():
    """Create database tables on application startup."""
    from src.domain.entities.customer import Customer
    from src.domain.entities.refund_case import RefundCase
    from src.domain.entities.refund_item import RefundItem
    from src.domain.entities.support_agent import SupportAgent
    from src.domain.entities.support_case import SupportCase

    async with engine.begin() as conn:
        await conn.run_sync(SupportCase.metadata.create_all)
        await conn.run_sync(RefundCase.metadata.create_all)
        await conn.run_sync(RefundItem.metadata.create_all)
        await conn.run_sync(Customer.metadata.create_all)
        await conn.run_sync(SupportAgent.metadata.create_all)


async def get_db_session():
    """Dependency to get database session."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
