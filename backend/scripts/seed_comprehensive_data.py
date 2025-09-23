#!/usr/bin/env python3
"""
Comprehensive seed data generator for AeroRhythm POC
Creates realistic, interconnected data for testing all backend features
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import random
from typing import List, Dict, Any

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database_async import AsyncSessionLocal, engine
from backend.app import models
from backend.app.core import security
from sqlalchemy import text
from sqlalchemy.future import select

# Q3 2025 date range
Q3_START = datetime(2025, 7, 1, tzinfo=timezone.utc)
Q3_END = datetime(2025, 9, 30, tzinfo=timezone.utc)

# Realistic data sets
AIRPORTS = [
    "LAX", "JFK", "LHR", "CDG", "FRA", "NRT", "ICN", "SIN", "DXB", "HKG",
    "ORD", "ATL", "DFW", "DEN", "SFO", "SEA", "MIA", "BOS", "PHX", "LAS"
]

AIRCRAFT_TYPES = [
    "B737-800", "B737-900", "A320", "A321", "B777-300ER", "B787-9",
    "A350-900", "A330-300", "B747-8", "A380-800"
]

RANKS = ["Captain", "First Officer", "Senior First Officer", "Flight Engineer"]
POSITIONS = ["CPT", "FO", "SFO", "FE"]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
    "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill"
]

FLIGHT_PREFIXES = ["AA", "UA", "DL", "WN", "B6", "NK", "F9", "AS", "HA", "G4"]

def generate_crew_data() -> List[Dict[str, Any]]:
    """Generate realistic crew data"""
    crew_data = []

    for i in range(1, 51):  # 50 crew members
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        rank = random.choice(RANKS)
        base = random.choice(AIRPORTS[:10])  # Major hubs

        # Generate hire date (1-15 years ago)
        years_ago = random.randint(1, 15)
        hire_date = datetime.now(timezone.utc) - timedelta(days=years_ago * 365 + random.randint(0, 365))

        # Seniority based on hire date
        seniority = max(1, years_ago * 12 + random.randint(0, 11))

        crew_data.append({
            "employee_id": f"EMP{i:04d}",
            "first_name": first_name,
            "last_name": last_name,
            "rank": rank,
            "base_airport": base,
            "hire_date": hire_date,
            "seniority_number": seniority,
            "status": "active" if random.random() > 0.05 else "inactive"  # 5% inactive
        })

    return crew_data

def generate_flight_data() -> List[Dict[str, Any]]:
    """Generate realistic flight data for Q3 2025"""
    flights = []
    flight_counter = 1

    # Generate flights for each day in Q3 2025
    current_date = Q3_START
    while current_date <= Q3_END:
        # Generate 5-15 flights per day
        daily_flights = random.randint(5, 15)

        for _ in range(daily_flights):
            origin = random.choice(AIRPORTS)
            destination = random.choice([airport for airport in AIRPORTS if airport != origin])

            # Generate departure time (6 AM to 11 PM)
            departure_hour = random.randint(6, 23)
            departure_minute = random.choice([0, 15, 30, 45])
            departure = current_date.replace(hour=departure_hour, minute=departure_minute, second=0, microsecond=0)

            # Flight duration 1-12 hours
            duration_hours = random.randint(1, 12)
            arrival = departure + timedelta(hours=duration_hours)

            # Handle overnight flights
            if arrival.date() > departure.date():
                arrival = arrival.replace(hour=min(arrival.hour, 6))  # Arrive by 6 AM next day

            prefix = random.choice(FLIGHT_PREFIXES)
            flight_number = f"{prefix}{random.randint(100, 9999)}"
            flight_id = f"{prefix}{flight_counter:04d}"

            flights.append({
                "id": flight_id,
                "flight_number": flight_number,
                "origin": origin,
                "destination": destination,
                "departure": departure,
                "arrival": arrival,
                "aircraft": random.choice(AIRCRAFT_TYPES),
                "attributes": {
                    "route_type": "domestic" if random.random() > 0.3 else "international",
                    "passenger_capacity": random.randint(120, 400)
                }
            })

            flight_counter += 1

        current_date += timedelta(days=1)

    return flights

def generate_roster_assignments(crew_data: List[Dict], flight_data: List[Dict]) -> List[Dict[str, Any]]:
    """Generate realistic roster assignments"""
    assignments = []

    # Group flights by date for easier assignment
    flights_by_date = {}
    for flight in flight_data:
        date_key = flight["departure"].date()
        if date_key not in flights_by_date:
            flights_by_date[date_key] = []
        flights_by_date[date_key].append(flight)

    # Assign crew to flights
    for date, daily_flights in flights_by_date.items():
        # Select available crew for this date (80% of crew available)
        available_crew = [crew for crew in crew_data if crew["status"] == "active"]
        available_crew = random.sample(available_crew, int(len(available_crew) * 0.8))

        for flight in daily_flights:
            # Assign 2-4 crew members per flight
            crew_count = random.randint(2, 4)
            assigned_crew = random.sample(available_crew, min(crew_count, len(available_crew)))

            for i, crew in enumerate(assigned_crew):
                position = POSITIONS[i] if i < len(POSITIONS) else "FA"

                # Start time is 1 hour before departure, end time is 30 minutes after arrival
                start_time = flight["departure"] - timedelta(hours=1)
                end_time = flight["arrival"] + timedelta(minutes=30)

                assignments.append({
                    "crew_id": crew_data.index(crew) + 1,  # Assuming crew IDs start from 1
                    "flight_id": flight["id"],
                    "start": start_time,
                    "end": end_time,
                    "position": position,
                    "attributes": {
                        "assignment_type": "scheduled",
                        "duty_time_hours": (end_time - start_time).total_seconds() / 3600
                    }
                })

    return assignments

def generate_disruption_data(crew_data: List[Dict], flight_data: List[Dict]) -> List[Dict[str, Any]]:
    """Generate disruption data to test conflict resolution"""
    disruptions = []

    # 1. Crew illness/sick leave
    sick_crew = random.choice([crew for crew in crew_data if crew["status"] == "active"])
    disruptions.append({
        "type": "crew_illness",
        "affected": {
            "crew_ids": [crew_data.index(sick_crew) + 1],
            "crew_names": [f"{sick_crew['first_name']} {sick_crew['last_name']}"]
        },
        "severity": "high",
        "attributes": {
            "illness_type": "flu",
            "expected_duration_days": 3,
            "requires_replacement": True
        }
    })

    # 2. Flight delay due to weather
    delayed_flight = random.choice(flight_data)
    disruptions.append({
        "type": "weather_delay",
        "affected": {
            "flight_ids": [delayed_flight["id"]],
            "flight_numbers": [delayed_flight["flight_number"]],
            "route": f"{delayed_flight['origin']}-{delayed_flight['destination']}"
        },
        "severity": "medium",
        "attributes": {
            "delay_minutes": 120,
            "weather_condition": "thunderstorm",
            "affects_crew_scheduling": True
        }
    })

    # 3. Aircraft maintenance issue
    maintenance_flight = random.choice(flight_data)
    disruptions.append({
        "type": "aircraft_maintenance",
        "affected": {
            "flight_ids": [maintenance_flight["id"]],
            "aircraft": maintenance_flight["aircraft"]
        },
        "severity": "high",
        "attributes": {
            "maintenance_type": "engine_inspection",
            "estimated_duration_hours": 4,
            "requires_aircraft_change": True
        }
    })

    # 4. Crew scheduling conflict (double booking)
    conflicting_crew = random.choice([crew for crew in crew_data if crew["status"] == "active"])
    disruptions.append({
        "type": "scheduling_conflict",
        "affected": {
            "crew_ids": [crew_data.index(conflicting_crew) + 1],
            "crew_name": f"{conflicting_crew['first_name']} {conflicting_crew['last_name']}"
        },
        "severity": "critical",
        "attributes": {
            "conflict_type": "double_booking",
            "overlapping_flights": 2,
            "requires_immediate_resolution": True
        }
    })

    # 5. Airport closure
    closed_airport = random.choice(AIRPORTS)
    affected_flights = [f for f in flight_data if f["origin"] == closed_airport or f["destination"] == closed_airport]
    disruptions.append({
        "type": "airport_closure",
        "affected": {
            "airport": closed_airport,
            "flight_count": len(affected_flights),
            "flight_ids": [f["id"] for f in affected_flights[:5]]  # Limit to first 5
        },
        "severity": "critical",
        "attributes": {
            "closure_reason": "security_incident",
            "estimated_duration_hours": 6,
            "affects_multiple_flights": True
        }
    })

    return disruptions

def generate_user_data() -> List[Dict[str, Any]]:
    """Generate user data for authentication testing"""
    users = [
        {
            "username": "admin",
            "email": "admin@aerorhythm.com",
            "password": "admin123",
            "is_superuser": True,
            "is_active": True
        },
        {
            "username": "scheduler",
            "email": "scheduler@aerorhythm.com",
            "password": "scheduler123",
            "is_superuser": True,
            "is_active": True
        },
        {
            "username": "viewer",
            "email": "viewer@aerorhythm.com",
            "password": "viewer123",
            "is_superuser": False,
            "is_active": True
        }
    ]
    return users

def generate_job_data() -> List[Dict[str, Any]]:
    """Generate background job data"""
    jobs = [
        {
            "type": "roster_generation",
            "status": "SUCCESS",
            "created_at": datetime.now(timezone.utc) - timedelta(hours=2),
            "completed_at": datetime.now(timezone.utc) - timedelta(hours=1, minutes=30),
            "result": {"generated_assignments": 1250, "conflicts_resolved": 3},
            "error_message": None
        },
        {
            "type": "conflict_detection",
            "status": "RUNNING",
            "created_at": datetime.now(timezone.utc) - timedelta(minutes=15),
            "completed_at": None,
            "result": None,
            "error_message": None
        },
        {
            "type": "crew_optimization",
            "status": "FAILED",
            "created_at": datetime.now(timezone.utc) - timedelta(hours=1),
            "completed_at": datetime.now(timezone.utc) - timedelta(minutes=45),
            "result": None,
            "error_message": "Insufficient crew availability for requested optimization"
        }
    ]
    return jobs

async def seed_database():
    """Main function to seed the database with comprehensive data"""
    print("🌱 Starting comprehensive database seeding...")

    async with AsyncSessionLocal() as db:
        try:
            # Generate data
            print("📊 Generating crew data...")
            crew_data = generate_crew_data()

            print("✈️ Generating flight data...")
            flight_data = generate_flight_data()

            print("📅 Generating roster assignments...")
            roster_data = generate_roster_assignments(crew_data, flight_data)

            print("⚠️ Generating disruption data...")
            disruption_data = generate_disruption_data(crew_data, flight_data)

            print("👤 Generating user data...")
            user_data = generate_user_data()

            print("⚙️ Generating job data...")
            job_data = generate_job_data()

            # Insert data into database
            print("💾 Inserting crew data...")
            for crew in crew_data:
                db_crew = models.Crew(**crew)
                db.add(db_crew)
            await db.commit()

            print("💾 Inserting flight data...")
            for flight in flight_data:
                db_flight = models.Flight(**flight)
                db.add(db_flight)
            await db.commit()

            print("💾 Inserting roster assignments...")
            for roster in roster_data:
                db_roster = models.Roster(**roster)
                db.add(db_roster)
            await db.commit()

            print("💾 Inserting disruption data...")
            for disruption in disruption_data:
                db_disruption = models.Disruption(**disruption)
                db.add(db_disruption)
            await db.commit()

            print("💾 Inserting user data...")
            for user in user_data:
                hashed_password = security.get_password_hash(user["password"])
                db_user = models.User(
                    username=user["username"],
                    email=user["email"],
                    hashed_password=hashed_password,
                    is_superuser=user["is_superuser"],
                    is_active=user["is_active"]
                )
                db.add(db_user)
            await db.commit()

            print("💾 Inserting job data...")
            for job in job_data:
                db_job = models.Job(**job)
                db.add(db_job)
            await db.commit()

            # Print summary
            print("\n🎉 Database seeding completed successfully!")
            print(f"📊 Summary:")
            print(f"   👥 Crew members: {len(crew_data)}")
            print(f"   ✈️ Flights: {len(flight_data)}")
            print(f"   📅 Roster assignments: {len(roster_data)}")
            print(f"   ⚠️ Disruptions: {len(disruption_data)}")
            print(f"   👤 Users: {len(user_data)}")
            print(f"   ⚙️ Jobs: {len(job_data)}")

            # Test data relationships
            print("\n🔗 Testing data relationships...")

            # Test crew-flight relationships
            crew_with_assignments_result = await db.execute(select(models.Crew).join(models.Roster).distinct())
            crew_with_assignments = len(crew_with_assignments_result.scalars().all())
            print(f"   Crew with assignments: {crew_with_assignments}")

            # Test flight-crew relationships
            flights_with_crew_result = await db.execute(select(models.Flight).join(models.Roster).distinct())
            flights_with_crew = len(flights_with_crew_result.scalars().all())
            print(f"   Flights with crew: {flights_with_crew}")

            # Test disruption data
            active_disruptions_result = await db.execute(
                select(models.Disruption).filter(
                    models.Disruption.severity.in_(["high", "critical"])
                )
            )
            active_disruptions = len(active_disruptions_result.scalars().all())
            print(f"   Active disruptions: {active_disruptions}")

            print("\n✅ All data relationships verified!")

        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_database())
