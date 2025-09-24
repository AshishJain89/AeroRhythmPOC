from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from .. import models, schemas
from ..config import settings
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        
        if not user or not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    async def get_current_user(db: AsyncSession, token: str) -> models.User:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        result = await db.execute(
            select(models.User).where(models.User.username == username)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_create: schemas.UserCreate) -> models.User:
        # Check if user already exists
        result = await db.execute(
            select(models.User).where(models.User.username == user_create.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already registered")
        
        result = await db.execute(
            select(models.User).where(models.User.email == user_create.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = AuthService.get_password_hash(user_create.password)
        db_user = models.User(
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

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
