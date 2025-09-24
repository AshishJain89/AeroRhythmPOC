from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

# Correct imports
from .. import models, schemas
from ..config import settings
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[models.User]:
        result = await db.execute(
            select(models.User).where(models.User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None
        
        if not AuthService.verify_password(password, str(user.hashed_password)):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    async def get_current_user(db: AsyncSession, token: str) -> models.User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username = payload.get("sub")
            if not isinstance(username, str):
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        result = await db.execute(
            select(models.User).where(models.User.username == username)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception
        return user

auth_service = AuthService()



# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from .. import models
# from ..core.security import verify_password
# from typing import Optional

# async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[models.User]:
#     result = await db.execute(select(models.User).where(models.User.username == username))
#     user = result.scalar_one_or_none()
#     if user and verify_password(password, user.hashed_password):
#         return user
#     return None

# async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
#     result = await db.execute(select(models.User).where(models.User.username == username))
#     return result.scalar_one_or_none()
