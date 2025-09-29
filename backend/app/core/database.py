import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

# Use SQLite for quick testing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./aerorhythm.db")

try:
    if DATABASE_URL.startswith("postgresql"):
        engine = create_async_engine(
            DATABASE_URL,
            echo=True,
            pool_pre_ping=True,
            future=True
        )
    else:
        # SQLite configuration
        engine = create_async_engine(
            DATABASE_URL,
            echo=True,
            connect_args={"check_same_thread": False},
            future=True
        )
except Exception as e:
    print(f"Database engine creation failed: {e}")
    # Fallback to SQLite
    DATABASE_URL = "sqlite+aiosqlite:///./aerorhythm.db"
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False},
        future=True
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

async def test_connection():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

async def init_db():
    """Intialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")


# Synchronous session for scripts and testing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Derive synchronous URL from the async one
SYNC_DATABASE_URL = DATABASE_URL.replace("+aiosqlite", "")

sync_engine_connect_args = {}
if "sqlite" in SYNC_DATABASE_URL:
    sync_engine_connect_args["check_same_thread"] = False

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    connect_args=sync_engine_connect_args,
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
