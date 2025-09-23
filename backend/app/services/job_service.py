from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import BackgroundTasks
from datetime import datetime
from .. import models, schemas
from ..services import ml_model
from typing import Any, Optional

async def create_roster_job(db: AsyncSession, start: datetime, end: datetime, background_tasks: BackgroundTasks) -> schemas.JobRead:
    job = models.Job(type="roster_generation", status="RUNNING")
    db.add(job)
    await db.commit()
    await db.refresh(job)
    # Run roster generation and persist assignments
    result = await ml_model.generate_roster(db, start, end)
    assignments = result.get("assignments", [])
    for a in assignments:
        assignment = models.RosterAssignment(
            crew_id=a["crew_id"],
            flight_id=a["flight_id"],
            start=a["start"],
            end=a["end"],
            position=a["position"],
            attributes=a.get("metadata", {})
        )
        db.add(assignment)
    job.status = "SUCCESS"
    job.result = result
    await db.commit()
    await db.refresh(job)
    return schemas.JobRead.model_validate(job, from_attributes=True)

async def get_job_by_id(db: AsyncSession, job_id: int) -> Optional[schemas.JobRead]:
    result = await db.execute(select(models.Job).where(models.Job.id == job_id))
    job = result.scalar_one_or_none()
    if job:
        return schemas.JobRead.model_validate(job, from_attributes=True)
    return None
