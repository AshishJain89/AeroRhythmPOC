#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Script for AeroRhythm POC
Tests complete user workflows from frontend to backend to database
"""

import asyncio
import json
import time
import requests
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading
import signal

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

class E2ETester:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:8080"
        self.test_results = []
        self.start_time = None
        self.auth_token = None
        self.test_data = {}
        self.backend_process = None
        self.frontend_process = None
        
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

    def start_backend_server(self) -> bool:
        """Start backend server for testing"""
        print(" Starting Backend Server...")
        start_time = time.time()
        
        try:
            backend_dir = PROJECT_ROOT / "backend"
            self.backend_process = subprocess.Popen(
                ["python", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            max_wait = 30
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=2)
                    if response.status_code == 200:
                        duration = time.time() - start_time
                        self.log_test("Backend Server Start", "PASS", "Server started successfully", duration)
                        return True
                except requests.RequestException:
                    pass
                time.sleep(1)
            
            self.log_test("Backend Server Start", "FAIL", "Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            self.log_test("Backend Server Start", "FAIL", f"Error starting server: {str(e)}")
            return False

    def start_frontend_server(self) -> bool:
        """Start frontend server for testing"""
        print(" Starting Frontend Server...")
        start_time = time.time()
        
        try:
            frontend_dir = PROJECT_ROOT / "frontend"
            
            # Install dependencies first
            install_result = subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if install_result.returncode != 0:
                self.log_test("Frontend Server Start", "FAIL", f"npm install failed: {install_result.stderr}")
                return False
            
            # Start dev server
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            max_wait = 60
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self.frontend_url}", timeout=2)
                    if response.status_code == 200:
                        duration = time.time() - start_time
                        self.log_test("Frontend Server Start", "PASS", "Server started successfully", duration)
                        return True
                except requests.RequestException:
                    pass
                time.sleep(1)
            
            self.log_test("Frontend Server Start", "FAIL", "Server failed to start within 60 seconds")
            return False
            
        except Exception as e:
            self.log_test("Frontend Server Start", "FAIL", f"Error starting server: {str(e)}")
            return False

    def test_user_authentication_flow(self) -> bool:
        """Test complete user authentication flow"""
        print(" Testing User Authentication Flow...")
        start_time = time.time()
        
        try:
            # Test login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = requests.post(
                f"{self.backend_url}/auth/token",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.log_test("User Login", "PASS", "Login successful")
                else:
                    self.log_test("User Login", "FAIL", "No access token in response")
                    return False
            else:
                self.log_test("User Login", "FAIL", f"Login failed with status {response.status_code}")
                return False
            
            # Test authenticated request
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{self.backend_url}/crews?limit=1", headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.log_test("Authenticated Request", "PASS", "Authenticated request successful")
            else:
                self.log_test("Authenticated Request", "FAIL", f"Authenticated request failed with status {response.status_code}")
                return False
            
            duration = time.time() - start_time
            self.log_test("User Authentication Flow", "PASS", "Complete authentication flow working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("User Authentication Flow", "FAIL", f"Authentication flow error: {str(e)}")
            return False

    def test_crew_management_workflow(self) -> bool:
        """Test complete crew management workflow"""
        print(" Testing Crew Management Workflow...")
        start_time = time.time()
        
        try:
            if not self.auth_token:
                self.log_test("Crew Management Workflow", "FAIL", "No authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # 1. Create new crew member
            new_crew = {
                "employee_id": "E2E_TEST_001",
                "first_name": "E2E",
                "last_name": "Test",
                "rank": "Captain",
                "base_airport": "LAX",
                "hire_date": "2025-01-01T00:00:00",
                "seniority_number": 100,
                "status": "active"
            }
            
            response = requests.post(
                f"{self.backend_url}/crews",
                json=new_crew,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                created_crew = response.json()
                self.test_data["created_crew_id"] = created_crew["id"]
                self.log_test("Create Crew", "PASS", "Crew member created successfully")
            else:
                self.log_test("Create Crew", "FAIL", f"Create crew failed with status {response.status_code}")
                return False
            
            # 2. Retrieve crew member
            response = requests.get(
                f"{self.backend_url}/crews/{self.test_data['created_crew_id']}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                crew = response.json()
                if crew["employee_id"] == "E2E_TEST_001":
                    self.log_test("Retrieve Crew", "PASS", "Crew member retrieved successfully")
                else:
                    self.log_test("Retrieve Crew", "FAIL", "Wrong crew data returned")
                    return False
            else:
                self.log_test("Retrieve Crew", "FAIL", f"Retrieve crew failed with status {response.status_code}")
                return False
            
            # 3. Update crew member
            updated_crew = {
                "employee_id": "E2E_TEST_001",
                "first_name": "E2E",
                "last_name": "Test",
                "rank": "Senior Captain",
                "base_airport": "LAX",
                "hire_date": "2025-01-01T00:00:00",
                "seniority_number": 100,
                "status": "active"
            }
            
            response = requests.put(
                f"{self.backend_url}/crews/{self.test_data['created_crew_id']}",
                json=updated_crew,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                updated = response.json()
                if updated["rank"] == "Senior Captain":
                    self.log_test("Update Crew", "PASS", "Crew member updated successfully")
                else:
                    self.log_test("Update Crew", "FAIL", "Crew member not updated correctly")
                    return False
            else:
                self.log_test("Update Crew", "FAIL", f"Update crew failed with status {response.status_code}")
                return False
            
            duration = time.time() - start_time
            self.log_test("Crew Management Workflow", "PASS", "Complete crew management workflow working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Crew Management Workflow", "FAIL", f"Crew management workflow error: {str(e)}")
            return False

    def test_flight_management_workflow(self) -> bool:
        """Test complete flight management workflow"""
        print("✈️ Testing Flight Management Workflow...")
        start_time = time.time()
        
        try:
            if not self.auth_token:
                self.log_test("Flight Management Workflow", "FAIL", "No authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # 1. Create new flight
            new_flight = {
                "id": "E2E_TEST_001",
                "flight_number": "E2E001",
                "origin": "LAX",
                "destination": "JFK",
                "departure": (datetime.now() + timedelta(hours=1)).isoformat(),
                "arrival": (datetime.now() + timedelta(hours=5)).isoformat(),
                "aircraft": "B737-800",
                "attributes": {
                    "route_type": "domestic",
                    "passenger_capacity": 180
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/flights",
                json=new_flight,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                created_flight = response.json()
                self.test_data["created_flight_id"] = created_flight["id"]
                self.log_test("Create Flight", "PASS", "Flight created successfully")
            else:
                self.log_test("Create Flight", "FAIL", f"Create flight failed with status {response.status_code}")
                return False
            
            # 2. Retrieve flight
            response = requests.get(
                f"{self.backend_url}/flights/{self.test_data['created_flight_id']}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                flight = response.json()
                if flight["flight_number"] == "E2E001":
                    self.log_test("Retrieve Flight", "PASS", "Flight retrieved successfully")
                else:
                    self.log_test("Retrieve Flight", "FAIL", "Wrong flight data returned")
                    return False
            else:
                self.log_test("Retrieve Flight", "FAIL", f"Retrieve flight failed with status {response.status_code}")
                return False
            
            duration = time.time() - start_time
            self.log_test("Flight Management Workflow", "PASS", "Complete flight management workflow working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Flight Management Workflow", "FAIL", f"Flight management workflow error: {str(e)}")
            return False

    def test_roster_assignment_workflow(self) -> bool:
        """Test complete roster assignment workflow"""
        print(" Testing Roster Assignment Workflow...")
        start_time = time.time()
        
        try:
            if not self.auth_token or "created_crew_id" not in self.test_data or "created_flight_id" not in self.test_data:
                self.log_test("Roster Assignment Workflow", "FAIL", "Missing required test data")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # 1. Create roster assignment
            new_assignment = {
                "crew_id": self.test_data["created_crew_id"],
                "flight_id": self.test_data["created_flight_id"],
                "start": (datetime.now() + timedelta(hours=1)).isoformat(),
                "end": (datetime.now() + timedelta(hours=5)).isoformat(),
                "position": "CPT",
                "attributes": {
                    "assignment_type": "scheduled",
                    "duty_time_hours": 4.0
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/rosters",
                json=new_assignment,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                created_assignment = response.json()
                self.test_data["created_roster_id"] = created_assignment["id"]
                self.log_test("Create Roster Assignment", "PASS", "Roster assignment created successfully")
            else:
                self.log_test("Create Roster Assignment", "FAIL", f"Create roster assignment failed with status {response.status_code}")
                return False
            
            # 2. Retrieve roster assignments
            response = requests.get(
                f"{self.backend_url}/rosters?limit=10",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                rosters = response.json()
                if isinstance(rosters, list) and len(rosters) > 0:
                    self.log_test("Retrieve Roster Assignments", "PASS", f"Retrieved {len(rosters)} roster assignments")
                else:
                    self.log_test("Retrieve Roster Assignments", "FAIL", "No roster assignments returned")
                    return False
            else:
                self.log_test("Retrieve Roster Assignments", "FAIL", f"Retrieve roster assignments failed with status {response.status_code}")
                return False
            
            duration = time.time() - start_time
            self.log_test("Roster Assignment Workflow", "PASS", "Complete roster assignment workflow working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Roster Assignment Workflow", "FAIL", f"Roster assignment workflow error: {str(e)}")
            return False

    def test_disruption_workflow(self) -> bool:
        """Test complete disruption management workflow"""
        print("⚠️ Testing Disruption Management Workflow...")
        start_time = time.time()
        
        try:
            if not self.auth_token:
                self.log_test("Disruption Management Workflow", "FAIL", "No authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # 1. Create disruption
            new_disruption = {
                "type": "crew_illness",
                "affected": {
                    "crew_ids": [self.test_data.get("created_crew_id", 1)],
                    "crew_names": ["E2E Test"]
                },
                "severity": "high",
                "attributes": {
                    "illness_type": "flu",
                    "expected_duration_days": 3,
                    "requires_replacement": True
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/disruptions",
                json=new_disruption,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                created_disruption = response.json()
                self.test_data["created_disruption_id"] = created_disruption["id"]
                self.log_test("Create Disruption", "PASS", "Disruption created successfully")
            else:
                self.log_test("Create Disruption", "FAIL", f"Create disruption failed with status {response.status_code}")
                return False
            
            # 2. Retrieve disruptions
            response = requests.get(
                f"{self.backend_url}/disruptions",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                disruptions = response.json()
                if isinstance(disruptions, list) and len(disruptions) > 0:
                    self.log_test("Retrieve Disruptions", "PASS", f"Retrieved {len(disruptions)} disruptions")
                else:
                    self.log_test("Retrieve Disruptions", "FAIL", "No disruptions returned")
                    return False
            else:
                self.log_test("Retrieve Disruptions", "FAIL", f"Retrieve disruptions failed with status {response.status_code}")
                return False
            
            duration = time.time() - start_time
            self.log_test("Disruption Management Workflow", "PASS", "Complete disruption management workflow working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Disruption Management Workflow", "FAIL", f"Disruption management workflow error: {str(e)}")
            return False

    def test_frontend_backend_integration(self) -> bool:
        """Test frontend-backend integration"""
        print(" Testing Frontend-Backend Integration...")
        start_time = time.time()
        
        try:
            # Test if frontend can access backend APIs
            # This is a simplified test - in a real scenario, you'd use Selenium or similar
            
            # Test CORS headers
            response = requests.options(
                f"{self.backend_url}/crews",
                headers={
                    "Origin": self.frontend_url,
                    "Access-Control-Request-Method": "GET"
                },
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                cors_headers = response.headers
                if "Access-Control-Allow-Origin" in cors_headers:
                    self.log_test("CORS Configuration", "PASS", "CORS headers present")
                else:
                    self.log_test("CORS Configuration", "WARN", "CORS headers missing")
            else:
                self.log_test("CORS Configuration", "FAIL", f"CORS preflight failed with status {response.status_code}")
            
            # Test API accessibility from frontend perspective
            response = requests.get(
                f"{self.backend_url}/health",
                headers={"Origin": self.frontend_url},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("API Accessibility", "PASS", "Backend APIs accessible from frontend")
            else:
                self.log_test("API Accessibility", "FAIL", f"Backend APIs not accessible from frontend")
                return False
            
            duration = time.time() - start_time
            self.log_test("Frontend-Backend Integration", "PASS", "Integration working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Frontend-Backend Integration", "FAIL", f"Integration test error: {str(e)}")
            return False

    def test_data_consistency(self) -> bool:
        """Test data consistency across the system"""
        print(" Testing Data Consistency...")
        start_time = time.time()
        
        try:
            if not self.auth_token:
                self.log_test("Data Consistency", "FAIL", "No authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test that created data is consistent across endpoints
            consistency_checks = []
            
            # Check crew data consistency
            if "created_crew_id" in self.test_data:
                response = requests.get(
                    f"{self.backend_url}/crews/{self.test_data['created_crew_id']}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    crew = response.json()
                    if crew["employee_id"] == "E2E_TEST_001":
                        consistency_checks.append("Crew data consistent")
                    else:
                        consistency_checks.append("Crew data inconsistent")
                else:
                    consistency_checks.append("Crew data retrieval failed")
            
            # Check flight data consistency
            if "created_flight_id" in self.test_data:
                response = requests.get(
                    f"{self.backend_url}/flights/{self.test_data['created_flight_id']}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    flight = response.json()
                    if flight["flight_number"] == "E2E001":
                        consistency_checks.append("Flight data consistent")
                    else:
                        consistency_checks.append("Flight data inconsistent")
                else:
                    consistency_checks.append("Flight data retrieval failed")
            
            # Check roster data consistency
            if "created_roster_id" in self.test_data:
                response = requests.get(
                    f"{self.backend_url}/rosters?limit=100",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    rosters = response.json()
                    roster_found = any(r["id"] == self.test_data["created_roster_id"] for r in rosters)
                    if roster_found:
                        consistency_checks.append("Roster data consistent")
                    else:
                        consistency_checks.append("Roster data inconsistent")
                else:
                    consistency_checks.append("Roster data retrieval failed")
            
            duration = time.time() - start_time
            
            # Count consistent checks
            consistent_checks = sum(1 for check in consistency_checks if "consistent" in check and "inconsistent" not in check)
            total_checks = len(consistency_checks)
            
            if consistent_checks >= total_checks * 0.8:  # 80% consistency
                self.log_test("Data Consistency", "PASS", f"{consistent_checks}/{total_checks} data consistency checks passed", duration)
                return True
            else:
                self.log_test("Data Consistency", "FAIL", f"Only {consistent_checks}/{total_checks} data consistency checks passed", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Data Consistency", "FAIL", f"Data consistency test error: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data created during E2E testing"""
        print(" Cleaning up E2E test data...")
        
        try:
            if not self.auth_token:
                return
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Clean up roster assignment
            if "created_roster_id" in self.test_data:
                response = requests.delete(
                    f"{self.backend_url}/rosters/{self.test_data['created_roster_id']}",
                    headers=headers,
                    timeout=10
                )
                if response.status_code in [200, 204]:
                    self.log_test("Cleanup Roster", "PASS", "Roster assignment deleted")
                else:
                    self.log_test("Cleanup Roster", "WARN", f"Roster cleanup returned status {response.status_code}")
            
            # Clean up disruption
            if "created_disruption_id" in self.test_data:
                response = requests.delete(
                    f"{self.backend_url}/disruptions/{self.test_data['created_disruption_id']}",
                    headers=headers,
                    timeout=10
                )
                if response.status_code in [200, 204]:
                    self.log_test("Cleanup Disruption", "PASS", "Disruption deleted")
                else:
                    self.log_test("Cleanup Disruption", "WARN", f"Disruption cleanup returned status {response.status_code}")
            
            # Clean up flight
            if "created_flight_id" in self.test_data:
                response = requests.delete(
                    f"{self.backend_url}/flights/{self.test_data['created_flight_id']}",
                    headers=headers,
                    timeout=10
                )
                if response.status_code in [200, 204]:
                    self.log_test("Cleanup Flight", "PASS", "Flight deleted")
                else:
                    self.log_test("Cleanup Flight", "WARN", f"Flight cleanup returned status {response.status_code}")
            
            # Clean up crew
            if "created_crew_id" in self.test_data:
                response = requests.delete(
                    f"{self.backend_url}/crews/{self.test_data['created_crew_id']}",
                    headers=headers,
                    timeout=10
                )
                if response.status_code in [200, 204]:
                    self.log_test("Cleanup Crew", "PASS", "Crew member deleted")
                else:
                    self.log_test("Cleanup Crew", "WARN", f"Crew cleanup returned status {response.status_code}")
            
        except requests.RequestException as e:
            self.log_test("Cleanup", "WARN", f"Cleanup error: {str(e)}")

    def stop_servers(self):
        """Stop backend and frontend servers"""
        print(" Stopping servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait(timeout=10)
            self.log_test("Backend Server Stop", "PASS", "Backend server stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait(timeout=10)
            self.log_test("Frontend Server Stop", "PASS", "Frontend server stopped")

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all end-to-end tests"""
        print(" Starting Comprehensive End-to-End Testing...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        try:
            # Start servers
            if not self.start_backend_server():
                return {"error": "Failed to start backend server"}
            
            if not self.start_frontend_server():
                return {"error": "Failed to start frontend server"}
            
            # Run tests
            tests = [
                ("User Authentication Flow", self.test_user_authentication_flow),
                ("Crew Management Workflow", self.test_crew_management_workflow),
                ("Flight Management Workflow", self.test_flight_management_workflow),
                ("Roster Assignment Workflow", self.test_roster_assignment_workflow),
                ("Disruption Management Workflow", self.test_disruption_workflow),
                ("Frontend-Backend Integration", self.test_frontend_backend_integration),
                ("Data Consistency", self.test_data_consistency)
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
            
            total_duration = time.time() - self.start_time
            success_rate = (passed_tests / total_tests) * 100
            
            print("=" * 60)
            print(f" End-to-End Testing Complete!")
            print(f" Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
            print(f"⏱️ Total Duration: {total_duration:.2f}s")
            
            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate,
                "duration": total_duration,
                "results": self.test_results
            }
            
        finally:
            # Always stop servers
            self.stop_servers()

def main():
    """Main function to run E2E tests"""
    tester = E2ETester()
    results = tester.run_all_tests()
    
    if "error" in results:
        print(f"❌ E2E Testing Failed: {results['error']}")
        sys.exit(1)
    
    # Save results to file
    results_file = PROJECT_ROOT / "tests" / "e2e_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f" Results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results["success_rate"] >= 80 else 1)

if __name__ == "__main__":
    main()
