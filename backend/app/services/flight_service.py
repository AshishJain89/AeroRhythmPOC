from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import models
from .. import schemas
from typing import List, Optional

class FlightService:
    @staticmethod
    async def get_flights(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Flight]:
        result = await db.execute(
            select(models.Flight)
            .offset(skip)
            .limit(limit)
            .order_by(models.Flight.scheduled_departure)
        )
        return result.scalars().all()

    @staticmethod
    async def get_flight(db: AsyncSession, flight_id: int) -> Optional[models.Flight]:
        result = await db.execute(
            select(models.Flight)
            .where(models.Flight.id == flight_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_flight(db: AsyncSession, flight: schemas.FlightCreate) -> models.Flight:
        db_flight = models.Flight(**flight.dict())
        db.add(db_flight)
        await db.commit()
        await db.refresh(db_flight)
        return db_flight

flight_service = FlightService()



# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from .. import models, schemas
# from typing import List, Optional

# async def get_flights(db: AsyncSession, skip: int = 0, limit: int = 500) -> List[schemas.FlightRead]:
#     result = await db.execute(select(models.Flight).offset(skip).limit(limit))
#     flights = result.scalars().all()
#     return [schemas.FlightRead.model_validate(f) for f in flights]

# async def get_flight(db: AsyncSession, flight_id: str) -> Optional[schemas.FlightRead]:
#     result = await db.execute(select(models.Flight).where(models.Flight.id == flight_id))
#     flight = result.scalar_one_or_none()
#     if flight:
#         return schemas.FlightRead.model_validate(flight)
#     return None

# async def create_flight(db: AsyncSession, payload: schemas.FlightCreate) -> schemas.FlightRead:
#     flight = models.Flight(**payload.model_dump())
#     db.add(flight)
#     await db.commit()
#     await db.refresh(flight)
#     return schemas.FlightRead.model_validate(flight)