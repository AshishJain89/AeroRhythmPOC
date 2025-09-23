from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import models
from ..core.security import verify_password
from typing import Optional

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.username == username))
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()
