#!/usr/bin/env python3
"""
Master Test Runner for AeroRhythm POC
Executes all test suites and generates comprehensive reports
"""

import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

class MasterTestRunner:
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.total_duration = 0
        
    def log_test_suite(self, suite_name: str, status: str, details: str = "", duration: float = 0):
        """Log test suite results"""
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {suite_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if duration > 0:
            print(f"   Duration: {duration:.2f}s")
        print()

    def run_frontend_tests(self) -> Dict[str, Any]:
        """Run frontend tests"""
        print("🎨 Running Frontend Tests...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, "test_frontend.py"],
                cwd=PROJECT_ROOT / "backend" / "tests",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.log_test_suite("Frontend Tests", "PASS", "All frontend tests passed", duration)
                return {"status": "PASS", "duration": duration, "output": result.stdout}
            else:
                self.log_test_suite("Frontend Tests", "FAIL", f"Frontend tests failed: {result.stderr}", duration)
                return {"status": "FAIL", "duration": duration, "output": result.stdout, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            self.log_test_suite("Frontend Tests", "FAIL", "Frontend tests timed out after 5 minutes")
            return {"status": "FAIL", "duration": 300, "error": "Timeout"}
        except Exception as e:
            self.log_test_suite("Frontend Tests", "FAIL", f"Frontend test error: {str(e)}")
            return {"status": "FAIL", "duration": 0, "error": str(e)}

    def run_backend_tests(self) -> Dict[str, Any]:
        """Run backend tests"""
        print("🔧 Running Backend Tests...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, "test_backend.py"],
                cwd=PROJECT_ROOT / "backend" / "tests",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.log_test_suite("Backend Tests", "PASS", "All backend tests passed", duration)
                return {"status": "PASS", "duration": duration, "output": result.stdout}
            else:
                self.log_test_suite("Backend Tests", "FAIL", f"Backend tests failed: {result.stderr}", duration)
                return {"status": "FAIL", "duration": duration, "output": result.stdout, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            self.log_test_suite("Backend Tests", "FAIL", "Backend tests timed out after 5 minutes")
            return {"status": "FAIL", "duration": 300, "error": "Timeout"}
        except Exception as e:
            self.log_test_suite("Backend Tests", "FAIL", f"Backend test error: {str(e)}")
            return {"status": "FAIL", "duration": 0, "error": str(e)}

    def run_database_tests(self) -> Dict[str, Any]:
        """Run database tests"""
        print("🗄️ Running Database Tests...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, "test_database.py"],
                cwd=PROJECT_ROOT / "backend" / "tests",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.log_test_suite("Database Tests", "PASS", "All database tests passed", duration)
                return {"status": "PASS", "duration": duration, "output": result.stdout}
            else:
                self.log_test_suite("Database Tests", "FAIL", f"Database tests failed: {result.stderr}", duration)
                return {"status": "FAIL", "duration": duration, "output": result.stdout, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            self.log_test_suite("Database Tests", "FAIL", "Database tests timed out after 5 minutes")
            return {"status": "FAIL", "duration": 300, "error": "Timeout"}
        except Exception as e:
            self.log_test_suite("Database Tests", "FAIL", f"Database test error: {str(e)}")
            return {"status": "FAIL", "duration": 0, "error": str(e)}

    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests"""
        print("🔄 Running End-to-End Tests...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, "test_e2e.py"],
                cwd=PROJECT_ROOT / "backend" / "tests",
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for E2E tests
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.log_test_suite("End-to-End Tests", "PASS", "All E2E tests passed", duration)
                return {"status": "PASS", "duration": duration, "output": result.stdout}
            else:
                self.log_test_suite("End-to-End Tests", "FAIL", f"E2E tests failed: {result.stderr}", duration)
                return {"status": "FAIL", "duration": duration, "output": result.stdout, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            self.log_test_suite("End-to-End Tests", "FAIL", "E2E tests timed out after 10 minutes")
            return {"status": "FAIL", "duration": 600, "error": "Timeout"}
        except Exception as e:
            self.log_test_suite("End-to-End Tests", "FAIL", f"E2E test error: {str(e)}")
            return {"status": "FAIL", "duration": 0, "error": str(e)}

    def run_disruption_tests(self) -> Dict[str, Any]:
        """Run disruption tests"""
        print("⚠️ Running Disruption Tests...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, "test_disruptions.py"],
                cwd=PROJECT_ROOT / "backend" / "tests",
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.log_test_suite("Disruption Tests", "PASS", "All disruption tests passed", duration)
                return {"status": "PASS", "duration": duration, "output": result.stdout}
            else:
                self.log_test_suite("Disruption Tests", "FAIL", f"Disruption tests failed: {result.stderr}", duration)
                return {"status": "FAIL", "duration": duration, "output": result.stdout, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            self.log_test_suite("Disruption Tests", "FAIL", "Disruption tests timed out after 5 minutes")
            return {"status": "FAIL", "duration": 300, "error": "Timeout"}
        except Exception as e:
            self.log_test_suite("Disruption Tests", "FAIL", f"Disruption test error: {str(e)}")
            return {"status": "FAIL", "duration": 0, "error": str(e)}

    def run_ai_stress_tests(self) -> Dict[str, Any]:
        """Run AI and stress tests"""
        print("🤖 Running AI and Stress Tests...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, "test_ai_stress.py"],
                cwd=PROJECT_ROOT / "backend" / "tests",
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for stress tests
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.log_test_suite("AI and Stress Tests", "PASS", "All AI and stress tests passed", duration)
                return {"status": "PASS", "duration": duration, "output": result.stdout}
            else:
                self.log_test_suite("AI and Stress Tests", "FAIL", f"AI and stress tests failed: {result.stderr}", duration)
                return {"status": "FAIL", "duration": duration, "output": result.stdout, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            self.log_test_suite("AI and Stress Tests", "FAIL", "AI and stress tests timed out after 10 minutes")
            return {"status": "FAIL", "duration": 600, "error": "Timeout"}
        except Exception as e:
            self.log_test_suite("AI and Stress Tests", "FAIL", f"AI and stress test error: {str(e)}")
            return {"status": "FAIL", "duration": 0, "error": str(e)}

    def load_individual_test_results(self) -> Dict[str, Any]:
        """Load results from individual test result files"""
        results = {}
        
        test_files = [
            "frontend_test_results.json",
            "backend_test_results.json", 
            "database_test_results.json",
            "e2e_test_results.json",
            "disruption_test_results.json",
            "ai_stress_test_results.json"
        ]
        
        for test_file in test_files:
            file_path = PROJECT_ROOT / "backend" / "tests" / test_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        results[test_file.replace("_test_results.json", "")] = json.load(f)
                except Exception as e:
                    print(f"⚠️ Could not load {test_file}: {str(e)}")
        
        return results

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("📊 Generating Comprehensive Test Report...")
        
        # Load individual test results
        individual_results = self.load_individual_test_results()
        
        # Calculate overall statistics
        total_tests = 0
        total_passed = 0
        total_duration = 0
        
        for suite_name, suite_results in self.test_results.items():
            if suite_results["status"] == "PASS":
                total_passed += 1
            total_duration += suite_results.get("duration", 0)
        
        # Calculate success rate
        success_rate = (total_passed / len(self.test_results)) * 100 if self.test_results else 0
        
        # Generate report
        report = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "total_duration": self.total_duration,
                "test_suites_run": len(self.test_results),
                "test_suites_passed": total_passed,
                "overall_success_rate": success_rate
            },
            "test_suite_results": self.test_results,
            "individual_test_results": individual_results,
            "summary": {
                "overall_status": "PASS" if success_rate >= 80 else "FAIL",
                "recommendations": [],
                "next_steps": []
            }
        }
        
        # Add recommendations based on results
        if success_rate < 80:
            report["summary"]["recommendations"].append("Overall test success rate is below 80% - review failed tests")
        
        failed_suites = [name for name, result in self.test_results.items() if result["status"] == "FAIL"]
        if failed_suites:
            report["summary"]["recommendations"].append(f"Failed test suites: {', '.join(failed_suites)}")
        
        if "frontend" in failed_suites:
            report["summary"]["recommendations"].append("Frontend issues detected - check UI components and build process")
        
        if "backend" in failed_suites:
            report["summary"]["recommendations"].append("Backend issues detected - check API endpoints and server configuration")
        
        if "database" in failed_suites:
            report["summary"]["recommendations"].append("Database issues detected - check schema and data integrity")
        
        if "e2e" in failed_suites:
            report["summary"]["recommendations"].append("End-to-end issues detected - check system integration")
        
        if "disruption" in failed_suites:
            report["summary"]["recommendations"].append("Disruption handling issues detected - check disruption management system")
        
        if "ai_stress" in failed_suites:
            report["summary"]["recommendations"].append("AI/Stress test issues detected - check system performance and AI functionality")
        
        # Add next steps
        if success_rate >= 90:
            report["summary"]["next_steps"].append("Excellent test results - system is ready for production")
        elif success_rate >= 80:
            report["summary"]["next_steps"].append("Good test results - address minor issues before production")
        else:
            report["summary"]["next_steps"].append("Test results need improvement - fix critical issues before proceeding")
        
        return report

    def run_all_tests(self, test_suites: List[str] = None) -> Dict[str, Any]:
        """Run all or specified test suites"""
        print("🧪 Starting Master Test Execution...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Define available test suites
        available_suites = {
            "frontend": self.run_frontend_tests,
            "backend": self.run_backend_tests,
            "database": self.run_database_tests,
            "e2e": self.run_e2e_tests,
            "disruption": self.run_disruption_tests,
            "ai_stress": self.run_ai_stress_tests
        }
        
        # Determine which test suites to run
        if test_suites is None:
            test_suites = list(available_suites.keys())
        
        # Run selected test suites
        for suite_name in test_suites:
            if suite_name in available_suites:
                try:
                    result = available_suites[suite_name]()
                    self.test_results[suite_name] = result
                except Exception as e:
                    self.test_results[suite_name] = {
                        "status": "FAIL",
                        "duration": 0,
                        "error": str(e)
                    }
                    self.log_test_suite(suite_name.title() + " Tests", "FAIL", f"Test suite error: {str(e)}")
            else:
                print(f"⚠️ Unknown test suite: {suite_name}")
        
        self.total_duration = time.time() - self.start_time
        
        # Generate comprehensive report
        report = self.generate_comprehensive_report()
        
        # Print summary
        print("=" * 60)
        print(f"🎯 Master Test Execution Complete!")
        print(f"📊 Overall Results: {report['test_execution']['test_suites_passed']}/{report['test_execution']['test_suites_run']} test suites passed")
        print(f"📈 Success Rate: {report['test_execution']['overall_success_rate']:.1f}%")
        print(f"⏱️ Total Duration: {self.total_duration:.2f}s")
        print(f"🏆 Overall Status: {report['summary']['overall_status']}")
        
        if report['summary']['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['summary']['recommendations']:
                print(f"   • {rec}")
        
        if report['summary']['next_steps']:
            print("\n🎯 Next Steps:")
            for step in report['summary']['next_steps']:
                print(f"   • {step}")
        
        return report

def main():
    """Main function to run master test suite"""
    parser = argparse.ArgumentParser(description="Master Test Runner for AeroRhythm POC")
    parser.add_argument("--suites", nargs="+", 
                       choices=["frontend", "backend", "database", "e2e", "disruption", "ai_stress"],
                       help="Specific test suites to run (default: all)")
    parser.add_argument("--output", default="comprehensive_test_report.json",
                       help="Output file for test report")
    args = parser.parse_args()
    
    runner = MasterTestRunner()
    report = runner.run_all_tests(args.suites)
    
    # Save comprehensive report
    output_file = PROJECT_ROOT / "backend" / "tests" / args.output
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Comprehensive report saved to: {output_file}")
    
    # Exit with appropriate code
    overall_status = report['summary']['overall_status']
    sys.exit(0 if overall_status == "PASS" else 1)

if __name__ == "__main__":
    main()
