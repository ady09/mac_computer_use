#!/usr/bin/env python3
"""
Refactored HTTP API server for test automation
Uses only the modular test automation framework
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import uvicorn
import sys
import os
import re
from typing import Optional, List, Dict, Any
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.test_runner_modular import ModularTestRunner
from tools.test_schema import validate_test_file

app = FastAPI(title="Test Automation API", version="2.0.0")


class TestExecutionRequest(BaseModel):
    """Request model for test execution"""
    command: str
    project: Optional[str] = None
    feature: Optional[str] = None
    test_file: Optional[str] = None


class TestExecutionResponse(BaseModel):
    """Response model for test execution"""
    status: str
    result: Dict[str, Any]
    message: Optional[str] = None
    report_path: Optional[str] = None


class TestValidationResponse(BaseModel):
    """Response model for test validation"""
    status: str
    valid_tests: List[str]
    invalid_tests: List[Dict[str, Any]]
    total_valid: int
    total_invalid: int


class AvailableTestsResponse(BaseModel):
    """Response model for available tests"""
    status: str
    projects: Dict[str, List[str]]
    total_projects: int
    total_tests: int


class TestAutomationAPI:
    """Main API class for test automation"""
    
    def __init__(self):
        self.tests_base_dir = "/Users/aditya/Documents/computer-use/mac_computer_use/tests"
        self.runner = ModularTestRunner(self.tests_base_dir)
    
    async def execute_command(self, command: str) -> List[Any]:
        """Parse natural language command and execute tests"""
        command_lower = command.lower().strip()
        results = []
        
        print(f"[API] Processing command: {command}")
        
        # Parse the command to determine what tests to run
        if "run all tests" in command_lower:
            # Run all tests
            if "for" in command_lower:
                # Extract project name: "run all tests for orcasheets"
                project_match = re.search(r"run all tests for (\w+)", command_lower)
                if project_match:
                    project = project_match.group(1)
                    results = await self._run_project_tests(project)
                else:
                    results = await self._run_all_tests()
            else:
                results = await self._run_all_tests()
        
        elif "test" in command_lower and "for" in command_lower:
            # Extract project and feature: "test file upload for orcasheets"
            project_match = re.search(r"for (\w+)", command_lower)
            feature_match = re.search(r"test ([\w\s]+) for", command_lower)
            
            if project_match:
                project = project_match.group(1)
                feature = feature_match.group(1).strip().replace(" ", "_") if feature_match else None
                
                if feature:
                    results = await self._run_feature_test(project, feature)
                else:
                    results = await self._run_project_tests(project)
        
        elif "test" in command_lower:
            # Simple test execution: "test search projects"
            feature_match = re.search(r"test ([\w\s]+)", command_lower)
            if feature_match:
                feature = feature_match.group(1).strip().replace(" ", "_")
                # Try to find the test in any project
                results = await self._find_and_run_test(feature)
        
        else:
            raise ValueError(f"Could not parse command: {command}")
        
        return results
    
    async def _run_all_tests(self) -> List[Any]:
        """Run all tests in all projects"""
        results = []
        projects_dir = Path(self.tests_base_dir) / "projects"
        
        if not projects_dir.exists():
            raise FileNotFoundError(f"Projects directory not found: {projects_dir}")
        
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                project_results = await self._run_project_tests(project_dir.name)
                results.extend(project_results)
        
        return results
    
    async def _run_project_tests(self, project: str) -> List[Any]:
        """Run all tests for a specific project"""
        results = []
        project_dir = Path(self.tests_base_dir) / "projects" / project
        
        if not project_dir.exists():
            raise FileNotFoundError(f"Project directory not found: {project_dir}")
        
        # Find all JSON test files in the project directory
        for test_file in project_dir.glob("*.json"):
            try:
                print(f"[API] Running test: {test_file}")
                result = await self.runner.run_test(str(test_file))
                results.append(result)
            except Exception as e:
                print(f"[API] Error running test {test_file}: {e}")
                # Create a dummy error result
                from datetime import datetime
                from tools.test_runner_modular import TestResult
                error_result = TestResult(
                    test_name=test_file.stem,
                    test_file=str(test_file),
                    status='error',
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration=0,
                    setup_results=[],
                    step_results=[],
                    cleanup_results=[],
                    error_message=str(e),
                    total_steps=0,
                    passed_steps=0,
                    failed_steps=0
                )
                results.append(error_result)
        
        return results
    
    async def _run_feature_test(self, project: str, feature: str) -> List[Any]:
        """Run a specific feature test for a project"""
        project_dir = Path(self.tests_base_dir) / "projects" / project
        test_file = project_dir / f"{feature}.json"
        
        if not test_file.exists():
            raise FileNotFoundError(f"Test file not found: {test_file}")
        
        print(f"[API] Running feature test: {test_file}")
        result = await self.runner.run_test(str(test_file))
        return [result]
    
    async def _find_and_run_test(self, feature: str) -> List[Any]:
        """Find and run a test by feature name across all projects"""
        projects_dir = Path(self.tests_base_dir) / "projects"
        
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                test_file = project_dir / f"{feature}.json"
                if test_file.exists():
                    print(f"[API] Found and running test: {test_file}")
                    result = await self.runner.run_test(str(test_file))
                    return [result]
        
        raise FileNotFoundError(f"No test found for feature: {feature}")
    
    def validate_tests(self) -> Dict[str, List]:
        """Validate all test files"""
        valid_tests = []
        invalid_tests = []
        
        projects_dir = Path(self.tests_base_dir) / "projects"
        
        if projects_dir.exists():
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    for test_file in project_dir.glob("*.json"):
                        try:
                            validate_test_file(str(test_file))
                            valid_tests.append(str(test_file))
                        except Exception as e:
                            invalid_tests.append({
                                "file": str(test_file),
                                "error": str(e)
                            })
        
        return {
            "valid": valid_tests,
            "invalid": invalid_tests
        }
    
    def get_available_tests(self) -> Dict[str, List[str]]:
        """Get list of available test cases organized by project"""
        available_tests = {}
        projects_dir = Path(self.tests_base_dir) / "projects"
        
        if projects_dir.exists():
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    project_tests = []
                    for test_file in project_dir.glob("*.json"):
                        try:
                            test_case = validate_test_file(str(test_file))
                            project_tests.append({
                                "name": test_case.metadata.name,
                                "file": test_file.name,
                                "feature": test_case.metadata.feature,
                                "description": test_case.metadata.description,
                                "tags": test_case.metadata.tags
                            })
                        except Exception as e:
                            print(f"[API] Warning: Invalid test file {test_file}: {e}")
                    
                    if project_tests:
                        available_tests[project_dir.name] = project_tests
        
        return available_tests


# Global API instance
test_api = TestAutomationAPI()


@app.get("/")
async def root():
    return {"message": "Test Automation API is running", "version": "2.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "test-automation"}


@app.post("/test/execute", response_model=TestExecutionResponse)
async def execute_test_automation(request: TestExecutionRequest):
    """
    Execute test automation based on natural language command
    
    Examples:
    - "run all tests for orcasheets"
    - "test file upload for orcasheets" 
    - "test search projects"
    - "run all tests"
    """
    try:
        print(f"[API] Received test execution request: {request.command}")
        
        # Execute the command
        results = await test_api.execute_command(request.command)
        
        # Generate report
        report_path = test_api.runner.generate_report(results)
        
        # Prepare response summary
        summary = {
            "total_tests": len(results),
            "passed_tests": len([r for r in results if r.status == 'passed']),
            "failed_tests": len([r for r in results if r.status == 'failed']),
            "error_tests": len([r for r in results if r.status == 'error']),
            "tests": [
                {
                    "name": r.test_name,
                    "status": r.status,
                    "duration": r.duration,
                    "passed_steps": r.passed_steps,
                    "failed_steps": r.failed_steps,
                    "total_steps": r.total_steps,
                    "error_message": r.error_message
                }
                for r in results
            ]
        }
        
        success_rate = (summary['passed_tests'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        
        return TestExecutionResponse(
            status="success",
            result=summary,
            message=f"Test automation completed. {summary['passed_tests']}/{summary['total_tests']} tests passed ({success_rate:.1f}%)",
            report_path=report_path
        )
        
    except Exception as e:
        print(f"[API] Test execution error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Test execution failed: {str(e)}"
        )


@app.get("/test/validate", response_model=TestValidationResponse)
async def validate_tests():
    """
    Validate all test files in the framework
    """
    try:
        validation_results = test_api.validate_tests()
        
        return TestValidationResponse(
            status="success",
            valid_tests=validation_results["valid"],
            invalid_tests=validation_results["invalid"],
            total_valid=len(validation_results["valid"]),
            total_invalid=len(validation_results["invalid"])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test validation failed: {str(e)}"
        )


@app.get("/test/available", response_model=AvailableTestsResponse)
async def get_available_tests():
    """
    Get list of available test cases organized by project
    """
    try:
        available_tests = test_api.get_available_tests()
        
        total_tests = sum(len(tests) for tests in available_tests.values())
        
        return AvailableTestsResponse(
            status="success",
            projects=available_tests,
            total_projects=len(available_tests),
            total_tests=total_tests
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available tests: {str(e)}"
        )


@app.post("/test/run-file")
async def run_specific_test_file(test_file_path: str):
    """
    Run a specific test file by path
    """
    try:
        if not os.path.exists(test_file_path):
            raise FileNotFoundError(f"Test file not found: {test_file_path}")
        
        print(f"[API] Running specific test file: {test_file_path}")
        result = await test_api.runner.run_test(test_file_path)
        
        # Generate report for single test
        report_path = test_api.runner.generate_report([result])
        
        return {
            "status": "success",
            "test_name": result.test_name,
            "test_status": result.status,
            "duration": result.duration,
            "passed_steps": result.passed_steps,
            "failed_steps": result.failed_steps,
            "total_steps": result.total_steps,
            "error_message": result.error_message,
            "report_path": report_path
        }
        
    except Exception as e:
        print(f"[API] Error running test file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Test file execution failed: {str(e)}"
        )


@app.get("/test/projects")
async def get_projects():
    """
    Get list of available projects
    """
    try:
        projects_dir = Path(test_api.tests_base_dir) / "projects"
        projects = []
        
        if projects_dir.exists():
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    test_count = len(list(project_dir.glob("*.json")))
                    projects.append({
                        "name": project_dir.name,
                        "test_count": test_count,
                        "path": str(project_dir)
                    })
        
        return {
            "status": "success",
            "projects": projects,
            "total_projects": len(projects)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get projects: {str(e)}"
        )


if __name__ == "__main__":
    print("[API] Starting Test Automation API server...")
    print("[API] Server will be available at: http://localhost:8000")
    print("[API] API docs at: http://localhost:8000/docs")
    
    # Run the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )