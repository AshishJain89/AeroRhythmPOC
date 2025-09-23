from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import schemas, models
from ..core.database_async import get_db
from .auth import get_current_user
from ..services import flight_service

router = APIRouter(prefix="/flights", tags=["flights"])

@router.get("", response_model=List[schemas.FlightRead])
async def list_flights(skip: int = 0, limit: int = 500, db: AsyncSession = Depends(get_db)) -> List[schemas.FlightRead]:
    """List all flights with pagination."""
    return await flight_service.get_flights(db, skip=skip, limit=limit)

@router.get("/{flight_id}", response_model=schemas.FlightRead)
async def get_flight(flight_id: str, db: AsyncSession = Depends(get_db)) -> schemas.FlightRead:
    """Get a flight by ID."""
    flight = await flight_service.get_flight(db, flight_id)
    if not flight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flight not found")
    return flight

@router.post("", response_model=schemas.FlightRead, status_code=status.HTTP_201_CREATED)
async def create_flight(payload: schemas.FlightCreate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> schemas.FlightRead:
    """Create a new flight. Only superusers allowed."""
    if not getattr(current_user, "is_superuser", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return await flight_service.create_flight(db, payload)
