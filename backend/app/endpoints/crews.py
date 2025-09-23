from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import schemas, models
from ..core.database_async import get_db
from .auth import get_current_user
from ..services import crew_service

router = APIRouter(prefix="/crews", tags=["crews"])

@router.get("", response_model=List[schemas.CrewRead])
async def list_crews(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> List[schemas.CrewRead]:
    """List all crews with pagination."""
    return await crew_service.get_crews(db, skip=skip, limit=limit)

@router.get("/{crew_id}", response_model=schemas.CrewRead)
async def get_crew(crew_id: int, db: AsyncSession = Depends(get_db)) -> schemas.CrewRead:
    """Get a crew by ID."""
    crew = await crew_service.get_crew(db, crew_id)
    if not crew:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crew not found")
    return crew

@router.post("", response_model=schemas.CrewRead, status_code=status.HTTP_201_CREATED)
async def create_crew(payload: schemas.CrewCreate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> schemas.CrewRead:
    """Create a new crew. Only superusers allowed."""
    if not getattr(current_user, "is_superuser", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return await crew_service.create_crew(db, payload)