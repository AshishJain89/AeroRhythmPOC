from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Any
from ..core.database_async import get_db
from .. import schemas
from ..services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/generate", response_model=schemas.JobRead, status_code=status.HTTP_202_ACCEPTED)
async def create_roster_job(start: datetime, end: datetime, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)) -> Any:
    """Create a roster generation job and schedule background task."""
    return await job_service.create_roster_job(db, start, end, background_tasks)

@router.get("/{job_id}", response_model=schemas.JobRead)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    """Get a job by ID."""
    job = await job_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job

    