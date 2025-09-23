from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings

# Use a synchronous SQLAlchemy engine (compatible with psycopg2).
# If you prefer async, switch to asyncpg + async engine and AsyncSession.
ENGINE_ARGS = {
    "echo": True,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
    "future": True,
    # you can add connect_args={"options": "-c timezone=utc"} if needed
}

if settings.DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set")

engine = create_engine(settings.DATABASE_URL, **ENGINE_ARGS)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy Session and ensures it is closed.
    Use in endpoints: `db: Sessino = Depends(get_db)`
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
