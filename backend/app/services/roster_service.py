from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime
from .. import models, schemas
from ..services import ml_model

async def get_roster_assignments(db: AsyncSession, start: Optional[datetime], end: Optional[datetime], skip: int = 0, limit: int = 1000) -> List[schemas.RosterAssignmentRead]:
    query = select(models.RosterAssignment)
    if start:
        query = query.where(models.RosterAssignment.start >= start)
    if end:
        query = query.where(models.RosterAssignment.end <= end)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    assignments = result.scalars().all()
    return [schemas.RosterAssignmentRead.model_validate(a) for a in assignments]

async def generate_roster(db: AsyncSession, start: datetime, end: datetime) -> schemas.GenerateRosterResponse:
    result = await ml_model.generate_roster(db, start, end)
    assignments = []
    for a in result.get("assignments", []):
        assignment = models.RosterAssignment(
            crew_id=a["crew_id"],
            flight_id=a["flight_id"],
            start=a["start"],
            end=a["end"],
            position=a["position"],
            attributes=a.get("metadata", {})
        )
        db.add(assignment)
        await db.flush()
        assignments.append(schemas.RosterAssignmentRead.model_validate(assignment))
    await db.commit()
    return schemas.GenerateRosterResponse(
        id=None,
        assignments=assignments,
        aiConfidence=result.get("ai_confidence"),
        metrics=result.get("metrics"),
    )

async def create_roster_assignment(db: AsyncSession, payload: schemas.RosterAssignmentCreate) -> schemas.RosterAssignmentRead:
    assignment = models.RosterAssignment(**payload.model_dump())
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return schemas.RosterAssignmentRead.model_validate(assignment)
