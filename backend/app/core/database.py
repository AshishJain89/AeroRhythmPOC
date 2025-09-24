import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from .config import settings
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Database configuration using settings
DATABASE_URL = settings.database_url

# Create async engine with better configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_size=10,
    max_overflow=20,
    # Use NullPool for development to avoid connection issues
    poolclass=NullPool if settings.debug else None
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Test database connection with retry logic
async def test_connection(max_retries: int = 3, retry_delay: float = 2.0):
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                # Test basic connection
                await conn.execute("SELECT 1")
                
                # Create tables if they don't exist
                await conn.run_sync(Base.metadata.create_all)
                
            print(f"Database connection successful! (Attempt {attempt + 1})")
            return True
            
        except Exception as e:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"🔄 Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print("All connection attempts failed!")
                return False

# Graceful shutdown
async def close_engine():
    """Close the database engine gracefully"""
    await engine.dispose()
    print("Database engine closed gracefully!")


# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, Session
# from typing import Generator
# from .config import settings


# # Use a synchronous SQLAlchemy engine (compatible with psycopg2).
# # If you prefer async, switch to asyncpg + async engine and AsyncSession.
# ENGINE_ARGS = {
#     "echo": True,
#     "pool_pre_ping": True,
#     "pool_size": 10,
#     "max_overflow": 20,
#     "future": True,
#     # you can add connect_args={"options": "-c timezone=utc"} if needed
# }

# if settings.DATABASE_URL is None:
#     raise ValueError("DATABASE_URL is not set")

# engine = create_engine(settings.DATABASE_URL, **ENGINE_ARGS)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def get_db() -> Generator[Session, None, None]:
#     """
#     FastAPI dependency that yields a SQLAlchemy Session and ensures it is closed.
#     Use in endpoints: `db: Sessino = Depends(get_db)`
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
