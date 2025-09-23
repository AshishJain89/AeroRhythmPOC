"""
Database table creation, migration, and sample data generation script
Optimized and refactored for seamless integration
"""
import os, logging, random, psycopg
from datetime import datetime, timedelta
from typing import List, Dict, Any
from contextlib import contextmanager
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.host = os.environ["POSTGRES_HOST"]
        self.port = os.environ["POSTGRES_PORT"]
        self.database = os.environ["POSTGRES_DB"]
        self.user = os.environ["POSTGRES_USER"]
        self.password = os.environ["POSTGRES_PASSWORD"]

    @property
    def dsn(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"

    def test_connection(self) -> bool:
        try:
            with psycopg.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def print_config(self):
        print("Database Configuration:")
        print(f"  Host: {self.host}")
        print(f"  Port: {self.port}")
        print(f"  Database: {self.database}")
        print(f"  User: {self.user}")
        print(f"  Password: {'*' * len(self.password)}")


class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = psycopg.connect(self.config.dsn)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_sql(self, sql: str, params: tuple = None) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params or ())
                    conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"SQL execution failed: {e}")
            return False

    def execute_many(self, sql: str, param_list: List[tuple]) -> bool:
        try:
            if not param_list:
                return True
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.executemany(sql, param_list)
                    conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Batch SQL execution failed: {e}")
            return False

    def fetchall(self, sql: str) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(sql)
                    return cur.fetchall()
        except Exception as e:
            self.logger.error(f"Fetch failed: {e}")
            return []

    def fetch_scalar(self, sql: str) -> Any:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    result = cur.fetchone()
                    return result[0] if result else None
        except Exception as e:
            self.logger.error(f"Fetch scalar failed: {e}")
            return None


class SchemaDefinitions:
    @staticmethod
    def get_table_definitions() -> Dict[str, str]:
        return {
            'crew': """
                CREATE TABLE IF NOT EXISTS crew (
                    id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(32) NOT NULL UNIQUE,
                    first_name VARCHAR(64),
                    last_name VARCHAR(64),
                    rank VARCHAR(32),
                    base_airport VARCHAR(8),
                    hire_date DATE,
                    seniority_number INT,
                    status VARCHAR(32),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            'flights': """
                CREATE TABLE IF NOT EXISTS flights (
                    id SERIAL PRIMARY KEY,
                    flight_number VARCHAR(16) NOT NULL UNIQUE,
                    airline_code VARCHAR(8),
                    departure_airport VARCHAR(8),
                    arrival_airport VARCHAR(8),
                    scheduled_departure TIMESTAMP,
                    scheduled_arrival TIMESTAMP,
                    aircraft_type VARCHAR(32),
                    status VARCHAR(32),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            'rosters': """
                CREATE TABLE IF NOT EXISTS rosters (
                    id SERIAL PRIMARY KEY,
                    crew_id INT REFERENCES crew(id),
                    flight_id INT REFERENCES flights(id),
                    assignment_type VARCHAR(32),
                    status VARCHAR(32),
                    crew_position VARCHAR(32),
                    duty_start TIMESTAMP,
                    duty_end TIMESTAMP,
                    report_time TIMESTAMP,
                    release_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            'audit_log': """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP,
                    user_id VARCHAR(255),
                    action VARCHAR(255),
                    details TEXT,
                    type VARCHAR(255)
                );
            """
        }

    @staticmethod
    def get_drop_statements() -> List[str]:
        return [
            "DROP TABLE IF EXISTS rosters CASCADE;",
            "DROP TABLE IF EXISTS flights CASCADE;",
            "DROP TABLE IF EXISTS crew CASCADE;",
            "DROP TABLE IF EXISTS audit_log CASCADE;"
        ]


class SampleDataGenerator:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _get_date_range(self, year: int, quarter: int):
        if quarter == 1:
            return datetime(year, 1, 1), datetime(year, 3, 31, 23, 59, 59)
        if quarter == 2:
            return datetime(year, 4, 1), datetime(year, 6, 30, 23, 59, 59)
        if quarter == 3:
            return datetime(year, 7, 1), datetime(year, 9, 30, 23, 59, 59)
        if quarter == 4:
            return datetime(year, 10, 1), datetime(year, 12, 31, 23, 59, 59)
        raise ValueError("Quarter must be between 1 and 4")

    def generate_crew(self, count: int = 100):
        sql = """
            INSERT INTO crew (employee_id, first_name, last_name, rank, base_airport, hire_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (employee_id) DO NOTHING;
        """
        crew_ranks = ["Captain", "First Officer", "Flight Attendant"]
        airports = ["JFK", "LHR", "DXB", "DEL", "SIN"]
        first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        params = [(
            f"EMP{i+1:04d}", random.choice(first_names), random.choice(last_names),
            random.choice(crew_ranks), random.choice(airports),
            datetime.now().date(), "active"
        ) for i in range(count)]
        self.db_manager.execute_many(sql, params)

    def generate_flights(self, year: int, quarter: int, count: int = 800):
        sql = """
            INSERT INTO flights (flight_number, airline_code, departure_airport, arrival_airport,
                                 scheduled_departure, scheduled_arrival, aircraft_type, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (flight_number) DO NOTHING;
        """
        start, end = self._get_date_range(year, quarter)
        airports = ["JFK", "LHR", "DXB", "DEL", "SIN", "BOM", "CCU", "MAA"]
        aircrafts = ["A320", "B737", "B777", "A380"]
        params = []
        for i in range(count):
            dep, arr = random.sample(airports, 2)
            dep_time = start + timedelta(days=random.randint(0, (end - start).days),
                                         hours=random.randint(0, 23),
                                         minutes=random.choice([0, 15, 30, 45]))
            arr_time = dep_time + timedelta(hours=random.randint(2, 12), minutes=random.choice([0, 15, 30, 45]))
            params.append((f"6E{i+1000}", "6E", dep, arr, dep_time, arr_time, random.choice(aircrafts), "scheduled"))
        self.db_manager.execute_many(sql, params)

    def generate_rosters(self, year: int, quarter: int, count: int = 5000):
        sql = """
            INSERT INTO rosters (crew_id, flight_id, assignment_type, status, crew_position,
                                 duty_start, duty_end, report_time, release_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        start, end = self._get_date_range(year, quarter)
        crew_ids = [row["id"] for row in self.db_manager.fetchall("SELECT id FROM crew")]
        flight_ids = [row["id"] for row in self.db_manager.fetchall("SELECT id FROM flights")]
        if not crew_ids or not flight_ids:
            return
        params = []
        for _ in range(count):
            crew_id = random.choice(crew_ids)
            flight_id = random.choice(flight_ids)
            duty_start = start + timedelta(days=random.randint(0, (end - start).days))
            duty_end = duty_start + timedelta(hours=8)
            params.append((crew_id, flight_id, "assignment", "planned", "Pilot",
                           duty_start, duty_end, duty_start - timedelta(hours=1), duty_end + timedelta(hours=1)))
        self.db_manager.execute_many(sql, params)

    def generate_audit_log(self, count: int = 200):
        sql = """
            INSERT INTO audit_log (timestamp, user_id, action, details, type)
            VALUES (%s, %s, %s, %s, %s);
        """
        actions = ["Roster Update", "System Maintenance", "Compliance Rule Update", "Disruption Alert"]
        users = ["admin", "system", "compliance_officer", "dispatcher"]
        types = ["roster_change", "system", "rule_update", "disruption"]
        params = []
        for _ in range(count):
            timestamp = datetime.now() - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
            params.append((
                timestamp,
                random.choice(users),
                random.choice(actions),
                "Details about the action.",
                random.choice(types)
            ))
        self.db_manager.execute_many(sql, params)

    def generate_all(self, year: int, quarter: int):
        self.generate_crew()
        self.generate_flights(year, quarter)
        self.generate_rosters(year, quarter)
        self.generate_audit_log()


class DatabaseMigration:
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.db_manager = DatabaseManager(self.config)
        self.schema = SchemaDefinitions()
        self.sample_generator = SampleDataGenerator(self.db_manager)

    def create_tables(self) -> bool:
        for table in ["crew", "flights", "rosters", "audit_log"]:
            if not self.db_manager.execute_sql(self.schema.get_table_definitions()[table]):
                return False
        return True

    def drop_all_tables(self) -> bool:
        for drop_sql in self.schema.get_drop_statements():
            if not self.db_manager.execute_sql(drop_sql):
                return False
        return True

    def reset_database(self, year: int, quarter: int, with_counts: bool = False) -> bool:
        ok = (self.drop_all_tables() and self.create_tables() and (self.sample_generator.generate_all(year, quarter) or True))
        if ok and with_counts:
            self.print_row_counts()
        return ok

    def print_row_counts(self):
        tables = ["crew", "flights", "rosters", "audit_log"]
        print("Row counts:")
        for t in tables:
            count = self.db_manager.fetch_scalar(f"SELECT COUNT(*) FROM {t};")
            print(f"  {t}: {count}")


def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main():
    import argparse
    setup_logging()
    parser = argparse.ArgumentParser(description="Database migration + sample data generator")
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--drop", action="store_true")
    parser.add_argument("--reset", nargs=2, metavar=("YEAR", "QUARTER"))
    parser.add_argument("--reset-with-counts", nargs=2, metavar=("YEAR", "QUARTER"))
    parser.add_argument("--generate", nargs=2, metavar=("YEAR", "QUARTER"))
    parser.add_argument("--test-connection", action="store_true")
    parser.add_argument("--show-config", action="store_true")
    args = parser.parse_args()

    config = DatabaseConfig()
    if args.show_config:
        config.print_config()
        return
    if args.test_connection:
        print("Testing DB connection...")
        print("Success!" if config.test_connection() else "Failed!")
        return

    migration = DatabaseMigration(config)
    if args.create:
        print("Create:", migration.create_tables())
    elif args.drop:
        print("Drop:", migration.drop_all_tables())
    elif args.reset:
        year, quarter = int(args.reset[0]), int(args.reset[1])
        print("Reset:", migration.reset_database(year, quarter))
    elif args.reset_with_counts:
        year, quarter = int(args.reset_with_counts[0]), int(args.reset_with_counts[1])
        print("Reset:", migration.reset_database(year, quarter, with_counts=True))
    elif args.generate:
        year, quarter = int(args.generate[0]), int(args.generate[1])
        migration.sample_generator.generate_all(year, quarter)
        migration.print_row_counts()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
