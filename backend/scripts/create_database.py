import argparse
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

# Add a new function to create tables with indexes
async def create_tables_with_indexes() -> None:
    ddl_statements = [
        # users
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(150) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_superuser BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
        );
        """,
        # crew
        """
        CREATE TABLE IF NOT EXISTS crew (
            id SERIAL PRIMARY KEY,
            employee_id VARCHAR(50) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            rank VARCHAR(50) NOT NULL,
            base_airport VARCHAR(10),
            hire_date TIMESTAMP WITH TIME ZONE,
            seniority_number INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
        );
        """,
        # flights
        """
        CREATE TABLE IF NOT EXISTS flights (
            id VARCHAR(64) PRIMARY KEY,
            flight_number VARCHAR(32) NOT NULL,
            origin VARCHAR(10) NOT NULL,
            destination VARCHAR(10) NOT NULL,
            departure TIMESTAMP WITH TIME ZONE NOT NULL,
            arrival TIMESTAMP WITH TIME ZONE NOT NULL,
            aircraft VARCHAR(50),
            attributes JSON,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
        );
        """,
        # rosters
        """
        CREATE TABLE IF NOT EXISTS rosters (
            id SERIAL PRIMARY KEY,
            crew_id INTEGER NOT NULL REFERENCES crew(id) ON DELETE CASCADE,
            flight_id VARCHAR(64) NOT NULL REFERENCES flights(id) ON DELETE CASCADE,
            start TIMESTAMP WITH TIME ZONE NOT NULL,
            "end" TIMESTAMP WITH TIME ZONE NOT NULL,
            position VARCHAR(32),
            attributes JSON,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
            CONSTRAINT uq_crew_flight UNIQUE (crew_id, flight_id)
        );
        """,
        # disruptions
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
        # jobs
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            type VARCHAR(100) NOT NULL,
            status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
            completed_at TIMESTAMP WITH TIME ZONE,
            result JSON,
            error_message VARCHAR(1024)
        );
        """,
        # Add indexes
        """
        CREATE INDEX idx_users_username ON users (username);
        CREATE INDEX idx_crew_employee_id ON crew (employee_id);
        CREATE INDEX idx_flights_flight_number ON flights (flight_number);
        CREATE INDEX idx_rosters_crew_id ON rosters (crew_id);
        CREATE INDEX idx_rosters_flight_id ON rosters (flight_id);
        """
    ]
    async with engine.begin() as conn:
        for ddl in ddl_statements:
            await conn.execute(text(ddl))
    print("Created tables with indexes.")

# Replace the original create_tables function with the new one
async def create_tables() -> None:
    ddl_statements = [
        # users
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(150) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_superuser BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
        );
        """,
        # crew
        """
        CREATE TABLE IF NOT EXISTS crew (
            id SERIAL PRIMARY KEY,
            employee_id VARCHAR(50) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            rank VARCHAR(50) NOT NULL,
            base_airport VARCHAR(10),
            hire_date TIMESTAMP WITH TIME ZONE,
            seniority_number INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
        );
        """,
        # flights
        """
        CREATE TABLE IF NOT EXISTS flights (
            id VARCHAR(64) PRIMARY KEY,
            flight_number VARCHAR(32) NOT NULL,
            origin VARCHAR(10) NOT NULL,
            destination VARCHAR(10) NOT NULL,
            departure TIMESTAMP WITH TIME ZONE NOT NULL,
            arrival TIMESTAMP WITH TIME ZONE NOT NULL,
            aircraft VARCHAR(50),
            attributes JSON,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
        );
        """,
        # rosters
        """
        CREATE TABLE IF NOT EXISTS rosters (
            id SERIAL PRIMARY KEY,
            crew_id INTEGER NOT NULL REFERENCES crew(id) ON DELETE CASCADE,
            flight_id VARCHAR(64) NOT NULL REFERENCES flights(id) ON DELETE CASCADE,
            start TIMESTAMP WITH TIME ZONE NOT NULL,
            "end" TIMESTAMP WITH TIME ZONE NOT NULL,
            position VARCHAR(32),
            attributes JSON,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
            CONSTRAINT uq_crew_flight UNIQUE (crew_id, flight_id)
        );
        """,
        # disruptions
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
        # jobs
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            type VARCHAR(100) NOT NULL,
            status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
            completed_at TIMESTAMP WITH TIME ZONE,
            result JSON,
            error_message VARCHAR(1024)
        );
        """,
    ]
    async with engine.begin() as conn:
        for ddl in ddl_statements:
            await conn.execute(text(ddl))
    print("Created tables.")
