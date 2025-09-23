from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from .. import crud, models
from . import ml_model


def run_roster_generation(job_id: int, start_iso: str, end_iso: str) -> None:
    """
    Background worker that creates its own DB session, updates job status, runs the ML/GA generator,
    persists assignments, and updates job.result. Arguments passed as primitives because BackgroundTasks serializes them.
    """
    db: Session = SessionLocal()
    try:
        job = crud.get_job_by_id(db, job_id)
        if not job:
            return
        crud.update_job_status(db, job, status="RUNNING")

        # parse datetimes
        start = datetime.fromisoformat(start_iso)
        end = datetime.fromisoformat(end_iso)

        # call the ML/GA service (expected to return dict with 'assignments', 'ai_confidence', 'metrics')
        result = ml_model.generate_roster(db, start, end)

        assignments = result.get("assignments", [])
        persisted = []
        if assignments:
            # assignments expected as List of dicts compatible with RosterAssignmentsCreate
            persisted_objs = crud.bulk_create_roster_assignments(db, assignments)
            persisted_ids = [int(getattr(a, "id")) for a in persisted_objs]
        else:
            persisted_ids = []
        
        job_result = {
            "assignmentIds": persisted_ids,
            "aiConfidence": result.get("ai_confidence"),
            "metrics": result.get("metrics", {}),
        }

        crud.update_job_status(db, job, status="SUCCESS", result=job_result)
    except Exception as exc:  # keep specific exception handling in production
        try:
            job = crud.get_job_by_id(db, job_id)
            if job:
                crud.update_job_status(db, job, status="FAILED", error_message=str(exc))
        finally:
            db.rollback()
    finally:
        db.close()
