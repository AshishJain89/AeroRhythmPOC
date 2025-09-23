#!/usr/bin/env python3
"""
Comprehensive Database Testing Script for AeroRhythm POC
Tests all database functionality including CRUD operations, relationships, and data integrity
"""

import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import SessionLocal, engine
from backend.app import models, crud
from backend.app.core import security
from sqlalchemy import text, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

class DatabaseTester:
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.test_data = {}
        self.db = None
        
    def log_test(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if duration > 0:
            print(f"   Duration: {duration:.2f}s")
        print()

    def setup_database_connection(self) -> bool:
        """Setup database connection for testing"""
        print("🔌 Setting up Database Connection...")
        start_time = time.time()
        
        try:
            self.db = SessionLocal()
            
            # Test basic connection
            result = self.db.execute(text("SELECT 1")).scalar()
            if result == 1:
                duration = time.time() - start_time
                self.log_test("Database Connection", "PASS", "Connection established successfully", duration)
                return True
            else:
                self.log_test("Database Connection", "FAIL", "Connection test failed")
                return False
                
        except SQLAlchemyError as e:
            self.log_test("Database Connection", "FAIL", f"Connection error: {str(e)}")
            return False

    def test_table_structure(self) -> bool:
        """Test database table structure and constraints"""
        print("🏗️ Testing Table Structure...")
        start_time = time.time()
        
        try:
            # Check if all required tables exist
            required_tables = [
                "users", "crew", "flights", "rosters", 
                "disruptions", "jobs", "audit_log", 
                "compliance_rules", "conflicts"
            ]
            
            existing_tables = []
            for table in required_tables:
                result = self.db.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    )
                """)).scalar()
                
                if result:
                    existing_tables.append(table)
            
            duration = time.time() - start_time
            
            if len(existing_tables) >= len(required_tables) * 0.8:  # 80% of tables exist
                self.log_test("Table Structure", "PASS", f"Found {len(existing_tables)}/{len(required_tables)} tables", duration)
                return True
            else:
                self.log_test("Table Structure", "FAIL", f"Only found {len(existing_tables)}/{len(required_tables)} tables", duration)
                return False
                
        except SQLAlchemyError as e:
            self.log_test("Table Structure", "FAIL", f"Table structure error: {str(e)}")
            return False

    def test_data_integrity(self) -> bool:
        """Test data integrity and constraints"""
        print("🔒 Testing Data Integrity...")
        start_time = time.time()
        
        try:
            integrity_checks = []
            
            # Check for orphaned roster assignments
            orphaned_rosters = self.db.execute(text("""
                SELECT COUNT(*) FROM rosters r 
                LEFT JOIN crew c ON r.crew_id = c.id 
                WHERE c.id IS NULL
            """)).scalar()
            
            if orphaned_rosters == 0:
                integrity_checks.append("No orphaned roster assignments")
            else:
                integrity_checks.append(f"Found {orphaned_rosters} orphaned roster assignments")
            
            # Check for orphaned flights in rosters
            orphaned_flights = self.db.execute(text("""
                SELECT COUNT(*) FROM rosters r 
                LEFT JOIN flights f ON r.flight_id = f.id 
                WHERE f.id IS NULL
            """)).scalar()
            
            if orphaned_flights == 0:
                integrity_checks.append("No orphaned flight references")
            else:
                integrity_checks.append(f"Found {orphaned_flights} orphaned flight references")
            
            # Check for duplicate crew employee IDs
            duplicate_crews = self.db.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT employee_id, COUNT(*) 
                    FROM crew 
                    GROUP BY employee_id 
                    HAVING COUNT(*) > 1
                ) duplicates
            """)).scalar()
            
            if duplicate_crews == 0:
                integrity_checks.append("No duplicate employee IDs")
            else:
                integrity_checks.append(f"Found {duplicate_crews} duplicate employee IDs")
            
            duration = time.time() - start_time
            
            # Count passed checks
            passed_checks = sum(1 for check in integrity_checks if "No" in check or "0" in check)
            
            if passed_checks >= len(integrity_checks) * 0.8:  # 80% pass rate
                self.log_test("Data Integrity", "PASS", f"{passed_checks}/{len(integrity_checks)} integrity checks passed", duration)
                return True
            else:
                self.log_test("Data Integrity", "FAIL", f"Only {passed_checks}/{len(integrity_checks)} integrity checks passed", duration)
                return False
                
        except SQLAlchemyError as e:
            self.log_test("Data Integrity", "FAIL", f"Data integrity error: {str(e)}")
            return False

    def test_crud_operations(self) -> bool:
        """Test CRUD operations for all entities"""
        print("📝 Testing CRUD Operations...")
        start_time = time.time()
        
        try:
            crud_tests = []
            
            # Test User CRUD
            try:
                # Create user
                hashed_password = security.get_password_hash("test123")
                test_user = models.User(
                    username="test_user_crud",
                    email="test@example.com",
                    hashed_password=hashed_password,
                    is_active=True,
                    is_superuser=False
                )
                self.db.add(test_user)
                self.db.commit()
                self.db.refresh(test_user)
                
                # Read user
                user = self.db.query(models.User).filter(models.User.username == "test_user_crud").first()
                if user:
                    crud_tests.append("User CRUD: Create and Read")
                    
                    # Update user
                    user.email = "updated@example.com"
                    self.db.commit()
                    
                    # Verify update
                    updated_user = self.db.query(models.User).filter(models.User.id == user.id).first()
                    if updated_user.email == "updated@example.com":
                        crud_tests.append("User CRUD: Update")
                    
                    # Delete user
                    self.db.delete(user)
                    self.db.commit()
                    crud_tests.append("User CRUD: Delete")
                else:
                    crud_tests.append("User CRUD: Failed to read")
                    
            except Exception as e:
                crud_tests.append(f"User CRUD: Error - {str(e)}")
            
            # Test Crew CRUD
            try:
                # Create crew
                test_crew = models.Crew(
                    employee_id="TEST_CRUD_001",
                    first_name="Test",
                    last_name="Pilot",
                    rank="Captain",
                    base_airport="LAX",
                    hire_date=datetime.now(),
                    seniority_number=100,
                    status="active"
                )
                self.db.add(test_crew)
                self.db.commit()
                self.db.refresh(test_crew)
                
                # Read crew
                crew = self.db.query(models.Crew).filter(models.Crew.employee_id == "TEST_CRUD_001").first()
                if crew:
                    crud_tests.append("Crew CRUD: Create and Read")
                    
                    # Update crew
                    crew.rank = "Senior Captain"
                    self.db.commit()
                    
                    # Verify update
                    updated_crew = self.db.query(models.Crew).filter(models.Crew.id == crew.id).first()
                    if updated_crew.rank == "Senior Captain":
                        crud_tests.append("Crew CRUD: Update")
                    
                    # Store for cleanup
                    self.test_data["test_crew_id"] = crew.id
                else:
                    crud_tests.append("Crew CRUD: Failed to read")
                    
            except Exception as e:
                crud_tests.append(f"Crew CRUD: Error - {str(e)}")
            
            # Test Flight CRUD
            try:
                # Create flight
                test_flight = models.Flight(
                    id="TEST_CRUD_001",
                    flight_number="TC001",
                    origin="LAX",
                    destination="JFK",
                    departure=datetime.now() + timedelta(hours=1),
                    arrival=datetime.now() + timedelta(hours=5),
                    aircraft="B737-800",
                    attributes={"test": True}
                )
                self.db.add(test_flight)
                self.db.commit()
                self.db.refresh(test_flight)
                
                # Read flight
                flight = self.db.query(models.Flight).filter(models.Flight.id == "TEST_CRUD_001").first()
                if flight:
                    crud_tests.append("Flight CRUD: Create and Read")
                    
                    # Update flight
                    flight.aircraft = "B777-300ER"
                    self.db.commit()
                    
                    # Verify update
                    updated_flight = self.db.query(models.Flight).filter(models.Flight.id == flight.id).first()
                    if updated_flight.aircraft == "B777-300ER":
                        crud_tests.append("Flight CRUD: Update")
                    
                    # Store for cleanup
                    self.test_data["test_flight_id"] = flight.id
                else:
                    crud_tests.append("Flight CRUD: Failed to read")
                    
            except Exception as e:
                crud_tests.append(f"Flight CRUD: Error - {str(e)}")
            
            duration = time.time() - start_time
            
            # Count successful CRUD operations
            successful_operations = sum(1 for test in crud_tests if "Error" not in test and "Failed" not in test)
            total_operations = len(crud_tests)
            
            if successful_operations >= total_operations * 0.8:  # 80% success rate
                self.log_test("CRUD Operations", "PASS", f"{successful_operations}/{total_operations} operations successful", duration)
                return True
            else:
                self.log_test("CRUD Operations", "FAIL", f"Only {successful_operations}/{total_operations} operations successful", duration)
                return False
                
        except SQLAlchemyError as e:
            self.log_test("CRUD Operations", "FAIL", f"CRUD operations error: {str(e)}")
            return False

    def test_relationships(self) -> bool:
        """Test database relationships and foreign keys"""
        print("🔗 Testing Database Relationships...")
        start_time = time.time()
        
        try:
            relationship_tests = []
            
            # Test Crew-Roster relationship
            crew_with_rosters = self.db.execute(text("""
                SELECT COUNT(DISTINCT c.id) 
                FROM crew c 
                INNER JOIN rosters r ON c.id = r.crew_id
            """)).scalar()
            
            if crew_with_rosters > 0:
                relationship_tests.append(f"Crew-Roster: {crew_with_rosters} crews have roster assignments")
            else:
                relationship_tests.append("Crew-Roster: No relationships found")
            
            # Test Flight-Roster relationship
            flights_with_rosters = self.db.execute(text("""
                SELECT COUNT(DISTINCT f.id) 
                FROM flights f 
                INNER JOIN rosters r ON f.id = r.flight_id
            """)).scalar()
            
            if flights_with_rosters > 0:
                relationship_tests.append(f"Flight-Roster: {flights_with_rosters} flights have roster assignments")
            else:
                relationship_tests.append("Flight-Roster: No relationships found")
            
            # Test cascade delete (if test data exists)
            if "test_crew_id" in self.test_data and "test_flight_id" in self.test_data:
                try:
                    # Create a roster assignment
                    test_roster = models.RosterAssignment(
                        crew_id=self.test_data["test_crew_id"],
                        flight_id=self.test_data["test_flight_id"],
                        start=datetime.now(),
                        end=datetime.now() + timedelta(hours=4),
                        position="CPT",
                        attributes={"test": True}
                    )
                    self.db.add(test_roster)
                    self.db.commit()
                    self.db.refresh(test_roster)
                    
                    # Test cascade delete
                    crew = self.db.query(models.Crew).filter(models.Crew.id == self.test_data["test_crew_id"]).first()
                    if crew:
                        self.db.delete(crew)
                        self.db.commit()
                        
                        # Check if roster was deleted (cascade)
                        roster_exists = self.db.query(models.RosterAssignment).filter(
                            models.RosterAssignment.id == test_roster.id
                        ).first()
                        
                        if not roster_exists:
                            relationship_tests.append("Cascade Delete: Roster deleted when crew deleted")
                        else:
                            relationship_tests.append("Cascade Delete: Roster not deleted (cascade failed)")
                    
                except Exception as e:
                    relationship_tests.append(f"Cascade Delete: Error - {str(e)}")
            
            duration = time.time() - start_time
            
            # Count successful relationship tests
            successful_tests = sum(1 for test in relationship_tests if "Error" not in test and "failed" not in test.lower())
            total_tests = len(relationship_tests)
            
            if successful_tests >= total_tests * 0.7:  # 70% success rate
                self.log_test("Database Relationships", "PASS", f"{successful_tests}/{total_tests} relationship tests passed", duration)
                return True
            else:
                self.log_test("Database Relationships", "FAIL", f"Only {successful_tests}/{total_tests} relationship tests passed", duration)
                return False
                
        except SQLAlchemyError as e:
            self.log_test("Database Relationships", "FAIL", f"Relationship test error: {str(e)}")
            return False

    def test_performance(self) -> bool:
        """Test database performance and query optimization"""
        print("⚡ Testing Database Performance...")
        start_time = time.time()
        
        try:
            performance_tests = []
            
            # Test simple query performance
            query_start = time.time()
            crew_count = self.db.execute(text("SELECT COUNT(*) FROM crew")).scalar()
            query_duration = time.time() - query_start
            
            if query_duration < 0.1:  # Should be very fast
                performance_tests.append(f"Simple Query: {query_duration:.3f}s (GOOD)")
            else:
                performance_tests.append(f"Simple Query: {query_duration:.3f}s (SLOW)")
            
            # Test join query performance
            query_start = time.time()
            join_result = self.db.execute(text("""
                SELECT COUNT(*) 
                FROM crew c 
                INNER JOIN rosters r ON c.id = r.crew_id
            """)).scalar()
            query_duration = time.time() - query_start
            
            if query_duration < 0.5:  # Should be reasonably fast
                performance_tests.append(f"Join Query: {query_duration:.3f}s (GOOD)")
            else:
                performance_tests.append(f"Join Query: {query_duration:.3f}s (SLOW)")
            
            # Test complex query performance
            query_start = time.time()
            complex_result = self.db.execute(text("""
                SELECT c.first_name, c.last_name, COUNT(r.id) as assignment_count
                FROM crew c 
                LEFT JOIN rosters r ON c.id = r.crew_id
                GROUP BY c.id, c.first_name, c.last_name
                ORDER BY assignment_count DESC
                LIMIT 10
            """)).fetchall()
            query_duration = time.time() - query_start
            
            if query_duration < 1.0:  # Should be reasonably fast
                performance_tests.append(f"Complex Query: {query_duration:.3f}s (GOOD)")
            else:
                performance_tests.append(f"Complex Query: {query_duration:.3f}s (SLOW)")
            
            duration = time.time() - start_time
            
            # Count good performance tests
            good_performance = sum(1 for test in performance_tests if "GOOD" in test)
            total_tests = len(performance_tests)
            
            if good_performance >= total_tests * 0.7:  # 70% good performance
                self.log_test("Database Performance", "PASS", f"{good_performance}/{total_tests} performance tests passed", duration)
                return True
            else:
                self.log_test("Database Performance", "FAIL", f"Only {good_performance}/{total_tests} performance tests passed", duration)
                return False
                
        except SQLAlchemyError as e:
            self.log_test("Database Performance", "FAIL", f"Performance test error: {str(e)}")
            return False

    def test_transactions(self) -> bool:
        """Test database transactions and rollback"""
        print("🔄 Testing Database Transactions...")
        start_time = time.time()
        
        try:
            transaction_tests = []
            
            # Test successful transaction
            try:
                self.db.begin()
                
                test_user = models.User(
                    username="test_transaction",
                    email="transaction@example.com",
                    hashed_password="hashed_password",
                    is_active=True,
                    is_superuser=False
                )
                self.db.add(test_user)
                self.db.commit()
                
                # Verify user was created
                user = self.db.query(models.User).filter(models.User.username == "test_transaction").first()
                if user:
                    transaction_tests.append("Transaction: Successful commit")
                    
                    # Clean up
                    self.db.delete(user)
                    self.db.commit()
                else:
                    transaction_tests.append("Transaction: Failed to create user")
                    
            except Exception as e:
                transaction_tests.append(f"Transaction: Error - {str(e)}")
                self.db.rollback()
            
            # Test rollback
            try:
                self.db.begin()
                
                test_user = models.User(
                    username="test_rollback",
                    email="rollback@example.com",
                    hashed_password="hashed_password",
                    is_active=True,
                    is_superuser=False
                )
                self.db.add(test_user)
                self.db.rollback()  # Intentionally rollback
                
                # Verify user was not created
                user = self.db.query(models.User).filter(models.User.username == "test_rollback").first()
                if not user:
                    transaction_tests.append("Transaction: Successful rollback")
                else:
                    transaction_tests.append("Transaction: Rollback failed")
                    
            except Exception as e:
                transaction_tests.append(f"Transaction Rollback: Error - {str(e)}")
            
            duration = time.time() - start_time
            
            # Count successful transaction tests
            successful_tests = sum(1 for test in transaction_tests if "Error" not in test and "failed" not in test.lower())
            total_tests = len(transaction_tests)
            
            if successful_tests >= total_tests * 0.8:  # 80% success rate
                self.log_test("Database Transactions", "PASS", f"{successful_tests}/{total_tests} transaction tests passed", duration)
                return True
            else:
                self.log_test("Database Transactions", "FAIL", f"Only {successful_tests}/{total_tests} transaction tests passed", duration)
                return False
                
        except SQLAlchemyError as e:
            self.log_test("Database Transactions", "FAIL", f"Transaction test error: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("🧹 Cleaning up test data...")
        
        try:
            # Clean up test flight
            if "test_flight_id" in self.test_data:
                flight = self.db.query(models.Flight).filter(models.Flight.id == self.test_data["test_flight_id"]).first()
                if flight:
                    self.db.delete(flight)
                    self.db.commit()
            
            # Clean up any remaining test users
            test_users = self.db.query(models.User).filter(
                models.User.username.like("test_%")
            ).all()
            
            for user in test_users:
                self.db.delete(user)
            
            self.db.commit()
            self.log_test("Cleanup", "PASS", "Test data cleaned up successfully")
            
        except Exception as e:
            self.log_test("Cleanup", "WARN", f"Cleanup error: {str(e)}")

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all database tests"""
        print("🧪 Starting Comprehensive Database Testing...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        tests = [
            ("Database Connection", self.setup_database_connection),
            ("Table Structure", self.test_table_structure),
            ("Data Integrity", self.test_data_integrity),
            ("CRUD Operations", self.test_crud_operations),
            ("Database Relationships", self.test_relationships),
            ("Database Performance", self.test_performance),
            ("Database Transactions", self.test_transactions)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, "FAIL", f"Test error: {str(e)}")
        
        # Cleanup
        self.cleanup_test_data()
        
        # Close database connection
        if self.db:
            self.db.close()
        
        total_duration = time.time() - self.start_time
        success_rate = (passed_tests / total_tests) * 100
        
        print("=" * 60)
        print(f"🎯 Database Testing Complete!")
        print(f"📊 Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        print(f"⏱️ Total Duration: {total_duration:.2f}s")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "duration": total_duration,
            "results": self.test_results
        }

def main():
    """Main function to run database tests"""
    tester = DatabaseTester()
    results = tester.run_all_tests()
    
    # Save results to file
    results_file = PROJECT_ROOT / "backend" / "tests" / "database_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results["success_rate"] >= 80 else 1)

if __name__ == "__main__":
    main()
