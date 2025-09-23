from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import models, schemas
from typing import List, Optional

async def get_crews(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[schemas.CrewRead]:
    result = await db.execute(select(models.Crew).offset(skip).limit(limit))
    crews = result.scalars().all()
    return [schemas.CrewRead.model_validate(c) for c in crews]

async def get_crew(db: AsyncSession, crew_id: int) -> Optional[schemas.CrewRead]:
    result = await db.execute(select(models.Crew).where(models.Crew.id == crew_id))
    crew = result.scalar_one_or_none()
    if crew:
        return schemas.CrewRead.model_validate(crew)
    return None

async def create_crew(db: AsyncSession, payload: schemas.CrewCreate) -> schemas.CrewRead:
    crew = models.Crew(**payload.model_dump())
    db.add(crew)
    await db.commit()
    await db.refresh(crew)
    return schemas.CrewRead.model_validate(crew)
