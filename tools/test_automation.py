"""
Main test automation tool that integrates all components
"""

import asyncio
import os
from pathlib import Path
from typing import List, Optional

from .test_parser import TestCommandParser, ParsedCommand
from .test_runner import TestRunner, TestResult
from .test_schema import validate_test_directory


class TestAutomationTool:
    """Main interface for the test automation framework"""
    
    def __init__(self, tests_base_dir: str = None):
        self.tests_base_dir = tests_base_dir or "/Users/aditya/Documents/computer-use/mac_computer_use/tests"
        self.parser = TestCommandParser(self.tests_base_dir)
        self.runner = TestRunner(self.tests_base_dir)
    
    async def execute_command(self, command: str) -> List[TestResult]:
        """
        Execute a natural language test command
        
        Args:
            command: Natural language command (e.g., "Test file uploading flow for Orcasheets")
            
        Returns:
            List of TestResult objects
        """
        print(f"Parsing command: {command}")
        
        # Parse the command
        parsed = self.parser.parse(command)
        print(f"Parsed command: {parsed}")
        
        # Execute based on parsed action
        if parsed.action == 'run_test':
            return await self._run_single_test(parsed)
        elif parsed.action == 'run_suite':
            return await self._run_test_suite(parsed)
        elif parsed.action == 'run_all':
            return await self._run_all_tests(parsed)
        else:
            raise ValueError(f"Unknown action: {parsed.action}")
    
    async def _run_single_test(self, parsed: ParsedCommand) -> List[TestResult]:
        """Run a single test based on parsed command"""
        test_file = parsed.test_file
        
        if not test_file:
            # Try to find test file based on project and feature
            if parsed.project and parsed.feature:
                test_file = self._find_test_file(parsed.project, parsed.feature)
            else:
                raise ValueError("Could not determine test file to run")
        
        if not test_file or not os.path.exists(test_file):
            raise FileNotFoundError(f"Test file not found: {test_file}")
        
        print(f"Running test: {test_file}")
        result = await self.runner.run_test(test_file)
        return [result]
    
    async def _run_test_suite(self, parsed: ParsedCommand) -> List[TestResult]:
        """Run multiple tests based on parsed command"""
        test_files = []
        
        if parsed.test_directory:
            # Run all tests in directory
            test_files = self._get_test_files_in_directory(parsed.test_directory)
        elif parsed.project:
            # Run all tests for project
            project_dir = f"{self.tests_base_dir}/projects/{parsed.project}"
            test_files = self._get_test_files_in_directory(project_dir)
        elif parsed.tags:
            # Run tests with specific tags
            test_files = self._get_test_files_by_tags(parsed.tags)
        else:
            raise ValueError("Could not determine which tests to run")
        
        if not test_files:
            raise ValueError("No test files found to run")
        
        print(f"Running {len(test_files)} test(s)")
        results = await self.runner.run_test_suite(test_files, parsed.parallel)
        return results
    
    async def _run_all_tests(self, parsed: ParsedCommand) -> List[TestResult]:
        """Run all available tests"""
        test_files = self._get_all_test_files()
        
        if not test_files:
            raise ValueError("No test files found")
        
        print(f"Running all {len(test_files)} test(s)")
        results = await self.runner.run_test_suite(test_files, parsed.parallel)
        return results
    
    def _find_test_file(self, project: str, feature: str) -> Optional[str]:
        """Find test file based on project and feature"""
        project_dir = Path(self.tests_base_dir) / "projects" / project
        
        if not project_dir.exists():
            return None
        
        # Try exact match first
        test_file = project_dir / f"{feature}.json"
        if test_file.exists():
            return str(test_file)
        
        # Try pattern matching
        for file_path in project_dir.glob("*.json"):
            if feature in file_path.stem.lower():
                return str(file_path)
        
        return None
    
    def _get_test_files_in_directory(self, directory: str) -> List[str]:
        """Get all test files in a directory"""
        test_files = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return test_files
        
        for file_path in dir_path.glob("*.json"):
            if not file_path.name.startswith('.'):
                test_files.append(str(file_path))
        
        return sorted(test_files)
    
    def _get_test_files_by_tags(self, tags: List[str]) -> List[str]:
        """Get test files that match specific tags"""
        test_files = []
        projects_dir = Path(self.tests_base_dir) / "projects"
        
        if not projects_dir.exists():
            return test_files
        
        for project_dir in projects_dir.glob("*/"):
            for test_file in project_dir.glob("*.json"):
                try:
                    # This would require reading and parsing each JSON file
                    # For now, just return all files
                    test_files.append(str(test_file))
                except Exception:
                    continue
        
        return test_files
    
    def _get_all_test_files(self) -> List[str]:
        """Get all available test files"""
        test_files = []
        projects_dir = Path(self.tests_base_dir) / "projects"
        
        if not projects_dir.exists():
            return test_files
        
        for project_dir in projects_dir.glob("*/"):
            test_files.extend(self._get_test_files_in_directory(str(project_dir)))
        
        return test_files
    
    def validate_tests(self) -> dict:
        """Validate all test files in the framework"""
        return validate_test_directory(self.tests_base_dir)
    
    def get_available_tests(self) -> dict:
        """Get list of available tests"""
        return self.parser.get_available_tests()
    
    def suggest_commands(self, partial_command: str) -> List[str]:
        """Get command suggestions based on partial input"""
        return self.parser.suggest_command(partial_command)
    
    async def run_and_report(self, command: str, report_file: str = None) -> str:
        """
        Execute command and generate HTML report
        
        Args:
            command: Natural language test command
            report_file: Optional path for report file
            
        Returns:
            Path to generated report file
        """
        try:
            # Execute the tests
            results = await self.execute_command(command)
            
            # Generate report
            report_path = self.runner.generate_report(results, report_file)
            
            # Print summary
            total_tests = len(results)
            passed_tests = len([r for r in results if r.status == 'passed'])
            failed_tests = len([r for r in results if r.status == 'failed'])
            
            print(f"\nTest Execution Summary:")
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {failed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
            print(f"Report: {report_path}")
            
            return report_path
            
        except Exception as e:
            print(f"Error executing tests: {str(e)}")
            raise


# Convenience function for direct usage
async def run_test_automation(command: str, tests_dir: str = None, report_file: str = None) -> str:
    """
    Convenience function to run test automation with a single command
    
    Args:
        command: Natural language test command
        tests_dir: Optional custom tests directory
        report_file: Optional custom report file path
        
    Returns:
        Path to generated report file
    """
    tool = TestAutomationTool(tests_dir)
    return await tool.run_and_report(command, report_file)


# Example usage in main
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_automation.py '<command>'")
        print("Examples:")
        print("  python test_automation.py 'test file upload flow for orcasheets'")
        print("  python test_automation.py 'run all orcasheets tests'")
        print("  python test_automation.py 'test mobile app login using emulator'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Run the test automation
    asyncio.run(run_test_automation(command))