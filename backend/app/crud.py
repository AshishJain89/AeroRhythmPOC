from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from . import models
from .core import security


# -------------------------
# Users / Auth
# -------------------------
async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    username: str,
    password: str,
    email: Optional[str] = None,
    is_superuser: bool = False,
) -> models.User:
    hashed = security.get_password_hash(password)
    user = models.User(
        username=username, email=email, hashed_password=hashed, is_superuser=is_superuser
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[models.User]:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    # Pylance may think `user.hashed_password` is a Column; cast to str for type-checker
    hashed_password = cast(str, getattr(user, "hashed_password"))
    if not security.verify_password(password, hashed_password):
        return None
    return user


# -------------------------
# Crews
# -------------------------
async def get_crews(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Crew]:
    stmt = select(models.Crew).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_crew(db: AsyncSession, crew_id: int) -> Optional[models.Crew]:
    stmt = select(models.Crew).where(models.Crew.id == crew_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_crew(
    db: AsyncSession,
    *,
    employee_id: str,
    first_name: str,
    last_name: str,
    rank: str,
    base_airport: Optional[str] = None,
    hire_date: Optional[datetime] = None,
    seniority_number: int = 0,
    status: str = "active",
) -> models.Crew:
    crew = models.Crew(
        employee_id=employee_id,
        first_name=first_name,
        last_name=last_name,
        rank=rank,
        base_airport=base_airport,
        hire_date=hire_date,
        seniority_number=seniority_number,
        status=status,
    )
    db.add(crew)
    try:
        await db.commit()
        await db.refresh(crew)
    except IntegrityError:
        await db.rollback()
        raise
    return crew


# -------------------------
# Flights
# -------------------------
async def get_flights(db: AsyncSession, skip: int = 0, limit: int = 500) -> List[models.Flight]:
    stmt = select(models.Flight).order_by(models.Flight.departure).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_flight(db: AsyncSession, flight_id: str) -> Optional[models.Flight]:
    stmt = select(models.Flight).where(models.Flight.id == flight_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_flight(
    db: AsyncSession,
    *,
    id: str,
    flight_number: str,
    origin: str,
    destination: str,
    departure: datetime,
    arrival: datetime,
    aircraft: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> models.Flight:
    flight = models.Flight(
        id=id,
        flight_number=flight_number,
        origin=origin,
        destination=destination,
        departure=departure,
        arrival=arrival,
        aircraft=aircraft,
        attributes=attributes or {},
    )
    db.add(flight)
    try:
        await db.commit()
        await db.refresh(flight)
    except IntegrityError:
        await db.rollback()
        raise
    return flight


# -------------------------
# Roster Assignments
# -------------------------
async def get_roster_assignments(
    db: AsyncSession,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 1000,
) -> List[models.RosterAssignment]:
    stmt = (
        select(models.RosterAssignment)
        .options(joinedload(models.RosterAssignment.crew), joinedload(models.RosterAssignment.flight))
        .order_by(models.RosterAssignment.start)
    )

    if start and end:
        stmt = stmt.where(and_(models.RosterAssignment.start >= start, models.RosterAssignment.end <= end))
    elif start:
        stmt = stmt.where(models.RosterAssignment.end >= start)
    elif end:
        stmt = stmt.where(models.RosterAssignment.start <= end)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_assignments_for_crew(db: AsyncSession, crew_id: int) -> List[models.RosterAssignment]:
    stmt = select(models.RosterAssignment).where(models.RosterAssignment.crew_id == crew_id).order_by(
        models.RosterAssignment.start
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_roster_assignment(
    db: AsyncSession,
    *,
    crew_id: int,
    flight_id: str,
    start: datetime,
    end: datetime,
    position: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> models.RosterAssignment:
    assignment = models.RosterAssignment(
        crew_id=crew_id,
        flight_id=flight_id,
        start=start,
        end=end,
        position=position,
        attributes=attributes or {},
    )
    db.add(assignment)
    try:
        await db.commit()
        await db.refresh(assignment)
    except IntegrityError:
        await db.rollback()
        raise
    return assignment


async def bulk_create_roster_assignments(db: AsyncSession, assignments: List[Dict[str, Any]]) -> List[models.RosterAssignment]:
    """
    Efficiently insert many assignments. `assignments` is list of dicts matching RosterAssignment fields.
    """
    objs = [models.RosterAssignment(**a) for a in assignments]
    db.add_all(objs)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    for o in objs:
        await db.refresh(o)
    return objs


async def delete_roster_assignment(db: AsyncSession, assignment_id: int) -> bool:
    obj = await db.get(models.RosterAssignment, assignment_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True


# -------------------------
# Disruptions
# -------------------------
async def create_disruption(
    db: AsyncSession,
    *,
    disruption_type: str,
    affected: Dict[str, Any],
    severity: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> models.Disruption:
    d = models.Disruption(type=disruption_type, affected=affected or {}, severity=severity, attributes=attributes or {})
    db.add(d)
    try:
        await db.commit()
        await db.refresh(d)
    except IntegrityError:
        await db.rollback()
        raise
    return d


async def list_disruptions(db: AsyncSession, skip: int = 0, limit: int = 200) -> List[models.Disruption]:
    stmt = select(models.Disruption).order_by(models.Disruption.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


# -------------------------
# Metrics / Utilities
# -------------------------
async def count_uncovered_flights(db: AsyncSession, start: Optional[datetime] = None, end: Optional[datetime] = None) -> int:
    """
    Simple metric: flights within window that have zero assignments.
    """
    flight_q = select(models.Flight.id)
    if start and end:
        flight_q = flight_q.where(and_(models.Flight.departure >= start, models.Flight.arrival <= end))
    flight_result = await db.execute(flight_q)
    flight_ids = [r[0] for r in flight_result.all()]

    if not flight_ids:
        return 0

    assigned_q = select(func.count(func.distinct(models.RosterAssignment.flight_id))).where(
        models.RosterAssignment.flight_id.in_(flight_ids)
    )
    assigned_result = await db.execute(assigned_q)
    assigned_count = assigned_result.scalar() or 0
    return max(0, len(flight_ids) - int(assigned_count))


async def get_basic_metrics(db: AsyncSession, start: Optional[datetime] = None, end: Optional[datetime] = None) -> Dict[str, Any]:
    total_flights_q = select(func.count(models.Flight.id))
    if start and end:
        total_flights_q = total_flights_q.where(and_(models.Flight.departure >= start, models.Flight.arrival <= end))
    total_flights_result = await db.execute(total_flights_q)
    total_flights = total_flights_result.scalar() or 0

    uncovered = await count_uncovered_flights(db, start=start, end=end)

    util_q = select(func.count(models.RosterAssignment.id))
    if start and end:
        util_q = util_q.where(and_(models.RosterAssignment.start >= start, models.RosterAssignment.end <= end))
    total_assignments_result = await db.execute(util_q)
    total_assignments = total_assignments_result.scalar() or 0

    return {
        "total_flights": int(total_flights),
        "uncovered_flights": int(uncovered),
        "total_assignments": int(total_assignments),
    }


# -------------------------
# Job helpers
# -------------------------


async def create_job(db: AsyncSession, job_type: str) -> models.Job:
    job = models.Job(type=job_type, status="PENDING")
    db.add(job)
    try:
        await db.commit()
        await db.refresh(job)
    except IntegrityError:
        await db.rollback()
        raise
    return job


async def get_job_by_id(db: AsyncSession, job_id: int) -> Optional[models.Job]:
    return await db.get(models.Job, job_id)


async def update_job_status(
    db: AsyncSession,
    job: models.Job,
    *,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
) -> models.Job:
    job.status = status  # type: ignore
    if result is not None:
        job.result = result  # type: ignore
    if error_message is not None:
        job.error_message = error_message  # type: ignore
    # set completed_at when finished
    if status in ("SUCCESS", "FAILED"):
        job.completed_at = datetime.now(timezone.utc)  # type: ignore
    try:
        db.add(job)
        await db.commit()
        await db.refresh(job)
    except IntegrityError:
        await db.rollback()
        raise
    return job
