# app/core/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from .config import settings

# Ensure DATABASE_URL uses asyncpg dialect. If user provided a sync URL,
# convert it to async form.
_db_url = settings.DATABASE_URL
if _db_url.startswith("postgresql://") and "+asyncpg" not in _db_url: # type: ignore
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1) # type: ignore

ENGINE_ARGS = {
    "echo": False,
    "pool_pre_ping": True,
    # you can tune pool_size / max_overflow via create_async_engine's poolclass if needed
}

engine = create_async_engine(_db_url, **ENGINE_ARGS, future=True) # type: ignore

# async_sessionmaker returns AsyncSession instances
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base for declarative models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession and ensures it is closed.
    Use in endpoints: `db: AsyncSession = Depends(get_db)`
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """
    Initialize DB (create tables). Call at startup if desired.
    Example:
        @app.on_event("startup")
        async def on_startup():
            await init_db()
    """
    async with engine.begin() as conn:
        # run_sync allows using sync metadata.create_all against async engine
        await conn.run_sync(Base.metadata.create_all)
