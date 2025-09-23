"""
Generate synthetic sample data for crews, flights, roster assignments and audit-like events.

Can write to database via SQLAlchemy models or export to JSON files in data/seed.

Usage examples:
  python backend/scripts/generate_sample_data.py --year 2025 --quarter 3 --to-db --counts
  python backend/scripts/generate_sample_data.py --year 2025 --quarter 3 --to-files --out backend/app/data/seed
  python backend/scripts/generate_sample_data.py --year 2025 --quarter 3 --to-db --crew 200 --flights 1200 --rosters 8000 --audit 400
"""

import argparse
import asyncio
import json
import os
import random
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# Ensure project root on sys.path for `backend.*` imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database_async import engine


SEED_DEFAULT_DIR = Path("backend/app/data/seed")


def quarter_date_range(year: int, quarter: int) -> Tuple[datetime, datetime]:
    if quarter not in (1, 2, 3, 4):
        raise ValueError("Quarter must be 1..4")
    if quarter == 1:
        return datetime(year, 1, 1, tzinfo=timezone.utc), datetime(year, 3, 31, 23, 59, 59, tzinfo=timezone.utc)
    if quarter == 2:
        return datetime(year, 4, 1, tzinfo=timezone.utc), datetime(year, 6, 30, 23, 59, 59, tzinfo=timezone.utc)
    if quarter == 3:
        return datetime(year, 7, 1, tzinfo=timezone.utc), datetime(year, 9, 30, 23, 59, 59, tzinfo=timezone.utc)
    return datetime(year, 10, 1, tzinfo=timezone.utc), datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)


@dataclass
class CrewSeed:
    name: str
    role: str
    base: str
    qualifications: List[str]
    seniority: int
    metadata: Dict[str, Any]


@dataclass
class FlightSeed:
    id: str
    flight_number: str
    origin: str
    destination: str
    departure: str
    arrival: str
    aircraft: str
    metadata: Dict[str, Any]


@dataclass
class AssignmentSeed:
    crew_id: int
    flight_id: str
    start: str
    end: str
    position: str
    metadata: Dict[str, Any]


def generate_crews(count: int = 100) -> List[CrewSeed]:
    first_names = ["Aarav", "Vihaan", "Vivaan", "Ananya", "Diya", "Ishaan", "Kabir", "Aadhya", "Arjun", "Zara"]
    last_names = ["Sharma", "Verma", "Gupta", "Iyer", "Khan", "Singh", "Nair", "Mehta", "Kapoor", "Bose"]
    bases = ["DEL", "BOM", "BLR", "MAA", "HYD", "CCU", "PNQ", "COK"]
    roles = ["CPT", "FO", "FA"]
    aircraft_types = ["A320", "B737", "A321", "A350"]
    crews: List[CrewSeed] = []
    for _ in range(count):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        role = random.choices(roles, weights=[1, 1, 2])[0]
        base = random.choice(bases)
        quals = random.sample(aircraft_types, k=random.randint(1, min(2, len(aircraft_types))))
        seniority = random.randint(1, 20)
        crews.append(CrewSeed(name=name, role=role, base=base, qualifications=quals, seniority=seniority, metadata={}))
    return crews


def generate_flights(year: int, quarter: int, count: int = 800) -> List[FlightSeed]:
    start, end = quarter_date_range(year, quarter)
    airports = ["DEL", "BOM", "BLR", "MAA", "HYD", "CCU", "PNQ", "COK", "JAI", "AMD"]
    aircraft_types = ["A320", "B737", "A321", "A350"]
    flights: List[FlightSeed] = []
    for i in range(count):
        origin, destination = random.sample(airports, 2)
        dep_time = start + timedelta(days=random.randint(0, (end - start).days), hours=random.randint(5, 22), minutes=random.choice([0, 15, 30, 45]))
        block = random.randint(60, 240)
        arr_time = dep_time + timedelta(minutes=block)
        flight_number = f"6E{1000 + i}"
        fid = f"{flight_number}-{dep_time.strftime('%Y%m%d')}"
        flights.append(
            FlightSeed(
                id=fid,
                flight_number=flight_number,
                origin=origin,
                destination=destination,
                departure=dep_time.isoformat(),
                arrival=arr_time.isoformat(),
                aircraft=random.choice(aircraft_types),
                metadata={},
            )
        )
    return flights


def generate_assignments(
    crew_ids: List[int],
    flight_ids: List[str],
    flights_by_id: Dict[str, FlightSeed],
    count: int = 5000,
) -> List[AssignmentSeed]:
    positions = ["CPT", "FO", "FA"]
    items: List[AssignmentSeed] = []
    for _ in range(count):
        crew_id = random.choice(crew_ids)
        flight_id = random.choice(flight_ids)
        dep = datetime.fromisoformat(flights_by_id[flight_id].departure)
        start = dep - timedelta(minutes=60)
        end = datetime.fromisoformat(flights_by_id[flight_id].arrival) + timedelta(minutes=30)
        items.append(
            AssignmentSeed(
                crew_id=crew_id,
                flight_id=flight_id,
                start=start.isoformat(),
                end=end.isoformat(),
                position=random.choice(positions),
                metadata={"source": "seed"},
            )
        )
    return items


def write_json_files(out_dir: Path, crews: List[CrewSeed], flights: List[FlightSeed]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    crews_path = out_dir / "crews.json"
    flights_path = out_dir / "flights.json"
    with open(crews_path, "w", encoding="utf-8") as f:
        json.dump([asdict(c) for c in crews], f, indent=2)
    with open(flights_path, "w", encoding="utf-8") as f:
        json.dump([asdict(fl) for fl in flights], f, indent=2)
    print(f"Wrote {crews_path} and {flights_path}")


async def insert_to_db(
    crews: List[CrewSeed],
    flights: List[FlightSeed],
    assignments: List[AssignmentSeed],
) -> Dict[str, int]:
    created = {"crews": 0, "flights": 0, "assignments": 0}
    async with engine.begin() as conn:
        # Insert crews
        if crews:
            await conn.execute(
                text(
                    """
                    INSERT INTO crew (employee_id, first_name, last_name, rank, base_airport, hire_date, seniority_number, status)
                    VALUES (:employee_id, :first_name, :last_name, :rank, :base_airport, :hire_date, :seniority_number, :status)
                    """
                ),
                [
                    {
                        "employee_id": f"EMP{i:04d}",
                        "first_name": c.name.split()[0],
                        "last_name": c.name.split()[-1],
                        "rank": c.role,
                        "base_airport": c.base,
                        "hire_date": datetime.now(timezone.utc) - timedelta(days=c.seniority * 365),
                        "seniority_number": c.seniority,
                        "status": "active",
                    }
                    for i, c in enumerate(crews)
                ],
            )
            created["crews"] = len(crews)

        # Insert flights
        if flights:
            await conn.execute(
                text(
                    """
                    INSERT INTO flights (id, flight_number, origin, destination, departure, arrival, aircraft, attributes)
                    VALUES (:id, :flight_number, :origin, :destination, :departure, :arrival, :aircraft, :attributes)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                [
                    {
                        "id": fl.id,
                        "flight_number": fl.flight_number,
                        "origin": fl.origin,
                        "destination": fl.destination,
                        "departure": datetime.fromisoformat(fl.departure),
                        "arrival": datetime.fromisoformat(fl.arrival),
                        "aircraft": fl.aircraft,
                        "attributes": json.dumps(fl.metadata),
                    }
                    for fl in flights
                ],
            )
            created["flights"] = len(flights)

        # Insert assignments
        if assignments:
            await conn.execute(
                text(
                    """
                    INSERT INTO rosters (crew_id, flight_id, start, "end", position, attributes)
                    VALUES (:crew_id, :flight_id, :start, :end, :position, :attributes)
                    ON CONFLICT (crew_id, flight_id) DO NOTHING
                    """
                ),
                [
                    {
                        "crew_id": a.crew_id,
                        "flight_id": a.flight_id,
                        "start": datetime.fromisoformat(a.start),
                        "end": datetime.fromisoformat(a.end),
                        "position": a.position,
                        "attributes": json.dumps(a.metadata),
                    }
                    for a in assignments
                ],
            )
            created["assignments"] = len(assignments)
    return created


async def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sample data for DB and/or JSON files")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--quarter", type=int, required=True, choices=[1, 2, 3, 4])
    parser.add_argument("--to-db", action="store_true", help="Insert generated data to database")
    parser.add_argument("--to-files", action="store_true", help="Write crews.json and flights.json to output dir")
    parser.add_argument("--out", default=str(SEED_DEFAULT_DIR), help="Output dir for JSON files")
    parser.add_argument("--crew", type=int, default=100)
    parser.add_argument("--flights", type=int, default=800)
    parser.add_argument("--rosters", type=int, default=5000)
    parser.add_argument("--counts", action="store_true", help="Print row counts after DB insert")
    args = parser.parse_args()

    crews = generate_crews(args.crew)
    flights = generate_flights(args.year, args.quarter, args.flights)
    flights_by_id = {f.id: f for f in flights}

    # For generating assignments, we need actual crew IDs from DB if inserting.
    # If not inserting, we synthesize crew IDs as 1..N just for export/testing consistency.
    if args.to_db:
        # Insert crews and flights first, then retrieve IDs via direct SQL
        await insert_to_db(crews=crews, flights=flights, assignments=[])
        async with engine.begin() as conn:
            crew_ids_result = await conn.execute(text("SELECT id FROM crew"))
            crew_ids = [row[0] for row in crew_ids_result.all()]
            flight_ids_result = await conn.execute(text("SELECT id FROM flights"))
            flight_ids = [row[0] for row in flight_ids_result.all()]
    else:
        crew_ids = list(range(1, len(crews) + 1))
        flight_ids = [f.id for f in flights]

    assignments = generate_assignments(crew_ids, flight_ids, flights_by_id, count=args.rosters)

    if args.to_files:
        out_dir = Path(args.out)
        write_json_files(out_dir, crews, flights)

    if args.to_db:
        created = await insert_to_db(crews=[], flights=[], assignments=assignments)
        # Note: crews/flights already inserted above; here we bulk insert assignments
        print(
            f"Inserted: crews={len(crew_ids)} flights={len(flight_ids)} assignments={created['assignments']}"
        )
        if args.counts:
            # Print counts using a lightweight query
            async with engine.begin() as conn:
                c_crews_result = await conn.execute(text("SELECT COUNT(*) FROM crew"))
                c_crews = c_crews_result.scalar() or 0
                c_flights_result = await conn.execute(text("SELECT COUNT(*) FROM flights"))
                c_flights = c_flights_result.scalar() or 0
                c_assign_result = await conn.execute(text("SELECT COUNT(*) FROM rosters"))
                c_assign = c_assign_result.scalar() or 0
                print(f"Counts -> crews={int(c_crews)} flights={int(c_flights)} assignments={int(c_assign)}")


if __name__ == "__main__":
    asyncio.run(main())
