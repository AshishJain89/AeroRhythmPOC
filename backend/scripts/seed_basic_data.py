#!/usr/bin/env python3
import asyncio
import uuid
import sys
import os
from datetime import datetime, timezone, timedelta
import json

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from backend.app.models.models import Crew, Flight, Disruption

async def seed_basic_data():
    async with AsyncSessionLocal() as db:
        print("Seeding basic data...")
        
        crews = [
            Crew(
                id=str(uuid.uuid4()),
                first_name="Rajesh",
                last_name="Sharma",
                employee_id="EMP001",
                position="Captain",
                home_base="DEL",
                status="available",
                license_expiry=datetime.now().date() + timedelta(days=365),
                qualifications=json.dumps(["B737", "A320"]),
                is_active=True,
                created_at=datetime.now(timezone.utc)
            ),
            Crew(
                id=str(uuid.uuid4()),
                first_name="Priya",
                last_name="Singh", 
                employee_id="EMP002",
                position="First Officer",
                home_base="DEL",
                status="available",
                license_expiry=datetime.now().date() + timedelta(days=200),
                qualifications=json.dumps(["A320"]),
                is_active=True,
                created_at=datetime.now(timezone.utc)
            ),
            Crew(
                id=str(uuid.uuid4()),
                first_name="Amit",
                last_name="Kumar",
                employee_id="EMP003",
                position="Flight Attendant",
                home_base="BOM",
                status="on_leave",
                license_expiry=datetime.now().date() + timedelta(days=150),
                qualifications=json.dumps(["Safety", "Service"]),
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
        ]
        
        for crew in crews:
            db.add(crew)
        
        # Create sample flights
        flights = [
            Flight(
                id=str(uuid.uuid4()),
                flight_number="6E-201",
                origin="DEL",
                destination="BOM",
                departure_time=datetime.now(timezone.utc) + timedelta(hours=2),
                arrival_time=datetime.now(timezone.utc) + timedelta(hours=4),
                aircraft_type="A320",
                status="scheduled",
                created_at=datetime.now(timezone.utc)
            ),
            Flight(
                id=str(uuid.uuid4()),
                flight_number="6E-202", 
                origin="BOM",
                destination="DEL",
                departure_time=datetime.now(timezone.utc) + timedelta(hours=6),
                arrival_time=datetime.now(timezone.utc) + timedelta(hours=8),
                aircraft_type="A320",
                status="scheduled",
                created_at=datetime.now(timezone.utc)
            )
        ]
        
        for flight in flights:
            db.add(flight)
        
        # Create sample disruptions - FIX JSON fields
        disruptions = [
            Disruption(
                id=str(uuid.uuid4()),
                title="Weather Delay - Delhi Airport",
                description="Heavy fog causing delays at Delhi airport",
                type="weather",
                severity="high",
                affected_flights=json.dumps(["6E-201", "6E-203"]),
                affected_crew=json.dumps(["EMP001"]),
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc) + timedelta(hours=3),
                status="active",
                created_at=datetime.now(timezone.utc)
            )
        ]
        
        for disruption in disruptions:
            db.add(disruption)
        
        try:
            await db.commit()
            print("Basic data seeded successfully!")
            print(f"{len(crews)} crew members")
            print(f"{len(flights)} flights")
            print(f"{len(disruptions)} disruptions")
        except Exception as e:
            await db.rollback()
            print(f"Error seeding data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(seed_basic_data())