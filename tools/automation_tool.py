"""
Test Automation Tool for Claude Desktop integration
Provides a simple interface for running test automation via MCP
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from anthropic.types.beta import BetaToolUnionParam

from .base import BaseAnthropicTool, ToolResult
from .test_automation import TestAutomationTool
from .test_parser import TestCommandParser


class AutomationTool(BaseAnthropicTool):
    """
    Test automation tool that can execute JSON-based tests using natural language commands
    """
    
    name: str = "automation"
    
    def __init__(self):
        super().__init__()
        self.test_tool = TestAutomationTool()
        self.parser = TestCommandParser()
    
    def to_params(self) -> BetaToolUnionParam:
        return {
            "name": self.name,
            "type": "function", 
            "function": {
                "name": self.name,
                "description": "Execute test automation using natural language commands. Can run predefined JSON test cases for applications like Spotify, OrcaSheets, mobile apps, and web apps.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Natural language command describing what to test. Examples: 'test spotify music playback', 'run all spotify tests', 'test file upload for orcasheets', 'create playlist in spotify'"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["execute", "list", "validate", "help"],
                            "description": "Action to perform: execute (run tests), list (show available tests), validate (check test files), help (show usage)"
                        }
                    },
                    "required": ["command"]
                }
            }
        }
    
    async def __call__(self, *, command: str, action: str = "execute", **kwargs) -> ToolResult:
        """
        Execute test automation based on natural language command
        
        Args:
            command: Natural language test command
            action: Action to perform (execute, list, validate, help)
        """
        try:
            if action == "help":
                return self._get_help()
            
            elif action == "list":
                return await self._list_available_tests()
            
            elif action == "validate":
                return await self._validate_tests()
            
            elif action == "execute":
                return await self._execute_tests(command)
            
            else:
                return ToolResult(error=f"Unknown action: {action}")
                
        except Exception as e:
            return ToolResult(error=f"Automation tool error: {str(e)}")
    
    async def _execute_tests(self, command: str) -> ToolResult:
        """Execute tests based on natural language command"""
        try:
            print(f"[AUTOMATION] Executing command: {command}")
            
            # Parse and execute the command
            results = await self.test_tool.execute_command(command)
            
            # Generate report
            report_path = self.test_tool.runner.generate_report(results)
            
            # Prepare summary
            total_tests = len(results)
            passed_tests = len([r for r in results if r.status == 'passed'])
            failed_tests = len([r for r in results if r.status == 'failed'])
            error_tests = len([r for r in results if r.status == 'error'])
            
            # Create output message
            output_lines = [
                f"✅ Test Automation Completed",
                f"",
                f"📊 Results Summary:",
                f"   Total Tests: {total_tests}",
                f"   Passed: {passed_tests}",
                f"   Failed: {failed_tests}",
                f"   Errors: {error_tests}",
                f"   Success Rate: {(passed_tests/total_tests*100):.1f}%",
                f"",
                f"📄 Report: {report_path}",
                f""
            ]
            
            # Add details for each test
            if results:
                output_lines.append("📝 Test Details:")
                for i, result in enumerate(results, 1):
                    status_emoji = "✅" if result.status == 'passed' else "❌" if result.status == 'failed' else "⚠️"
                    output_lines.append(f"   {status_emoji} {result.test_name} ({result.duration:.1f}s)")
                    
                    if result.error_message:
                        output_lines.append(f"      Error: {result.error_message}")
            
            # Open report if on macOS
            try:
                if os.path.exists(report_path):
                    os.system(f"open '{report_path}'")
                    output_lines.append(f"📖 Report opened in browser")
            except:
                pass
            
            output = "\n".join(output_lines)
            
            if failed_tests > 0 or error_tests > 0:
                return ToolResult(output=output, error=f"{failed_tests + error_tests} test(s) failed")
            else:
                return ToolResult(output=output)
                
        except Exception as e:
            return ToolResult(error=f"Failed to execute tests: {str(e)}")
    
    async def _list_available_tests(self) -> ToolResult:
        """List all available test cases"""
        try:
            available_tests = self.test_tool.get_available_tests()
            
            if not available_tests:
                return ToolResult(output="No test cases found. Check the tests directory structure.")
            
            output_lines = ["📋 Available Test Cases:", ""]
            
            for project, tests in available_tests.items():
                output_lines.append(f"🎯 {project.upper()}:")
                for test in tests:
                    output_lines.append(f"   • {test}")
                output_lines.append("")
            
            total_tests = sum(len(tests) for tests in available_tests.values())
            output_lines.append(f"Total: {total_tests} tests across {len(available_tests)} projects")
            
            output_lines.extend([
                "",
                "💡 Usage Examples:",
                "   • 'test spotify music playback'",
                "   • 'run all spotify tests'",
                "   • 'test file upload for orcasheets'",
                "   • 'create playlist in spotify'"
            ])
            
            return ToolResult(output="\n".join(output_lines))
            
        except Exception as e:
            return ToolResult(error=f"Failed to list tests: {str(e)}")
    
    async def _validate_tests(self) -> ToolResult:
        """Validate all test files"""
        try:
            validation_results = self.test_tool.validate_tests()
            
            valid_count = len(validation_results["valid"])
            invalid_count = len(validation_results["invalid"])
            
            output_lines = [
                f"🔍 Test Validation Results:",
                f"",
                f"✅ Valid tests: {valid_count}",
                f"❌ Invalid tests: {invalid_count}",
                f""
            ]
            
            if validation_results["invalid"]:
                output_lines.append("❌ Invalid test files:")
                for invalid in validation_results["invalid"]:
                    output_lines.append(f"   • {invalid}")
                output_lines.append("")
            
            if validation_results["valid"]:
                output_lines.append("✅ Valid test files:")
                for valid in validation_results["valid"]:
                    test_name = Path(valid).stem
                    project = Path(valid).parent.name
                    output_lines.append(f"   • {project}/{test_name}")
            
            if invalid_count > 0:
                return ToolResult(output="\n".join(output_lines), error=f"{invalid_count} invalid test file(s)")
            else:
                return ToolResult(output="\n".join(output_lines))
                
        except Exception as e:
            return ToolResult(error=f"Failed to validate tests: {str(e)}")
    
    def _get_help(self) -> ToolResult:
        """Get help information"""
        help_text = """
🤖 Test Automation Framework Help

📋 AVAILABLE ACTIONS:
   • execute - Run test automation (default)
   • list    - Show available test cases
   • validate - Check test file validity
   • help    - Show this help message

🎯 EXAMPLE COMMANDS:

Spotify Tests:
   • "test spotify music playback"
   • "run all spotify tests"
   • "create playlist in spotify"
   • "test spotify shuffle play"
   • "search artist in spotify"

OrcaSheets Tests:
   • "test file upload for orcasheets"
   • "run orcasheets automation"

Mobile App Tests:
   • "test mobile app login using emulator"
   • "run mobile app tests"

Web App Tests:
   • "test web app checkout flow"
   • "run web application tests"

General:
   • "run all tests"
   • "validate all test files"
   • "list available tests"

📁 TEST STRUCTURE:
Tests are organized in JSON files under:
   tests/projects/{project_name}/{test_name}.json

🎵 SPOTIFY TESTS AVAILABLE:
   • play_music - Basic music playback
   • create_playlist - Playlist management
   • shuffle_play - Playback controls
   • search_artist - Artist discovery

💡 TIP: Use natural language! The framework understands
context and will find the appropriate test to run.
"""
        return ToolResult(output=help_text)