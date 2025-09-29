from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timezone
from ..models.models import Crew, Flight, Roster, Disruption, User


class AsyncCRUD:
    def __init__(self, model):
        self.model = model

    
    async def get(self, db: AsyncSession, id: str) -> Optional[Any]:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Any]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> Any:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


class CrewCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Crew)
    
    async def get_by_employee_id(self, db:AsyncSession, employee_id: str) -> Optional[Crew]:
        result = await db.execute(select(Crew).filter(Crew.employee_id == employee_id))
        return result.scalar_one_or_none()
    
    async def get_active_crew(self, db: AsyncSession) -> List[Crew]:
        result = await db.execute(select(Crew).filter(Crew.is_active == True))
        return list(result.scalars().all())
    

class FlightCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Flight)
    
    async def get_by_date_range(self, db: AsyncSession, start_date: date, end_date: date) -> List[Flight]:
        result = await db.execute(
            select(Flight).filter(
                and_(
                    Flight.departure_time >= start_date,
                    Flight.arrival_time <= end_date
                )
            ).order_by(Flight.departure_time)
        )
        return list(result.scalars().all())
    
class RosterCRUD(AsyncCRUD):
    def __init__(self):
        super().__init__(Roster)

    async def get_by_date_range(self, db: AsyncSession, start_date: date, end_date: date) -> List[Roster]:
        result = await db.execute(
            select(Roster).filter(
                and_(
                    Roster.assignment_date >= start_date,
                    Roster.assignment_date <= end_date
                )
            ).order_by(Roster.assignment_date, Roster.report_time)
        )
        return list(result.scalars().all())
    

# Initialize CRUD instances
crew_crud = CrewCRUD()
flight_crud = FlightCRUD()
roster_crud = RosterCRUD()
disruption_crud = AsyncCRUD(Disruption)