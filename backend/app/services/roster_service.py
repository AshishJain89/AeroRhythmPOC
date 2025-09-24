from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .. import models, schemas
from datetime import date
from typing import List, Optional

class RosterService:
    @staticmethod
    async def get_roster_assignments(
        db: AsyncSession, 
        start: date, 
        end: date, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[models.Roster]:
        result = await db.execute(
            select(models.Roster)
            .options(selectinload(models.Roster.crew), selectinload(models.Roster.flight))
            .where(and_(
                models.Roster.assignment_date >= start,
                models.Roster.assignment_date <= end
            ))
            .offset(skip)
            .limit(limit)
            .order_by(models.Roster.assignment_date, models.Roster.report_time)
        )
        return result.scalars().all()

    @staticmethod
    async def create_roster_assignment(db: AsyncSession, roster: schemas.RosterCreate) -> models.Roster:
        db_roster = models.Roster(**roster.dict())
        db.add(db_roster)
        await db.commit()
        await db.refresh(db_roster)
        return db_roster

roster_service = RosterService()



# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from typing import List, Optional
# from datetime import datetime
# from .. import models, schemas
# from ..services import ml_model

# async def get_roster_assignments(db: AsyncSession, start: Optional[datetime], end: Optional[datetime], skip: int = 0, limit: int = 1000) -> List[schemas.RosterAssignmentRead]:
#     query = select(models.RosterAssignment)
#     if start:
#         query = query.where(models.RosterAssignment.start >= start)
#     if end:
#         query = query.where(models.RosterAssignment.end <= end)
#     query = query.offset(skip).limit(limit)
#     result = await db.execute(query)
#     assignments = result.scalars().all()
#     return [schemas.RosterAssignmentRead.model_validate(a) for a in assignments]

# async def generate_roster(db: AsyncSession, start: datetime, end: datetime) -> schemas.GenerateRosterResponse:
#     result = await ml_model.generate_roster(db, start, end)
#     assignments = []
#     for a in result.get("assignments", []):
#         assignment = models.RosterAssignment(
#             crew_id=a["crew_id"],
#             flight_id=a["flight_id"],
#             start=a["start"],
#             end=a["end"],
#             position=a["position"],
#             attributes=a.get("metadata", {})
#         )
#         db.add(assignment)
#         await db.flush()
#         assignments.append(schemas.RosterAssignmentRead.model_validate(assignment))
#     await db.commit()
#     return schemas.GenerateRosterResponse(
#         id=None,
#         assignments=assignments,
#         aiConfidence=result.get("ai_confidence"),
#         metrics=result.get("metrics"),
#     )

# async def create_roster_assignment(db: AsyncSession, payload: schemas.RosterAssignmentCreate) -> schemas.RosterAssignmentRead:
#     assignment = models.RosterAssignment(**payload.model_dump())
#     db.add(assignment)
#     await db.commit()
#     await db.refresh(assignment)
#     return schemas.RosterAssignmentRead.model_validate(assignment)
