from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import schemas, models
from ..core.database_async import get_db
from .auth import get_current_user
from ..services import disruption_service

router = APIRouter(prefix="/disruptions", tags=["disruptions"])

@router.get("", response_model=List[schemas.DisruptionRead])
async def list_disruptions(skip: int = 0, limit: int = 200, db: AsyncSession = Depends(get_db)) -> List[schemas.DisruptionRead]:
    """List all disruptions with pagination."""
    return await disruption_service.list_disruptions(db, skip, limit)

@router.post("", response_model=schemas.DisruptionRead, status_code=status.HTTP_201_CREATED)
async def create_disruption(payload: schemas.DisruptionCreate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> schemas.DisruptionRead:
    """Create a new disruption. Any authenticated user allowed."""
    return await disruption_service.create_disruption(db, payload)
