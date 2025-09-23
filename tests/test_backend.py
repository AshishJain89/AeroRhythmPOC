#!/usr/bin/env python3
"""
Comprehensive Backend Testing Script for AeroRhythm POC
Tests all backend functionality including APIs, authentication, and business logic
"""

import asyncio
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

class BackendTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_results = []
        self.start_time = None
        self.auth_token = None
        self.test_data = {}
        
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

    def test_server_health(self) -> bool:
        """Test if backend server is running and healthy"""
        print(" Testing Server Health...")
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.log_test("Server Health", "PASS", "Server is healthy", duration)
                    return True
                else:
                    self.log_test("Server Health", "FAIL", f"Unexpected health response: {data}", duration)
                    return False
            else:
                self.log_test("Server Health", "FAIL", f"Health check failed with status {response.status_code}", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Server Health", "FAIL", f"Could not connect to server: {str(e)}")
            return False

    def test_api_documentation(self) -> bool:
        """Test API documentation endpoints"""
        print(" Testing API Documentation...")
        start_time = time.time()
        
        try:
            # Test Swagger UI
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("API Documentation", "PASS", "Swagger UI accessible", duration)
                return True
            else:
                self.log_test("API Documentation", "FAIL", f"Swagger UI returned status {response.status_code}", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("API Documentation", "FAIL", f"Could not access API docs: {str(e)}")
            return False

    def test_authentication(self) -> bool:
        """Test authentication system"""
        print(" Testing Authentication...")
        start_time = time.time()
        
        try:
            # Test login with valid credentials
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/token",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.log_test("Authentication", "PASS", "Login successful", duration)
                    return True
                else:
                    self.log_test("Authentication", "FAIL", "No access token in response", duration)
                    return False
            else:
                self.log_test("Authentication", "FAIL", f"Login failed with status {response.status_code}", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Authentication", "FAIL", f"Authentication error: {str(e)}")
            return False

    def test_crew_endpoints(self) -> bool:
        """Test crew management endpoints"""
        print(" Testing Crew Endpoints...")
        start_time = time.time()
        
        try:
            # Test GET /crews
            response = requests.get(f"{self.base_url}/crews?skip=0&limit=5", timeout=10)
            
            if response.status_code == 200:
                crews = response.json()
                if isinstance(crews, list) and len(crews) > 0:
                    self.test_data["crew_id"] = crews[0]["id"]
                    self.log_test("GET /crews", "PASS", f"Retrieved {len(crews)} crew members")
                else:
                    self.log_test("GET /crews", "FAIL", "No crew data returned")
                    return False
            else:
                self.log_test("GET /crews", "FAIL", f"GET /crews failed with status {response.status_code}")
                return False
            
            # Test GET /crews/{id}
            if "crew_id" in self.test_data:
                response = requests.get(f"{self.base_url}/crews/{self.test_data['crew_id']}", timeout=10)
                if response.status_code == 200:
                    crew = response.json()
                    if crew.get("id") == self.test_data["crew_id"]:
                        self.log_test("GET /crews/{id}", "PASS", "Retrieved specific crew member")
                    else:
                        self.log_test("GET /crews/{id}", "FAIL", "Wrong crew data returned")
                        return False
                else:
                    self.log_test("GET /crews/{id}", "FAIL", f"GET /crews/{{id}} failed with status {response.status_code}")
                    return False
            
            # Test POST /crews (requires authentication)
            if self.auth_token:
                new_crew = {
                    "employee_id": "TEST001",
                    "first_name": "Test",
                    "last_name": "Pilot",
                    "rank": "Captain",
                    "base_airport": "LAX",
                    "hire_date": "2025-01-01T00:00:00",
                    "seniority_number": 100,
                    "status": "active"
                }
                
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = requests.post(
                    f"{self.base_url}/crews",
                    json=new_crew,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 201:
                    created_crew = response.json()
                    self.test_data["created_crew_id"] = created_crew["id"]
                    self.log_test("POST /crews", "PASS", "Created new crew member")
                else:
                    self.log_test("POST /crews", "FAIL", f"POST /crews failed with status {response.status_code}")
                    return False
            
            duration = time.time() - start_time
            self.log_test("Crew Endpoints", "PASS", "All crew endpoints working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Crew Endpoints", "FAIL", f"Crew endpoint error: {str(e)}")
            return False

    def test_flight_endpoints(self) -> bool:
        """Test flight management endpoints"""
        print("✈️ Testing Flight Endpoints...")
        start_time = time.time()
        
        try:
            # Test GET /flights
            response = requests.get(f"{self.base_url}/flights?skip=0&limit=5", timeout=10)
            
            if response.status_code == 200:
                flights = response.json()
                if isinstance(flights, list) and len(flights) > 0:
                    self.test_data["flight_id"] = flights[0]["id"]
                    self.log_test("GET /flights", "PASS", f"Retrieved {len(flights)} flights")
                else:
                    self.log_test("GET /flights", "FAIL", "No flight data returned")
                    return False
            else:
                self.log_test("GET /flights", "FAIL", f"GET /flights failed with status {response.status_code}")
                return False
            
            # Test GET /flights/{id}
            if "flight_id" in self.test_data:
                response = requests.get(f"{self.base_url}/flights/{self.test_data['flight_id']}", timeout=10)
                if response.status_code == 200:
                    flight = response.json()
                    if flight.get("id") == self.test_data["flight_id"]:
                        self.log_test("GET /flights/{id}", "PASS", "Retrieved specific flight")
                    else:
                        self.log_test("GET /flights/{id}", "FAIL", "Wrong flight data returned")
                        return False
                else:
                    self.log_test("GET /flights/{id}", "FAIL", f"GET /flights/{{id}} failed with status {response.status_code}")
                    return False
            
            duration = time.time() - start_time
            self.log_test("Flight Endpoints", "PASS", "All flight endpoints working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Flight Endpoints", "FAIL", f"Flight endpoint error: {str(e)}")
            return False

    def test_roster_endpoints(self) -> bool:
        """Test roster management endpoints"""
        print(" Testing Roster Endpoints...")
        start_time = time.time()
        
        try:
            # Test GET /rosters
            response = requests.get(f"{self.base_url}/rosters?skip=0&limit=5", timeout=10)
            
            if response.status_code == 200:
                rosters = response.json()
                if isinstance(rosters, list) and len(rosters) > 0:
                    self.test_data["roster_id"] = rosters[0]["id"]
                    self.log_test("GET /rosters", "PASS", f"Retrieved {len(rosters)} roster assignments")
                else:
                    self.log_test("GET /rosters", "FAIL", "No roster data returned")
                    return False
            else:
                self.log_test("GET /rosters", "FAIL", f"GET /rosters failed with status {response.status_code}")
                return False
            
            duration = time.time() - start_time
            self.log_test("Roster Endpoints", "PASS", "All roster endpoints working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Roster Endpoints", "FAIL", f"Roster endpoint error: {str(e)}")
            return False

    def test_disruption_endpoints(self) -> bool:
        """Test disruption management endpoints"""
        print("⚠️ Testing Disruption Endpoints...")
        start_time = time.time()
        
        try:
            # Test GET /disruptions
            response = requests.get(f"{self.base_url}/disruptions", timeout=10)
            
            if response.status_code == 200:
                disruptions = response.json()
                if isinstance(disruptions, list):
                    self.log_test("GET /disruptions", "PASS", f"Retrieved {len(disruptions)} disruptions")
                else:
                    self.log_test("GET /disruptions", "FAIL", "Invalid disruption data format")
                    return False
            else:
                self.log_test("GET /disruptions", "FAIL", f"GET /disruptions failed with status {response.status_code}")
                return False
            
            duration = time.time() - start_time
            self.log_test("Disruption Endpoints", "PASS", "All disruption endpoints working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Disruption Endpoints", "FAIL", f"Disruption endpoint error: {str(e)}")
            return False

    def test_job_endpoints(self) -> bool:
        """Test job management endpoints"""
        print("⚙️ Testing Job Endpoints...")
        start_time = time.time()
        
        try:
            # Test GET /jobs
            response = requests.get(f"{self.base_url}/jobs", timeout=10)
            
            if response.status_code == 200:
                jobs = response.json()
                if isinstance(jobs, list):
                    self.log_test("GET /jobs", "PASS", f"Retrieved {len(jobs)} jobs")
                else:
                    self.log_test("GET /jobs", "FAIL", "Invalid job data format")
                    return False
            else:
                self.log_test("GET /jobs", "FAIL", f"GET /jobs failed with status {response.status_code}")
                return False
            
            duration = time.time() - start_time
            self.log_test("Job Endpoints", "PASS", "All job endpoints working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Job Endpoints", "FAIL", f"Job endpoint error: {str(e)}")
            return False

    def test_error_handling(self) -> bool:
        """Test error handling and validation"""
        print(" Testing Error Handling...")
        start_time = time.time()
        
        try:
            # Test 404 error
            response = requests.get(f"{self.base_url}/crews/99999", timeout=10)
            if response.status_code == 404:
                self.log_test("404 Error Handling", "PASS", "Correctly returns 404 for non-existent resource")
            else:
                self.log_test("404 Error Handling", "FAIL", f"Expected 404, got {response.status_code}")
                return False
            
            # Test invalid data validation
            invalid_crew = {
                "employee_id": "",  # Invalid empty ID
                "first_name": "",   # Invalid empty name
                "rank": "InvalidRank"  # Invalid rank
            }
            
            if self.auth_token:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = requests.post(
                    f"{self.base_url}/crews",
                    json=invalid_crew,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 422:  # Validation error
                    self.log_test("Data Validation", "PASS", "Correctly validates input data")
                else:
                    self.log_test("Data Validation", "FAIL", f"Expected 422, got {response.status_code}")
                    return False
            
            duration = time.time() - start_time
            self.log_test("Error Handling", "PASS", "All error handling working", duration)
            return True
            
        except requests.RequestException as e:
            self.log_test("Error Handling", "FAIL", f"Error handling test error: {str(e)}")
            return False

    def test_performance(self) -> bool:
        """Test API performance"""
        print("⚡ Testing API Performance...")
        start_time = time.time()
        
        try:
            # Test response times for key endpoints
            endpoints = [
                ("/health", 0.1),      # Should be very fast
                ("/crews?limit=10", 1.0),  # Should be fast
                ("/flights?limit=10", 1.0), # Should be fast
                ("/rosters?limit=10", 1.0)  # Should be fast
            ]
            
            performance_passed = 0
            for endpoint, max_time in endpoints:
                endpoint_start = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                endpoint_duration = time.time() - endpoint_start
                
                if response.status_code == 200 and endpoint_duration <= max_time:
                    performance_passed += 1
                    self.log_test(f"Performance {endpoint}", "PASS", f"Response time: {endpoint_duration:.3f}s")
                else:
                    self.log_test(f"Performance {endpoint}", "FAIL", f"Response time: {endpoint_duration:.3f}s (max: {max_time}s)")
            
            duration = time.time() - start_time
            
            if performance_passed >= len(endpoints) * 0.75:  # 75% pass rate
                self.log_test("API Performance", "PASS", f"{performance_passed}/{len(endpoints)} endpoints met performance criteria", duration)
                return True
            else:
                self.log_test("API Performance", "FAIL", f"Only {performance_passed}/{len(endpoints)} endpoints met performance criteria", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("API Performance", "FAIL", f"Performance test error: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print(" Cleaning up test data...")
        
        try:
            if self.auth_token and "created_crew_id" in self.test_data:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = requests.delete(
                    f"{self.base_url}/crews/{self.test_data['created_crew_id']}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 204]:
                    self.log_test("Cleanup", "PASS", "Test data cleaned up successfully")
                else:
                    self.log_test("Cleanup", "WARN", f"Cleanup returned status {response.status_code}")
                    
        except requests.RequestException as e:
            self.log_test("Cleanup", "WARN", f"Cleanup error: {str(e)}")

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all backend tests"""
        print(" Starting Comprehensive Backend Testing...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        tests = [
            ("Server Health", self.test_server_health),
            ("API Documentation", self.test_api_documentation),
            ("Authentication", self.test_authentication),
            ("Crew Endpoints", self.test_crew_endpoints),
            ("Flight Endpoints", self.test_flight_endpoints),
            ("Roster Endpoints", self.test_roster_endpoints),
            ("Disruption Endpoints", self.test_disruption_endpoints),
            ("Job Endpoints", self.test_job_endpoints),
            ("Error Handling", self.test_error_handling),
            ("API Performance", self.test_performance)
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
        print(f" Backend Testing Complete!")
        print(f" Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        print(f"⏱️ Total Duration: {total_duration:.2f}s")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "duration": total_duration,
            "results": self.test_results
        }

def main():
    """Main function to run backend tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backend API Testing Script")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Backend server URL")
    args = parser.parse_args()
    
    tester = BackendTester(args.url)
    results = tester.run_all_tests()
    
    # Save results to file
    results_file = PROJECT_ROOT / "tests" / "backend_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f" Results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results["success_rate"] >= 80 else 1)

if __name__ == "__main__":
    main()
