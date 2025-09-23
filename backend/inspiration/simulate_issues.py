import os, asyncio, random, psycopg, sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ["POSTGRES_HOST"]
DB_PORT = os.environ["POSTGRES_PORT"]
DB_NAME = os.environ["POSTGRES_DB"]
DB_USER = os.environ["POSTGRES_USER"]
DB_PASS = os.environ["POSTGRES_PASSWORD"]

DSN = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASS}"


async def main():
    async with await psycopg.AsyncConnection.connect(DSN) as conn:
        async with conn.cursor() as cur:
            # 1) Create overlapping rosters to simulate conflicts
            # pick two flights close in time and assign the same captain
            await cur.execute(
                """
                SELECT id, flight_number, scheduled_departure, scheduled_arrival
                FROM flights
                WHERE scheduled_departure > NOW() - INTERVAL '1 day'
                ORDER BY scheduled_departure ASC
                LIMIT 10
                """
            )
            flights = await cur.fetchall()
            if len(flights) >= 2:
                f1 = flights[0]
                f2 = flights[1]
                # choose a captain
                await cur.execute("SELECT id FROM crew WHERE rank = 'CAPTAIN' LIMIT 1")
                cap = await cur.fetchone()
                if cap:
                    captain_id = cap[0]
                    # assign same captain to both flights with overlapping times
                    for fid in (f1[0], f2[0]):
                        await cur.execute(
                            """
                            INSERT INTO rosters (crew_id, flight_id, crew_position, status)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                            """,
                            (captain_id, fid, 'captain', 'active'),
                        )

            # 2) Add upcoming disruptions forecasts
            disruptions = [
                {
                    "type": "weather",
                    "severity": "high",
                    "title": "Severe Thunderstorms",
                    "description": "Forecasted thunderstorms likely to cause delays and diversions.",
                },
                {
                    "type": "crew_shortage",
                    "severity": "medium",
                    "title": "Unexpected Crew Sickness Spike",
                    "description": "Increased sick reports forecasted for the next 48 hours.",
                },
            ]
            now = datetime.now(timezone.utc)
            for d in disruptions:
                await cur.execute(
                    """
                    INSERT INTO disruptions (type, severity, title, description, affected_flights, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        d["type"],
                        d["severity"],
                        d["title"],
                        d["description"],
                        psycopg.types.json.Json([]),
                        now + timedelta(hours=random.randint(1, 24)),
                    ),
                )

        await conn.commit()
    print("Simulation complete: conflicts seeded and disruptions added.")


if __name__ == "__main__":
    # Fix for Windows: psycopg async requires SelectorEventLoop
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())


