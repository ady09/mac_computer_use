"""
Modular test runner for executing JSON-based test automation
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import base64

from .test_schema import TestCase, TestStep, ActionType, OnFailureAction, validate_test_file
from .computer import ComputerTool
from .base import ToolResult, ToolError

from .test_automation import (
    OCREngine,
    ElementFinder,
    ClickHandler,
    ScreenshotHandler,
    TypeHandler,
    KeyHandler,
    WaitHandler,
    ApplicationHandler,
    FileHandler,
    VerificationHandler,
    CustomHandler
)


@dataclass
class StepResult:
    """Result of executing a single test step"""
    step_name: str
    action: str
    status: str  # 'passed', 'failed', 'skipped'
    duration: float
    error_message: Optional[str] = None
    screenshot: Optional[str] = None  # base64 encoded
    output: Optional[str] = None


@dataclass
class TestResult:
    """Result of executing a complete test case"""
    test_name: str
    test_file: str
    status: str  # 'passed', 'failed', 'error'
    start_time: datetime
    end_time: datetime
    duration: float
    setup_results: List[StepResult]
    step_results: List[StepResult]
    cleanup_results: List[StepResult]
    error_message: Optional[str] = None
    total_steps: int = 0
    passed_steps: int = 0
    failed_steps: int = 0


class ModularTestRunner:
    """Main test runner for executing test cases using modular components"""
    
    def __init__(self, tests_base_dir: str = None, reports_dir: str = None):
        self.tests_base_dir = tests_base_dir or "/Users/aditya/Documents/computer-use/mac_computer_use/tests"
        self.reports_dir = reports_dir or f"{self.tests_base_dir}/reports"
        self.computer_tool = ComputerTool()
        
        # Ensure reports directory exists
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize modular components
        self.ocr_engine = OCREngine()
        self.element_finder = ElementFinder(self.ocr_engine)
        
        # Initialize action handlers
        self.screenshot_handler = ScreenshotHandler(self.computer_tool)
        self.click_handler = ClickHandler(self.computer_tool, self.element_finder)
        self.type_handler = TypeHandler(self.computer_tool)
        self.key_handler = KeyHandler(self.computer_tool)
        self.wait_handler = WaitHandler(self.computer_tool)
        self.app_handler = ApplicationHandler(self.computer_tool)
        self.file_handler = FileHandler(self.computer_tool)
        self.verification_handler = VerificationHandler(self.computer_tool, self.element_finder)
        self.custom_handler = CustomHandler(self.computer_tool)
        
        # Action handlers mapping
        self.action_handlers = {
            ActionType.COMPUTER_CLICK: self.click_handler.execute,
            ActionType.COMPUTER_TYPE: self.type_handler.execute,
            ActionType.COMPUTER_SCREENSHOT: self.screenshot_handler.execute,
            ActionType.COMPUTER_KEY: self.key_handler.execute,
            ActionType.WAIT: self.wait_handler.execute,
            ActionType.VERIFY_ELEMENT: self.verification_handler.execute_verify_element,
            ActionType.VERIFY_TEXT: self.verification_handler.execute_verify_text,
            ActionType.OPEN_APPLICATION: self.app_handler.execute_open,
            ActionType.CLOSE_APPLICATION: self.app_handler.execute_close,
            ActionType.FILE_UPLOAD: self.file_handler.execute_upload,
            ActionType.ENSURE_FILE_EXISTS: self.file_handler.execute_ensure_exists,
            ActionType.CUSTOM: self.custom_handler.execute
        }

    async def run_test(self, test_file_path: str) -> TestResult:
        """
        Execute a single test case
        
        Args:
            test_file_path: Path to the JSON test file
            
        Returns:
            TestResult object with execution details
        """
        start_time = datetime.now()
        
        try:
            # Validate and load test case
            test_case = validate_test_file(test_file_path)
            test_name = test_case.metadata.name
            
            print(f"Starting test: {test_name}")
            
            # Execute setup steps
            setup_results = []
            if test_case.setup:
                print("Running setup steps...")
                for step in test_case.setup:
                    step_result = await self._execute_step(step)
                    setup_results.append(step_result)
                    if step_result.status == 'failed':
                        return self._create_failed_result(
                            test_name, test_file_path, start_time, setup_results, [], [],
                            f"Setup step failed: {step_result.error_message}"
                        )
            
            # Execute main test steps
            step_results = []
            print("Running test steps...")
            for i, step in enumerate(test_case.steps, 1):
                print(f"Step {i}/{len(test_case.steps)}: {step.name}")
                step_result = await self._execute_step(step)
                step_results.append(step_result)
                
                if step_result.status == 'failed':
                    # Handle failure based on step configuration
                    if step.on_failure == OnFailureAction.CONTINUE:
                        print(f"Step failed but continuing: {step_result.error_message}")
                        continue
                    elif step.on_failure == OnFailureAction.RETRY:
                        print(f"Step failed, attempting retry: {step_result.error_message}")
                        # Take screenshot before retry
                        retry_screenshot = await self.computer_tool(action='screenshot')
                        print(f"[RETRY] Taking fallback screenshot, retrying step: {step.name}")
                        
                        # Retry the step once
                        retry_result = await self._execute_step(step)
                        if retry_result.status == 'passed':
                            print(f"[RETRY] Step succeeded on retry: {step.name}")
                            # Replace the failed result with the successful retry
                            step_results[-1] = retry_result
                            continue
                        else:
                            print(f"[RETRY] Step failed again after retry: {retry_result.error_message}")
                            # Keep original failed result and stop
                            break
                    else:  # STOP
                        print(f"Step failed, stopping test: {step_result.error_message}")
                        break
            
            # Execute cleanup steps
            cleanup_results = []
            if test_case.cleanup:
                print("Running cleanup steps...")
                for step in test_case.cleanup:
                    step_result = await self._execute_step(step)
                    cleanup_results.append(step_result)
                    # Continue cleanup even if steps fail
            
            # Calculate final status
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            all_step_results = setup_results + step_results + cleanup_results
            total_steps = len(all_step_results)
            passed_steps = len([r for r in all_step_results if r.status == 'passed'])
            failed_steps = len([r for r in all_step_results if r.status == 'failed'])
            
            # Determine overall test status
            if failed_steps == 0:
                status = 'passed'
            else:
                status = 'failed'
            
            return TestResult(
                test_name=test_name,
                test_file=test_file_path,
                status=status,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                setup_results=setup_results,
                step_results=step_results,
                cleanup_results=cleanup_results,
                total_steps=total_steps,
                passed_steps=passed_steps,
                failed_steps=failed_steps
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_name="Unknown",
                test_file=test_file_path,
                status='error',
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                setup_results=[],
                step_results=[],
                cleanup_results=[],
                error_message=str(e),
                total_steps=0,
                passed_steps=0,
                failed_steps=0
            )

    async def _execute_step(self, step: TestStep) -> StepResult:
        """Execute a single test step"""
        start_time = time.time()
        
        try:
            print(f"[TEST] Executing step: {step.name}")
            print(f"[TEST] Action: {step.action}, Params: {step.params}")
            
            # Get the appropriate handler
            handler = self.action_handlers.get(step.action)
            if not handler:
                raise Exception(f"No handler found for action: {step.action}")
            
            # Execute the action
            result = await handler(step.params)
            
            # Check for errors
            if result.error:
                return StepResult(
                    step_name=step.name,
                    action=step.action.value,
                    status='failed',
                    duration=time.time() - start_time,
                    error_message=result.error,
                    screenshot=result.base64_image
                )
            
            print(f"[TEST] Action result: {result.output or ''}")
            if result.base64_image:
                print(f"[TEST] Screenshot captured: {len(result.base64_image)} bytes")
            
            # Check expected outcomes if specified
            expectations_met = True
            if step.expected:
                print(f"[TEST] Checking expected outcomes: {step.expected}")
                expectations_met = await self._verify_expected(step.expected, result, max_retries=1)
                print(f"[TEST] Expectations met: {expectations_met}")
            
            if not expectations_met:
                return StepResult(
                    step_name=step.name,
                    action=step.action.value,
                    status='failed',
                    duration=time.time() - start_time,
                    error_message="Expected outcomes not met",
                    screenshot=result.base64_image,
                    output=result.output
                )
            
            print(f"[TEST] Step completed successfully: {step.name}")
            return StepResult(
                step_name=step.name,
                action=step.action.value,
                status='passed',
                duration=time.time() - start_time,
                screenshot=result.base64_image,
                output=result.output
            )
            
        except Exception as e:
            print(f"[TEST] Step failed with error: {str(e)}")
            return StepResult(
                step_name=step.name,
                action=step.action.value,
                status='failed',
                duration=time.time() - start_time,
                error_message=str(e)
            )

    async def _verify_expected(self, expected: Dict[str, Any], result: ToolResult, max_retries: int = 1) -> bool:
        """Verify expected outcomes with retry logic"""
        try:
            for expectation, value in expected.items():
                if expectation == "window_visible":
                    # Verify window is visible with retry
                    verification_result = await self.verification_handler.execute_verify_window({
                        "app": value, 
                        "max_retries": max_retries, 
                        "wait_time": 2
                    })
                    if verification_result.error:
                        print(f"[VERIFY] Window verification failed: {verification_result.error}")
                        return False
                        
                elif expectation == "text_visible":
                    # Verify text is visible on screen with retry
                    verification_result = await self.verification_handler.execute_verify_text({
                        "text": value, 
                        "max_retries": max_retries, 
                        "wait_time": 2
                    })
                    if verification_result.error:
                        print(f"[VERIFY] Text verification failed: {verification_result.error}")
                        return False
                        
                elif expectation == "element_visible":
                    # Verify element is visible with retry
                    verification_result = await self.verification_handler.execute_verify_element({
                        "element": value, 
                        "max_retries": max_retries, 
                        "wait_time": 2
                    })
                    if verification_result.error:
                        print(f"[VERIFY] Element verification failed: {verification_result.error}")
                        return False
                        
                elif expectation == "dialog_open":
                    # Check if a dialog is open with text-based verification
                    dialog_indicators = ["OK", "Cancel", "Yes", "No", "Close", "Save", "Don't Save"]
                    found_dialog = False
                    for indicator in dialog_indicators:
                        verification_result = await self.verification_handler.execute_verify_text({
                            "text": indicator, 
                            "max_retries": max_retries, 
                            "wait_time": 2
                        })
                        if not verification_result.error:
                            found_dialog = True
                            break
                    if not found_dialog:
                        print(f"[VERIFY] Dialog verification failed: No dialog indicators found")
                        return False
                    
                elif expectation == "upload_complete":
                    # Check for upload completion indicators
                    upload_indicators = ["Upload complete", "Upload successful", "File uploaded", "100%", "Done"]
                    found_completion = False
                    for indicator in upload_indicators:
                        verification_result = await self.verification_handler.execute_verify_text({
                            "text": indicator, 
                            "max_retries": max_retries, 
                            "wait_time": 2
                        })
                        if not verification_result.error:
                            found_completion = True
                            break
                    if not found_completion:
                        print(f"[VERIFY] Upload completion verification failed: No completion indicators found")
                        return False
                    
                else:
                    print(f"[VERIFY] Unknown expectation type: {expectation}")
                    
            return True
            
        except Exception as e:
            print(f"[VERIFY] Error checking expectations: {str(e)}")
            return False

    def _create_failed_result(self, test_name: str, test_file: str, start_time: datetime,
                             setup_results: List[StepResult], step_results: List[StepResult],
                             cleanup_results: List[StepResult], error_message: str) -> TestResult:
        """Create a failed test result"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return TestResult(
            test_name=test_name,
            test_file=test_file,
            status='failed',
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            setup_results=setup_results,
            step_results=step_results,
            cleanup_results=cleanup_results,
            error_message=error_message,
            total_steps=len(step_results),
            passed_steps=len([r for r in step_results if r.status == 'passed']),
            failed_steps=len([r for r in step_results if r.status == 'failed'])
        )

    def generate_report(self, results: List[TestResult], output_file: str = None) -> str:
        """Generate HTML test report"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.reports_dir}/test_report_{timestamp}.html"
        
        # Generate HTML report
        html_content = self._generate_html_report(results)
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"Test report generated: {output_file}")
        return output_file

    def _generate_html_report(self, results: List[TestResult]) -> str:
        """Generate HTML content for test report"""
        total_tests = len(results)
        passed_tests = len([r for r in results if r.status == 'passed'])
        failed_tests = len([r for r in results if r.status == 'failed'])
        error_tests = len([r for r in results if r.status == 'error'])
        
        # Calculate success rate safely to avoid division by zero
        success_rate = f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Automation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .test-result {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .passed {{ border-left: 5px solid #28a745; }}
                .failed {{ border-left: 5px solid #dc3545; }}
                .error {{ border-left: 5px solid #ffc107; }}
                .step-result {{ margin: 5px 0; padding: 8px; background: #f8f9fa; border-radius: 3px; }}
                .screenshot {{ max-width: 300px; cursor: pointer; }}
                details {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>Test Automation Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {total_tests}</p>
                <p>Passed: {passed_tests}</p>
                <p>Failed: {failed_tests}</p>
                <p>Errors: {error_tests}</p>
                <p>Success Rate: {success_rate}</p>
            </div>
        """
        
        for result in results:
            html += f"""
            <div class="test-result {result.status}">
                <h3>{result.test_name}</h3>
                <p><strong>Status:</strong> {result.status.upper()}</p>
                <p><strong>Duration:</strong> {result.duration:.2f}s</p>
                <p><strong>File:</strong> {result.test_file}</p>
                
                {f'<p><strong>Error:</strong> {result.error_message}</p>' if result.error_message else ''}
                
                <details>
                    <summary>Step Details ({result.passed_steps}/{result.total_steps} passed)</summary>
            """
            
            all_steps = result.setup_results + result.step_results + result.cleanup_results
            for i, step in enumerate(all_steps, 1):
                status_emoji = "✅" if step.status == "passed" else "❌"
                html += f"""
                    <div class="step-result">
                        <strong>{status_emoji} Step {i}: {step.step_name}</strong><br>
                        Action: {step.action}<br>
                        Duration: {step.duration:.2f}s<br>
                        {f'Error: {step.error_message}<br>' if step.error_message else ''}
                        {f'Output: {step.output}<br>' if step.output else ''}
                        {f'<img src="data:image/png;base64,{step.screenshot}" class="screenshot" alt="Screenshot">' if step.screenshot else ''}
                    </div>
                """
            
            html += """
                </details>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html