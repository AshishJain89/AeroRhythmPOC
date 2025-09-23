import asyncio
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from .. import models, crud

SEED_DIR = Path(__file__).parent.parent / "data" / "seed"


async def _load_seed_data(db: AsyncSession) -> None:
    print("[SEED] Loading seed data...")

    # Load Crews
    crews_path = SEED_DIR / "crews.json"
    with open(crews_path, "r") as f:
        crews = json.load(f)
    for crew in crews:
        await crud.create_crew(db, **crew)

    # Load Flights
    flights_path = SEED_DIR / "flights.json"
    with open(flights_path, "r") as f:
        flights = json.load(f)
    for flight in flights:
        await crud.create_flight(db, **flight)

    print(f"[SEED] Loaded {len(crews)} crews and {len(flights)} flights.")


def load_seed_data(db: AsyncSession) -> None:
    asyncio.run(_load_seed_data(db))
