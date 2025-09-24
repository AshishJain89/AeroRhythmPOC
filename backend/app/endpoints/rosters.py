from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
from .. import schemas
from ..core.database import get_db
from ..services.roster_service import roster_service

router = APIRouter()

@router.get("/", response_model=List[schemas.Roster])
async def get_rosters(
    start: date = Query(..., description="Start date for roster period"),
    end: date = Query(..., description="End date for roster period"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    rosters = await roster_service.get_roster_assignments(db, start, end, skip, limit)
    return rosters

@router.post("/", response_model=schemas.Roster)
async def create_roster(roster: schemas.RosterCreate, db: AsyncSession = Depends(get_db)):
    return await roster_service.create_roster_assignment(db, roster)



# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List, Optional
# from datetime import datetime
# from .. import schemas, models
# from ..core.database_async import get_db
# from .auth import get_current_user
# from ..services import roster_service

# router = APIRouter(prefix="/rosters", tags=["rosters"])

# @router.get("", response_model=List[schemas.RosterAssignmentRead])
# async def get_rosters(start: Optional[datetime] = Query(None), end: Optional[datetime] = Query(None), skip: int = 0, limit: int = 1000, db: AsyncSession = Depends(get_db)) -> List[schemas.RosterAssignmentRead]:
#     """List roster assignments with optional date filtering."""
#     return await roster_service.get_roster_assignments(db, start, end, skip, limit)

# @router.post("/generate", response_model=schemas.GenerateRosterResponse)
# async def generate_roster(start: datetime, end: datetime, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> schemas.GenerateRosterResponse:
#     """Trigger roster generation using ML/GA service."""
#     return await roster_service.generate_roster(db, start, end)

# @router.post("/assignments", response_model=schemas.RosterAssignmentRead, status_code=status.HTTP_201_CREATED)
# async def create_assignment(payload: schemas.RosterAssignmentCreate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> schemas.RosterAssignmentRead:
#     """Create a new roster assignment."""
#     return await roster_service.create_roster_assignment(db, payload)


