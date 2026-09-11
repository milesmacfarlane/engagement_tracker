"""Database configuration and initialization."""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5433/engagement_tracker"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to False in production
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=0,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()

async def init_db():
    """Initialize database tables."""
    # Import models to register them with Base
    from app.models import User, Student, Class, Observation

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Get database session for dependency injection."""
    async with async_session() as session:
        yield session
