from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import models, schemas
from typing import List, Optional

async def get_flights(db: AsyncSession, skip: int = 0, limit: int = 500) -> List[schemas.FlightRead]:
    result = await db.execute(select(models.Flight).offset(skip).limit(limit))
    flights = result.scalars().all()
    return [schemas.FlightRead.model_validate(f) for f in flights]

async def get_flight(db: AsyncSession, flight_id: str) -> Optional[schemas.FlightRead]:
    result = await db.execute(select(models.Flight).where(models.Flight.id == flight_id))
    flight = result.scalar_one_or_none()
    if flight:
        return schemas.FlightRead.model_validate(flight)
    return None

async def create_flight(db: AsyncSession, payload: schemas.FlightCreate) -> schemas.FlightRead:
    flight = models.Flight(**payload.model_dump())
    db.add(flight)
    await db.commit()
    await db.refresh(flight)
    return schemas.FlightRead.model_validate(flight)