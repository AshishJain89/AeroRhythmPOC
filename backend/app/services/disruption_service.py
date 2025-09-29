from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import models
from .. import schemas
from typing import List, Optional

class DisruptionService:
    @staticmethod
    async def list_disruptions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Disruption]:
        result = await db.execute(
            select(models.Disruption)
            .offset(skip)
            .limit(limit)
            .order_by(models.Disruption.start_time.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def create_disruption(db: AsyncSession, disruption: schemas.DisruptionCreate) -> models.Disruption:
        db_disruption = models.Disruption(**disruption.dict())
        db.add(db_disruption)
        await db.commit()
        await db.refresh(db_disruption)
        return db_disruption

disruption_service = DisruptionService()


# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from .. import models, schemas
# from typing import List

# async def list_disruptions(db: AsyncSession, skip: int = 0, limit: int = 200) -> List[schemas.DisruptionRead]:
#     result = await db.execute(select(models.Disruption).offset(skip).limit(limit))
#     disruptions = result.scalars().all()
#     return [schemas.DisruptionRead.model_validate(d) for d in disruptions]

# async def create_disruption(db: AsyncSession, payload: schemas.DisruptionCreate) -> schemas.DisruptionRead:
#     disruption = models.Disruption(**payload.model_dump())
#     db.add(disruption)
#     await db.commit()
#     await db.refresh(disruption)
#     # TODO: trigger recalculation, send notification, etc.
#     return schemas.DisruptionRead.model_validate(disruption)
