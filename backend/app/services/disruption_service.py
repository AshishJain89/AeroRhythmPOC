from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import models, schemas
from typing import List

async def list_disruptions(db: AsyncSession, skip: int = 0, limit: int = 200) -> List[schemas.DisruptionRead]:
    result = await db.execute(select(models.Disruption).offset(skip).limit(limit))
    disruptions = result.scalars().all()
    return [schemas.DisruptionRead.model_validate(d) for d in disruptions]

async def create_disruption(db: AsyncSession, payload: schemas.DisruptionCreate) -> schemas.DisruptionRead:
    disruption = models.Disruption(**payload.model_dump())
    db.add(disruption)
    await db.commit()
    await db.refresh(disruption)
    # TODO: trigger recalculation, send notification, etc.
    return schemas.DisruptionRead.model_validate(disruption)
