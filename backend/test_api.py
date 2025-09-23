#!/usr/bin/env python3
"""
Comprehensive API testing script for AeroRhythm backend
"""
import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8005"

def test_endpoint(method, endpoint, data=None, expected_status=200, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    if description:
        print(f"Description: {description}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"✅ PASS - Expected {expected_status}")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    json_data = response.json()
                    print(f"Response: {json.dumps(json_data, indent=2)[:200]}...")
                except:
                    print(f"Response: {response.text[:200]}...")
            else:
                print(f"Response: {response.text[:200]}...")
            return True
        else:
            print(f"❌ FAIL - Expected {expected_status}, got {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Server not running on {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT - Request timed out")
        return False
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return False

def main():
    print("🚀 Starting Comprehensive API Tests for AeroRhythm Backend")
    print(f"Base URL: {BASE_URL}")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    tests_total += 1
    if test_endpoint("GET", "/health", expected_status=200, description="Basic health check"):
        tests_passed += 1
    
    # Test 2: API Documentation
    tests_total += 1
    if test_endpoint("GET", "/docs", expected_status=200, description="OpenAPI documentation"):
        tests_passed += 1
    
    # Test 3: OpenAPI JSON
    tests_total += 1
    if test_endpoint("GET", "/openapi.json", expected_status=200, description="OpenAPI schema"):
        tests_passed += 1
    
    # Test 4: Get Crews
    tests_total += 1
    if test_endpoint("GET", "/crews", expected_status=200, description="List all crews"):
        tests_passed += 1
    
    # Test 5: Get Crews with pagination
    tests_total += 1
    if test_endpoint("GET", "/crews?skip=0&limit=10", expected_status=200, description="List crews with pagination"):
        tests_passed += 1
    
    # Test 6: Get Flights
    tests_total += 1
    if test_endpoint("GET", "/flights", expected_status=200, description="List all flights"):
        tests_passed += 1
    
    # Test 7: Get Flights with pagination
    tests_total += 1
    if test_endpoint("GET", "/flights?skip=0&limit=10", expected_status=200, description="List flights with pagination"):
        tests_passed += 1
    
    # Test 8: Get Roster Assignments
    tests_total += 1
    if test_endpoint("GET", "/rosters", expected_status=200, description="List all roster assignments"):
        tests_passed += 1
    
    # Test 9: Get Disruptions
    tests_total += 1
    if test_endpoint("GET", "/disruptions", expected_status=200, description="List all disruptions"):
        tests_passed += 1
    
    # Test 10: Get Jobs
    tests_total += 1
    if test_endpoint("GET", "/jobs", expected_status=200, description="List all jobs"):
        tests_passed += 1
    
    # Test 11: Create a new crew member
    tests_total += 1
    crew_data = {
        "name": "Test Pilot",
        "role": "CPT",
        "base": "LAX",
        "qualifications": ["B737", "A320"],
        "seniority": 5,
        "metadata": {"test": True}
    }
    if test_endpoint("POST", "/crews", data=crew_data, expected_status=200, description="Create new crew member"):
        tests_passed += 1
    
    # Test 12: Create a new flight
    tests_total += 1
    flight_data = {
        "id": "TEST001",
        "flight_number": "AA100",
        "origin": "LAX",
        "destination": "JFK",
        "departure": (datetime.now() + timedelta(hours=1)).isoformat(),
        "arrival": (datetime.now() + timedelta(hours=6)).isoformat(),
        "aircraft": "B737",
        "metadata": {"test": True}
    }
    if test_endpoint("POST", "/flights", data=flight_data, expected_status=200, description="Create new flight"):
        tests_passed += 1
    
    # Test 13: Create a roster assignment
    tests_total += 1
    roster_data = {
        "crew_id": 1,
        "flight_id": "TEST001",
        "start": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end": (datetime.now() + timedelta(hours=6)).isoformat(),
        "position": "CPT",
        "metadata": {"test": True}
    }
    if test_endpoint("POST", "/rosters", data=roster_data, expected_status=200, description="Create roster assignment"):
        tests_passed += 1
    
    # Test 14: Create a disruption
    tests_total += 1
    disruption_data = {
        "type": "delay",
        "affected": {"flights": ["TEST001"], "crews": [1]},
        "severity": "medium",
        "metadata": {"test": True}
    }
    if test_endpoint("POST", "/disruptions", data=disruption_data, expected_status=200, description="Create disruption"):
        tests_passed += 1
    
    # Test 15: Test error handling - invalid crew ID
    tests_total += 1
    if test_endpoint("GET", "/crews/99999", expected_status=404, description="Get non-existent crew (should return 404)"):
        tests_passed += 1
    
    # Test 16: Test error handling - invalid flight ID
    tests_total += 1
    if test_endpoint("GET", "/flights/INVALID", expected_status=404, description="Get non-existent flight (should return 404)"):
        tests_passed += 1
    
    # Test 17: Test validation - create crew with missing required fields
    tests_total += 1
    invalid_crew_data = {
        "role": "CPT"  # Missing required 'name' field
    }
    if test_endpoint("POST", "/crews", data=invalid_crew_data, expected_status=422, description="Create crew with missing required fields (should return 422)"):
        tests_passed += 1
    
    # Test 18: Test validation - create flight with invalid data
    tests_total += 1
    invalid_flight_data = {
        "id": "TEST002",
        "flight_number": "AA200",
        "origin": "LAX",
        "destination": "JFK",
        "departure": "invalid-date",  # Invalid date format
        "arrival": (datetime.now() + timedelta(hours=6)).isoformat(),
        "aircraft": "B737"
    }
    if test_endpoint("POST", "/flights", data=invalid_flight_data, expected_status=422, description="Create flight with invalid date (should return 422)"):
        tests_passed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🏁 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("🎉 ALL TESTS PASSED! Backend is working correctly.")
        return 0
    else:
        print(f"⚠️  {tests_total - tests_passed} tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
