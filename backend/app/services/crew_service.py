from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .. import models, schemas
from typing import List, Optional

class CrewService:
    @staticmethod
    async def get_crews(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Crew]:
        result = await db.execute(
            select(models.Crew)
            .offset(skip)
            .limit(limit)
            .order_by(models.Crew.name)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_crew(db: AsyncSession, crew_id: int) -> Optional[models.Crew]:
        result = await db.execute(
            select(models.Crew)
            .where(models.Crew.id == crew_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_crew(db: AsyncSession, crew: schemas.CrewCreate) -> models.Crew:
        db_crew = models.Crew(**crew.model_dump())
        db.add(db_crew)
        await db.commit()
        await db.refresh(db_crew)
        return db_crew
    
    @staticmethod
    async def update_crew(db: AsyncSession, crew_id: int, crew_update: schemas.CrewCreate) -> Optional[models.Crew]:
        result = await db.execute(
            select(models.Crew)
            .where(models.Crew.id == crew_id)
        )
        db_crew = result.scalar_one_or_none()

        if db_crew:
            for field, value in crew_update.model_dump().items():
                setattr(db_crew, field, value)
            await db.commit()
            await db.refresh(db_crew)
        
        return db_crew
    
    @staticmethod
    async def delete_crew(db: AsyncSession, crew_id: int) -> bool:
        result = await db.execute(
            select(models.Crew)
            .where(models.Crew.id == crew_id)
        )
        db_crew = result.scalar_one_or_none()

        if db_crew:
            await db.delete(db_crew)
            await db.commit()
            return True
        return False
    
crew_service = CrewService()

# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from .. import models, schemas
# from typing import List, Optional

# async def get_crews(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[schemas.CrewRead]:
#     result = await db.execute(select(models.Crew).offset(skip).limit(limit))
#     crews = result.scalars().all()
#     return [schemas.CrewRead.model_validate(c) for c in crews]

# async def get_crew(db: AsyncSession, crew_id: int) -> Optional[schemas.CrewRead]:
#     result = await db.execute(select(models.Crew).where(models.Crew.id == crew_id))
#     crew = result.scalar_one_or_none()
#     if crew:
#         return schemas.CrewRead.model_validate(crew)
#     return None

# async def create_crew(db: AsyncSession, payload: schemas.CrewCreate) -> schemas.CrewRead:
#     crew = models.Crew(**payload.model_dump())
#     db.add(crew)
#     await db.commit()
#     await db.refresh(crew)
#     return schemas.CrewRead.model_validate(crew)
