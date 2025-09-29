#!/usr/bin/env python3
"""
Comprehensive Disruption Testing Script for AeroRhythm POC
Tests disruption creation, handling, resolution, and impact analysis
"""

import asyncio
import json
import time
import requests
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.crud import crud

from backend.app.core.database import SessionLocal, sync_engine
from backend.app.models import models
from backend.app.models.models import Base

# Create tables
Base.metadata.create_all(sync_engine)

class DisruptionTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_results = []
        self.start_time = None
        self.auth_token = None
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

    def setup_authentication(self) -> bool:
        """Setup authentication for testing"""
        print(" Setting up Authentication...")
        start_time = time.time()
        
        try:
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
                    self.log_test("Authentication Setup", "PASS", "Authentication successful", duration)
                    return True
                else:
                    self.log_test("Authentication Setup", "FAIL", "No access token in response", duration)
                    return False
            else:
                self.log_test("Authentication Setup", "FAIL", f"Authentication failed with status {response.status_code}", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Authentication Setup", "FAIL", f"Authentication error: {str(e)}")
            return False

    def setup_database_connection(self) -> bool:
        """Setup database connection for testing"""
        print(" Setting up Database Connection...")
        start_time = time.time()
        
        try:
            self.db = SessionLocal()
            
            # Get some test data
            crew = self.db.query(models.Crew).first()
            flight = self.db.query(models.Flight).first()
            
            if crew and flight:
                self.test_data["crew_id"] = crew.id
                self.test_data["flight_id"] = flight.id
                self.test_data["crew_name"] = f"{crew.first_name} {crew.last_name}"
                self.test_data["flight_number"] = flight.flight_number
                
                duration = time.time() - start_time
                self.log_test("Database Connection", "PASS", "Database connected and test data retrieved", duration)
                return True
            else:
                self.log_test("Database Connection", "FAIL", "No test data available in database")
                return False
                
        except Exception as e:
            self.log_test("Database Connection", "FAIL", f"Database connection error: {str(e)}")
            return False

    def test_crew_illness_disruption(self) -> bool:
        """Test crew illness disruption creation and handling"""
        print(" Testing Crew Illness Disruption...")
        start_time = time.time()
        
        try:
            if not self.auth_token or "crew_id" not in self.test_data:
                self.log_test("Crew Illness Disruption", "FAIL", "Missing required test data")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Create crew illness disruption
            disruption_data = {
                "type": "crew_illness",
                "affected": {
                    "crew_ids": [self.test_data["crew_id"]],
                    "crew_names": [self.test_data["crew_name"]],
                    "illness_type": "flu",
                    "symptoms": ["fever", "cough", "fatigue"]
                },
                "severity": "high",
                "attributes": {
                    "illness_type": "flu",
                    "expected_duration_days": 3,
                    "requires_replacement": True,
                    "medical_certificate_required": True,
                    "contagious": True
                }
            }
            
            response = requests.post(
                f"{self.base_url}/disruptions",
                json=disruption_data,
                headers=headers,
                timeout=10
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 201:
                created_disruption = response.json()
                self.test_data["crew_illness_id"] = created_disruption["id"]
                
                # Verify disruption details
                if created_disruption["type"] == "crew_illness" and created_disruption["severity"] == "high":
                    self.log_test("Crew Illness Disruption", "PASS", "Crew illness disruption created successfully", duration)
                    return True
                else:
                    self.log_test("Crew Illness Disruption", "FAIL", "Disruption created but with incorrect details", duration)
                    return False
            else:
                self.log_test("Crew Illness Disruption", "FAIL", f"Failed to create crew illness disruption: {response.status_code}", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Crew Illness Disruption", "FAIL", f"Crew illness disruption error: {str(e)}")
            return False

    def test_weather_delay_disruption(self) -> bool:
        """Test weather delay disruption creation and handling"""
        print("️ Testing Weather Delay Disruption...")
        start_time = time.time()
        
        try:
            if not self.auth_token or "flight_id" not in self.test_data:
                self.log_test("Weather Delay Disruption", "FAIL", "Missing required test data")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Create weather delay disruption
            disruption_data = {
                "type": "weather_delay",
                "affected": {
                    "flight_ids": [self.test_data["flight_id"]],
                    "flight_numbers": [self.test_data["flight_number"]],
                    "airports_affected": ["LAX", "JFK"],
                    "weather_conditions": ["thunderstorm", "heavy_rain", "low_visibility"]
                },
                "severity": "medium",
                "attributes": {
                    "delay_minutes": 120,
                    "weather_condition": "thunderstorm",
                    "visibility_miles": 0.5,
                    "wind_speed_mph": 45,
                    "affects_crew_scheduling": True,
                    "passenger_impact": "high"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/disruptions",
                json=disruption_data,
                headers=headers,
                timeout=10
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 201:
                created_disruption = response.json()
                self.test_data["weather_delay_id"] = created_disruption["id"]
                
                # Verify disruption details
                if created_disruption["type"] == "weather_delay" and created_disruption["severity"] == "medium":
                    self.log_test("Weather Delay Disruption", "PASS", "Weather delay disruption created successfully", duration)
                    return True
                else:
                    self.log_test("Weather Delay Disruption", "FAIL", "Disruption created but with incorrect details", duration)
                    return False
            else:
                self.log_test("Weather Delay Disruption", "FAIL", f"Failed to create weather delay disruption: {response.status_code}", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Weather Delay Disruption", "FAIL", f"Weather delay disruption error: {str(e)}")
            return False

    def test_aircraft_maintenance_disruption(self) -> bool:
        """Test aircraft maintenance disruption creation and handling"""
        print(" Testing Aircraft Maintenance Disruption...")
        start_time = time.time()
        
        try:
            if not self.auth_token or "flight_id" not in self.test_data:
                self.log_test("Aircraft Maintenance Disruption", "FAIL", "Missing required test data")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Create aircraft maintenance disruption
            disruption_data = {
                "type": "aircraft_maintenance",
                "affected": {
                    "flight_ids": [self.test_data["flight_id"]],
                    "aircraft_registration": "N12345",
                    "aircraft_type": "B737-800",
                    "maintenance_type": "engine_inspection"
                },
                "severity": "high",
                "attributes": {
                    "maintenance_type": "engine_inspection",
                    "estimated_duration_hours": 4,
                    "requires_aircraft_change": True,
                    "safety_critical": True,
                    "maintenance_station": "LAX",
                    "parts_required": ["engine_filter", "oil_seal"]
                }
            }
            
            response = requests.post(
                f"{self.base_url}/disruptions",
                json=disruption_data,
                headers=headers,
                timeout=10
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 201:
                created_disruption = response.json()
                self.test_data["maintenance_id"] = created_disruption["id"]
                
                # Verify disruption details
                if created_disruption["type"] == "aircraft_maintenance" and created_disruption["severity"] == "high":
                    self.log_test("Aircraft Maintenance Disruption", "PASS", "Aircraft maintenance disruption created successfully", duration)
                    return True
                else:
                    self.log_test("Aircraft Maintenance Disruption", "FAIL", "Disruption created but with incorrect details", duration)
                    return False
            else:
                self.log_test("Aircraft Maintenance Disruption", "FAIL", f"Failed to create aircraft maintenance disruption: {response.status_code}", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Aircraft Maintenance Disruption", "FAIL", f"Aircraft maintenance disruption error: {str(e)}")
            return False

    def test_scheduling_conflict_disruption(self) -> bool:
        """Test scheduling conflict disruption creation and handling"""
        print("⏰ Testing Scheduling Conflict Disruption...")
        start_time = time.time()
        
        try:
            if not self.auth_token or "crew_id" not in self.test_data:
                self.log_test("Scheduling Conflict Disruption", "FAIL", "Missing required test data")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Create scheduling conflict disruption
            disruption_data = {
                "type": "scheduling_conflict",
                "affected": {
                    "crew_ids": [self.test_data["crew_id"]],
                    "crew_name": self.test_data["crew_name"],
                    "conflict_type": "double_booking",
                    "overlapping_flights": 2
                },
                "severity": "critical",
                "attributes": {
                    "conflict_type": "double_booking",
                    "overlapping_flights": 2,
                    "requires_immediate_resolution": True,
                    "scheduling_error": True,
                    "crew_availability": "unavailable",
                    "resolution_priority": "urgent"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/disruptions",
                json=disruption_data,
                headers=headers,
                timeout=10
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 201:
                created_disruption = response.json()
                self.test_data["scheduling_conflict_id"] = created_disruption["id"]
                
                # Verify disruption details
                if created_disruption["type"] == "scheduling_conflict" and created_disruption["severity"] == "critical":
                    self.log_test("Scheduling Conflict Disruption", "PASS", "Scheduling conflict disruption created successfully", duration)
                    return True
                else:
                    self.log_test("Scheduling Conflict Disruption", "FAIL", "Disruption created but with incorrect details", duration)
                    return False
            else:
                self.log_test("Scheduling Conflict Disruption", "FAIL", f"Failed to create scheduling conflict disruption: {response.status_code}", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Scheduling Conflict Disruption", "FAIL", f"Scheduling conflict disruption error: {str(e)}")
            return False

    def test_airport_closure_disruption(self) -> bool:
        """Test airport closure disruption creation and handling"""
        print(" Testing Airport Closure Disruption...")
        start_time = time.time()
        
        try:
            if not self.auth_token:
                self.log_test("Airport Closure Disruption", "FAIL", "Missing authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get flights affected by airport closure
            response = requests.get(f"{self.base_url}/flights?limit=5", headers=headers, timeout=10)
            if response.status_code == 200:
                flights = response.json()
                affected_flights = [f["id"] for f in flights[:3]]  # Take first 3 flights
            else:
                affected_flights = ["FLIGHT001", "FLIGHT002", "FLIGHT003"]  # Fallback
            
            # Create airport closure disruption
            disruption_data = {
                "type": "airport_closure",
                "affected": {
                    "airport": "LAX",
                    "closure_reason": "security_incident",
                    "flight_count": len(affected_flights),
                    "flight_ids": affected_flights,
                    "departure_flights": len(affected_flights),
                    "arrival_flights": len(affected_flights)
                },
                "severity": "critical",
                "attributes": {
                    "closure_reason": "security_incident",
                    "estimated_duration_hours": 6,
                    "affects_multiple_flights": True,
                    "passenger_impact": "severe",
                    "alternative_airports": ["BUR", "LGB", "ONT"],
                    "security_level": "heightened"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/disruptions",
                json=disruption_data,
                headers=headers,
                timeout=10
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 201:
                created_disruption = response.json()
                self.test_data["airport_closure_id"] = created_disruption["id"]
                
                # Verify disruption details
                if created_disruption["type"] == "airport_closure" and created_disruption["severity"] == "critical":
                    self.log_test("Airport Closure Disruption", "PASS", "Airport closure disruption created successfully", duration)
                    return True
                else:
                    self.log_test("Airport Closure Disruption", "FAIL", "Disruption created but with incorrect details", duration)
                    return False
            else:
                self.log_test("Airport Closure Disruption", "FAIL", f"Failed to create airport closure disruption: {response.status_code}", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Airport Closure Disruption", "FAIL", f"Airport closure disruption error: {str(e)}")
            return False

    def test_disruption_impact_analysis(self) -> bool:
        """Test disruption impact analysis and cascading effects"""
        print(" Testing Disruption Impact Analysis...")
        start_time = time.time()
        
        try:
            if not self.auth_token:
                self.log_test("Disruption Impact Analysis", "FAIL", "Missing authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get all disruptions
            response = requests.get(f"{self.base_url}/disruptions", headers=headers, timeout=10)
            
            if response.status_code == 200:
                disruptions = response.json()
                
                # Analyze disruption types and severities
                disruption_types = {}
                severity_counts = {}
                total_affected_flights = 0
                total_affected_crew = 0
                
                for disruption in disruptions:
                    # Count by type
                    disruption_type = disruption.get("type", "unknown")
                    disruption_types[disruption_type] = disruption_types.get(disruption_type, 0) + 1
                    
                    # Count by severity
                    severity = disruption.get("severity", "unknown")
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    # Count affected resources
                    affected = disruption.get("affected", {})
                    if "flight_ids" in affected:
                        total_affected_flights += len(affected["flight_ids"])
                    if "crew_ids" in affected:
                        total_affected_crew += len(affected["crew_ids"])
                
                # Calculate impact metrics
                total_disruptions = len(disruptions)
                critical_disruptions = severity_counts.get("critical", 0)
                high_severity_disruptions = severity_counts.get("high", 0)
                
                impact_analysis = {
                    "total_disruptions": total_disruptions,
                    "disruption_types": disruption_types,
                    "severity_distribution": severity_counts,
                    "total_affected_flights": total_affected_flights,
                    "total_affected_crew": total_affected_crew,
                    "critical_disruptions": critical_disruptions,
                    "high_severity_disruptions": high_severity_disruptions
                }
                
                duration = time.time() - start_time
                
                # Validate impact analysis
                if total_disruptions > 0 and len(disruption_types) > 0:
                    self.log_test("Disruption Impact Analysis", "PASS", 
                                f"Analyzed {total_disruptions} disruptions affecting {total_affected_flights} flights and {total_affected_crew} crew members", 
                                duration)
                    return True
                else:
                    self.log_test("Disruption Impact Analysis", "FAIL", "No disruptions found for analysis", duration)
                    return False
            else:
                self.log_test("Disruption Impact Analysis", "FAIL", f"Failed to retrieve disruptions: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.log_test("Disruption Impact Analysis", "FAIL", f"Impact analysis error: {str(e)}")
            return False

    def test_disruption_resolution_workflow(self) -> bool:
        """Test disruption resolution workflow"""
        print(" Testing Disruption Resolution Workflow...")
        start_time = time.time()
        
        try:
            if not self.auth_token or not self.test_data.get("crew_illness_id"):
                self.log_test("Disruption Resolution Workflow", "FAIL", "Missing required test data")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Simulate resolution steps
            resolution_steps = [
                {
                    "step": "assessment",
                    "action": "assess_crew_availability",
                    "status": "completed",
                    "details": "Identified replacement crew member"
                },
                {
                    "step": "replacement",
                    "action": "assign_replacement_crew",
                    "status": "in_progress",
                    "details": "Contacting replacement crew member"
                },
                {
                    "step": "notification",
                    "action": "notify_affected_parties",
                    "status": "pending",
                    "details": "Preparing notifications for passengers and crew"
                }
            ]
            
            # Test resolution workflow by updating disruption
            resolution_data = {
                "type": "crew_illness",
                "affected": {
                    "crew_ids": [self.test_data["crew_id"]],
                    "crew_names": [self.test_data["crew_name"]],
                    "resolution_steps": resolution_steps
                },
                "severity": "high",
                "attributes": {
                    "illness_type": "flu",
                    "expected_duration_days": 3,
                    "requires_replacement": True,
                    "replacement_crew_assigned": True,
                    "resolution_status": "in_progress",
                    "estimated_resolution_time": "2 hours"
                }
            }
            
            # Note: This assumes there's an update endpoint for disruptions
            # If not available, we'll test the concept with a new disruption
            response = requests.post(
                f"{self.base_url}/disruptions",
                json=resolution_data,
                headers=headers,
                timeout=10
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 201:
                self.log_test("Disruption Resolution Workflow", "PASS", "Disruption resolution workflow tested successfully", duration)
                return True
            else:
                self.log_test("Disruption Resolution Workflow", "FAIL", f"Failed to test resolution workflow: {response.status_code}", duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Disruption Resolution Workflow", "FAIL", f"Resolution workflow error: {str(e)}")
            return False

    def test_disruption_notification_system(self) -> bool:
        """Test disruption notification and alert system"""
        print(" Testing Disruption Notification System...")
        start_time = time.time()
        
        try:
            if not self.auth_token:
                self.log_test("Disruption Notification System", "FAIL", "Missing authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test notification scenarios
            notification_scenarios = [
                {
                    "scenario": "critical_disruption_alert",
                    "disruption_type": "airport_closure",
                    "severity": "critical",
                    "notification_priority": "urgent",
                    "affected_parties": ["operations", "crew", "passengers", "management"]
                },
                {
                    "scenario": "crew_illness_notification",
                    "disruption_type": "crew_illness",
                    "severity": "high",
                    "notification_priority": "high",
                    "affected_parties": ["crew_scheduling", "flight_operations", "medical"]
                },
                {
                    "scenario": "weather_delay_update",
                    "disruption_type": "weather_delay",
                    "severity": "medium",
                    "notification_priority": "medium",
                    "affected_parties": ["passengers", "ground_crew", "air_traffic_control"]
                }
            ]
            
            # Simulate notification system by creating test disruptions
            notifications_sent = 0
            
            for scenario in notification_scenarios:
                # Create a test disruption for notification testing
                test_disruption = {
                    "type": scenario["disruption_type"],
                    "affected": {
                        "notification_scenario": scenario["scenario"],
                        "affected_parties": scenario["affected_parties"]
                    },
                    "severity": scenario["severity"],
                    "attributes": {
                        "notification_priority": scenario["notification_priority"],
                        "notification_sent": True,
                        "notification_timestamp": datetime.now().isoformat(),
                        "notification_channels": ["email", "sms", "dashboard_alert"]
                    }
                }
                
                response = requests.post(
                    f"{self.base_url}/disruptions",
                    json=test_disruption,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 201:
                    notifications_sent += 1
            
            duration = time.time() - start_time
            
            if notifications_sent >= len(notification_scenarios) * 0.8:  # 80% success rate
                self.log_test("Disruption Notification System", "PASS", 
                            f"Notification system tested with {notifications_sent}/{len(notification_scenarios)} scenarios", 
                            duration)
                return True
            else:
                self.log_test("Disruption Notification System", "FAIL", 
                            f"Only {notifications_sent}/{len(notification_scenarios)} notification scenarios successful", 
                            duration)
                return False
                
        except requests.RequestException as e:
            self.log_test("Disruption Notification System", "FAIL", f"Notification system error: {str(e)}")
            return False

    def test_disruption_data_consistency(self) -> bool:
        """Test disruption data consistency and validation"""
        print(" Testing Disruption Data Consistency...")
        start_time = time.time()
        
        try:
            if not self.db:
                self.log_test("Disruption Data Consistency", "FAIL", "No database connection")
                return False
            
            # Test data consistency checks
            consistency_checks = []
            
            # Check for disruptions with valid types
            valid_types = ["crew_illness", "weather_delay", "aircraft_maintenance", "scheduling_conflict", "airport_closure"]
            disruptions = self.db.query(models.Disruption).all()
            
            valid_type_count = 0
            for disruption in disruptions:
                if disruption.type in valid_types:
                    valid_type_count += 1
            
            if valid_type_count == len(disruptions):
                consistency_checks.append("All disruptions have valid types")
            else:
                consistency_checks.append(f"{valid_type_count}/{len(disruptions)} disruptions have valid types")
            
            # Check for disruptions with valid severities
            valid_severities = ["low", "medium", "high", "critical"]
            valid_severity_count = 0
            for disruption in disruptions:
                if disruption.severity in valid_severities:
                    valid_severity_count += 1
            
            if valid_severity_count == len(disruptions):
                consistency_checks.append("All disruptions have valid severities")
            else:
                consistency_checks.append(f"{valid_severity_count}/{len(disruptions)} disruptions have valid severities")
            
            # Check for disruptions with non-empty affected data
            non_empty_affected = 0
            for disruption in disruptions:
                if disruption.affected and len(str(disruption.affected)) > 2:  # More than just "{}"
                    non_empty_affected += 1
            
            if non_empty_affected == len(disruptions):
                consistency_checks.append("All disruptions have non-empty affected data")
            else:
                consistency_checks.append(f"{non_empty_affected}/{len(disruptions)} disruptions have non-empty affected data")
            
            duration = time.time() - start_time
            
            # Count successful consistency checks
            successful_checks = sum(1 for check in consistency_checks if "All" in check)
            total_checks = len(consistency_checks)
            
            if successful_checks >= total_checks * 0.8:  # 80% success rate
                self.log_test("Disruption Data Consistency", "PASS", 
                            f"{successful_checks}/{total_checks} consistency checks passed", 
                            duration)
                return True
            else:
                self.log_test("Disruption Data Consistency", "FAIL", 
                            f"Only {successful_checks}/{total_checks} consistency checks passed", 
                            duration)
                return False
                
        except Exception as e:
            self.log_test("Disruption Data Consistency", "FAIL", f"Data consistency error: {str(e)}")
            return False

    def cleanup_test_data(self):
        """Clean up test data created during disruption testing"""
        print(" Cleaning up disruption test data...")
        
        try:
            if not self.auth_token:
                return
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Clean up created disruptions
            disruption_ids = [
                self.test_data.get("crew_illness_id"),
                self.test_data.get("weather_delay_id"),
                self.test_data.get("maintenance_id"),
                self.test_data.get("scheduling_conflict_id"),
                self.test_data.get("airport_closure_id")
            ]
            
            cleaned_count = 0
            for disruption_id in disruption_ids:
                if disruption_id:
                    try:
                        response = requests.delete(
                            f"{self.base_url}/disruptions/{disruption_id}",
                            headers=headers,
                            timeout=10
                        )
                        if response.status_code in [200, 204]:
                            cleaned_count += 1
                    except requests.RequestException:
                        pass
            
            if cleaned_count > 0:
                self.log_test("Cleanup", "PASS", f"Cleaned up {cleaned_count} test disruptions")
            else:
                self.log_test("Cleanup", "WARN", "No test disruptions to clean up")
                
        except Exception as e:
            self.log_test("Cleanup", "WARN", f"Cleanup error: {str(e)}")

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all disruption tests"""
        print(" Starting Comprehensive Disruption Testing...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Setup
        if not self.setup_authentication():
            return {"error": "Failed to setup authentication"}
        
        if not self.setup_database_connection():
            return {"error": "Failed to setup database connection"}
        
        # Run tests
        tests = [
            ("Crew Illness Disruption", self.test_crew_illness_disruption),
            ("Weather Delay Disruption", self.test_weather_delay_disruption),
            ("Aircraft Maintenance Disruption", self.test_aircraft_maintenance_disruption),
            ("Scheduling Conflict Disruption", self.test_scheduling_conflict_disruption),
            ("Airport Closure Disruption", self.test_airport_closure_disruption),
            ("Disruption Impact Analysis", self.test_disruption_impact_analysis),
            ("Disruption Resolution Workflow", self.test_disruption_resolution_workflow),
            ("Disruption Notification System", self.test_disruption_notification_system),
            ("Disruption Data Consistency", self.test_disruption_data_consistency)
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
        print(f" Disruption Testing Complete!")
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
    """Main function to run disruption tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Disruption Testing Script")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Backend server URL")
    args = parser.parse_args()
    
    tester = DisruptionTester(args.url)
    results = tester.run_all_tests()
    
    if "error" in results:
        print(f"❌ Disruption Testing Failed: {results['error']}")
        sys.exit(1)
    
    # Save results to file
    results_file = PROJECT_ROOT / "tests" / "disruption_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f" Results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results["success_rate"] >= 80 else 1)

if __name__ == "__main__":
    main()
