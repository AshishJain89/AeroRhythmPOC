from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import models

async def generate_roster(db: AsyncSession, start: datetime, end: datetime) -> Dict[str, Any]:
    # Example: fetch all crews and flights, assign each crew to a flight in a round-robin way
    crews = (await db.execute(models.Crew.__table__.select())).scalars().all()
    flights = (await db.execute(models.Flight.__table__.select())).scalars().all()
    assignments = []
    for i, flight in enumerate(flights):
        if i < len(crews):
            crew = crews[i]
            assignments.append({
                "crew_id": crew.id,
                "flight_id": flight.id,
                "start": flight.departure.isoformat(),
                "end": flight.arrival.isoformat(),
                "position": crew.rank,
                "metadata": {"source": "simple-assigner"}
            })
    return {
        "assignments": assignments,
        "ai_confidence": 0.9,
        "metrics": {"generatedAt": datetime.now(timezone.utc).isoformat(), "totalAssignments": len(assignments)}
    }