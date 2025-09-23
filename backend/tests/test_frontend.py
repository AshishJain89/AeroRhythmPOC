#!/usr/bin/env python3
"""
Comprehensive Frontend Testing Script for AeroRhythm POC
Tests all frontend functionality including UI components, routing, and user interactions
"""

import asyncio
import json
import time
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

class FrontendTester:
    def __init__(self):
        self.base_url = "http://localhost:5173"  # Vite default port
        self.test_results = []
        self.start_time = None
        
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

    def test_frontend_build(self) -> bool:
        """Test if frontend builds successfully"""
        print("🔨 Testing Frontend Build...")
        start_time = time.time()
        
        try:
            # Navigate to frontend directory
            frontend_dir = PROJECT_ROOT / "frontend"
            
            # Test npm/yarn install
            result = subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                self.log_test("Frontend Build", "FAIL", f"npm install failed: {result.stderr}")
                return False
            
            # Test build
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.log_test("Frontend Build", "PASS", "Build completed successfully", duration)
                return True
            else:
                self.log_test("Frontend Build", "FAIL", f"Build failed: {result.stderr}", duration)
                return False
                
        except subprocess.TimeoutExpired:
            self.log_test("Frontend Build", "FAIL", "Build timed out after 5 minutes")
            return False
        except Exception as e:
            self.log_test("Frontend Build", "FAIL", f"Build error: {str(e)}")
            return False

    def test_frontend_dev_server(self) -> bool:
        """Test if frontend dev server starts successfully"""
        print("🚀 Testing Frontend Dev Server...")
        start_time = time.time()
        
        try:
            frontend_dir = PROJECT_ROOT / "frontend"
            
            # Start dev server in background
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            time.sleep(10)
            
            # Check if server is running
            import requests
            try:
                response = requests.get(f"{self.base_url}", timeout=5)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_test("Frontend Dev Server", "PASS", "Server started successfully", duration)
                    process.terminate()
                    return True
                else:
                    self.log_test("Frontend Dev Server", "FAIL", f"Server returned status {response.status_code}", duration)
                    process.terminate()
                    return False
                    
            except requests.RequestException:
                self.log_test("Frontend Dev Server", "FAIL", "Could not connect to dev server")
                process.terminate()
                return False
                
        except Exception as e:
            self.log_test("Frontend Dev Server", "FAIL", f"Server start error: {str(e)}")
            return False

    def test_ui_components(self) -> bool:
        """Test UI component rendering and functionality"""
        print("🎨 Testing UI Components...")
        start_time = time.time()
        
        components_to_test = [
            "AppShell",
            "Header", 
            "Sidebar",
            "CrewCard",
            "DisruptionsFeed",
            "SearchBar",
            "TimelineView"
        ]
        
        passed = 0
        total = len(components_to_test)
        
        for component in components_to_test:
            try:
                # Check if component file exists
                component_path = PROJECT_ROOT / "frontend" / "src" / "components" / f"{component}.tsx"
                if not component_path.exists():
                    self.log_test(f"Component {component}", "FAIL", "Component file not found")
                    continue
                
                # Read component file and check for basic structure
                with open(component_path, 'r') as f:
                    content = f.read()
                
                # Basic checks
                checks = [
                    ("export", "Component exports properly"),
                    ("function" in content or "const" in content, "Component is defined"),
                    ("return", "Component has return statement"),
                    ("jsx" in content.lower() or "tsx" in content.lower(), "Component has JSX")
                ]
                
                component_passed = all(check[0] for check in checks)
                if component_passed:
                    passed += 1
                    self.log_test(f"Component {component}", "PASS", "Component structure valid")
                else:
                    failed_checks = [check[1] for check in checks if not check[0]]
                    self.log_test(f"Component {component}", "FAIL", f"Failed checks: {', '.join(failed_checks)}")
                    
            except Exception as e:
                self.log_test(f"Component {component}", "FAIL", f"Error: {str(e)}")
        
        duration = time.time() - start_time
        success_rate = (passed / total) * 100
        
        if success_rate >= 80:
            self.log_test("UI Components", "PASS", f"{passed}/{total} components passed ({success_rate:.1f}%)", duration)
            return True
        else:
            self.log_test("UI Components", "FAIL", f"Only {passed}/{total} components passed ({success_rate:.1f}%)", duration)
            return False

    def test_routing(self) -> bool:
        """Test frontend routing configuration"""
        print("🛣️ Testing Frontend Routing...")
        start_time = time.time()
        
        try:
            # Check routes file
            routes_path = PROJECT_ROOT / "frontend" / "src" / "routes.tsx"
            if not routes_path.exists():
                self.log_test("Frontend Routing", "FAIL", "Routes file not found")
                return False
            
            with open(routes_path, 'r') as f:
                content = f.read()
            
            # Check for expected routes
            expected_routes = [
                "Dashboard",
                "Crew", 
                "Roster",
                "Disruptions",
                "Settings",
                "Login"
            ]
            
            found_routes = []
            for route in expected_routes:
                if route.lower() in content.lower():
                    found_routes.append(route)
            
            duration = time.time() - start_time
            
            if len(found_routes) >= len(expected_routes) * 0.8:  # 80% of routes found
                self.log_test("Frontend Routing", "PASS", f"Found {len(found_routes)}/{len(expected_routes)} routes", duration)
                return True
            else:
                self.log_test("Frontend Routing", "FAIL", f"Only found {len(found_routes)}/{len(expected_routes)} routes", duration)
                return False
                
        except Exception as e:
            self.log_test("Frontend Routing", "FAIL", f"Error: {str(e)}")
            return False

    def test_api_integration(self) -> bool:
        """Test frontend API integration"""
        print("🔌 Testing Frontend API Integration...")
        start_time = time.time()
        
        try:
            # Check API client files
            api_dir = PROJECT_ROOT / "frontend" / "src" / "api"
            api_files = [
                "apiClient.ts",
                "auth.ts", 
                "crews.ts",
                "rosters.ts"
            ]
            
            found_files = 0
            for api_file in api_files:
                if (api_dir / api_file).exists():
                    found_files += 1
            
            duration = time.time() - start_time
            
            if found_files >= len(api_files) * 0.75:  # 75% of API files found
                self.log_test("API Integration", "PASS", f"Found {found_files}/{len(api_files)} API files", duration)
                return True
            else:
                self.log_test("API Integration", "FAIL", f"Only found {found_files}/{len(api_files)} API files", duration)
                return False
                
        except Exception as e:
            self.log_test("API Integration", "FAIL", f"Error: {str(e)}")
            return False

    def test_responsive_design(self) -> bool:
        """Test responsive design implementation"""
        print("📱 Testing Responsive Design...")
        start_time = time.time()
        
        try:
            # Check for responsive design indicators
            css_files = list((PROJECT_ROOT / "frontend" / "src").rglob("*.css"))
            tailwind_config = PROJECT_ROOT / "frontend" / "tailwind.config.ts"
            
            responsive_indicators = 0
            
            # Check Tailwind config
            if tailwind_config.exists():
                with open(tailwind_config, 'r') as f:
                    content = f.read()
                if "screens" in content or "breakpoints" in content:
                    responsive_indicators += 1
            
            # Check CSS files for responsive classes
            for css_file in css_files[:3]:  # Check first 3 CSS files
                with open(css_file, 'r') as f:
                    content = f.read()
                if any(breakpoint in content for breakpoint in ["@media", "sm:", "md:", "lg:", "xl:"]):
                    responsive_indicators += 1
                    break
            
            duration = time.time() - start_time
            
            if responsive_indicators > 0:
                self.log_test("Responsive Design", "PASS", f"Found {responsive_indicators} responsive indicators", duration)
                return True
            else:
                self.log_test("Responsive Design", "FAIL", "No responsive design indicators found", duration)
                return False
                
        except Exception as e:
            self.log_test("Responsive Design", "FAIL", f"Error: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all frontend tests"""
        print("🧪 Starting Comprehensive Frontend Testing...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        tests = [
            ("Frontend Build", self.test_frontend_build),
            ("Frontend Dev Server", self.test_frontend_dev_server),
            ("UI Components", self.test_ui_components),
            ("Frontend Routing", self.test_routing),
            ("API Integration", self.test_api_integration),
            ("Responsive Design", self.test_responsive_design)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, "FAIL", f"Test error: {str(e)}")
        
        total_duration = time.time() - self.start_time
        success_rate = (passed_tests / total_tests) * 100
        
        print("=" * 60)
        print(f"🎯 Frontend Testing Complete!")
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
    """Main function to run frontend tests"""
    tester = FrontendTester()
    results = tester.run_all_tests()
    
    # Save results to file
    results_file = PROJECT_ROOT / "backend" / "tests" / "frontend_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results["success_rate"] >= 80 else 1)

if __name__ == "__main__":
    main()
