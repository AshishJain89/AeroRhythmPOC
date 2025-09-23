import asyncio
import sys
from pathlib import Path
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Ensure project root is on sys.path so `backend.*` imports work when run directly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import settings
from backend.app.core.database_async import AsyncSessionLocal, engine

# Simulate disruptions
async def simulate_disruptions() -> None:
    disruptions = [
        # Disruption 1
        """
        CREATE TABLE IF NOT EXISTS disruptions (
            id SERIAL PRIMARY KEY,
            type VARCHAR(80) NOT NULL,
            affected JSON,
            severity VARCHAR(32),
            attributes JSON,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
        );
        """,
        # Disruption 2
        """
        CREATE TABLE IF NOT EXISTS disruptions (
            id SERIAL PRIMARY KEY,
            type VARCHAR(80) NOT NULL,
            affected JSON,
            severity VARCHAR(32),
            attributes JSON,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
        );
        """,
    ]
    async with engine.begin() as conn:
        for ddl in disruptions:
            await conn.execute(text(ddl))
    print("Simulated disruptions.")

# Replace the original simulate_disruptions function with the new one
async def simulate_disruptions() -> None:
    disruptions = [
        # Disruption 1
        """
        CREATE TABLE IF NOT EXISTS disruptions (
            id SERIAL PRIMARY KEY,
            type VARCHAR(80) NOT NULL,
            affected JSON,
            severity VARCHAR(32),
            attributes JSON,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
        );
        """,
        # Disruption 2
        """
        CREATE TABLE IF NOT EXISTS disruptions (
            id SERIAL PRIMARY KEY,
            type VARCHAR(80) NOT NULL,
            affected JSON,
            severity VARCHAR(32),
            attributes JSON,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
        );
        """,
    ]
    async with engine.begin() as conn:
        for ddl in disruptions:
            await conn.execute(text(ddl))
    print("Simulated disruptions.")

+++++++ REPLACE
+++++++ REPLACE
