"""
OrcaSheets automation tool implementation.
"""

import time
from typing import Any, Dict

try:
    from anthropic.types.beta import BetaToolUnionParam
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    # Create a mock type for development/testing
    BetaToolUnionParam = dict

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from tools.base import BaseAnthropicTool, ToolResult
except ImportError:
    # Create mock base classes for testing without full dependencies
    class BaseAnthropicTool:
        def __call__(self, **kwargs):
            raise NotImplementedError("Mock implementation")
        
        def to_params(self):
            return {}
    
    class ToolResult:
        def __init__(self, output=None, error=None, base64_image=None):
            self.output = output
            self.error = error
            self.base64_image = base64_image
from ..config import OrcaSheetsConfig
from ..tasks import OrcaSheetsTask, TaskType, TaskValidator
from .ui_automation import UIAutomation


class OrcaSheetsTool(BaseAnthropicTool):
    """Tool for automating OrcaSheets tasks."""
    
    def __init__(self, config: OrcaSheetsConfig = None):
        self.config = config or OrcaSheetsConfig.load_from_env()
        self.ui = UIAutomation(self.config)
    
    def __call__(self, **kwargs) -> ToolResult:
        """Execute OrcaSheets automation task."""
        try:
            # Parse and validate the task
            task_type = kwargs.get('task_type')
            parameters = kwargs.get('parameters', {})
            
            if not task_type:
                return ToolResult(error="No task_type specified")
            
            # Create task object
            try:
                task_enum = TaskType(task_type)
            except ValueError:
                return ToolResult(error=f"Invalid task type: {task_type}")
            
            task = OrcaSheetsTask(task_type=task_enum, parameters=parameters)
            
            # Validate task
            if not task.validate():
                return ToolResult(error="Task validation failed - invalid or unsafe parameters")
            
            # Execute the task
            return self._execute_task(task)
            
        except Exception as e:
            return ToolResult(error=f"Error executing OrcaSheets task: {str(e)}")
    
    def _execute_task(self, task: OrcaSheetsTask) -> ToolResult:
        """Execute a validated OrcaSheets task."""
        if task.task_type == TaskType.OPEN_ORCASHEETS:
            return self._open_orcasheets()
        elif task.task_type == TaskType.COMBINED_OPEN_AND_UPLOAD:
            return self._combined_open_and_upload(task.parameters)
        elif task.task_type == TaskType.UPLOAD_FILE:
            return self._upload_file(task.parameters)
        elif task.task_type == TaskType.SELECT_PROJECT:
            return self._select_project(task.parameters)
        elif task.task_type == TaskType.ADD_NEW_SHEET:
            return self._add_new_sheet()
        else:
            return ToolResult(error=f"Task type not implemented: {task.task_type}")
    
    def _open_orcasheets(self) -> ToolResult:
        """Open OrcaSheets using Spotlight search."""
        try:
            # Take initial screenshot
            screenshot = self.ui.take_screenshot()
            
            # Check if OrcaSheets is already running
            if self.ui.wait_for_window("orcasheets", timeout=2):
                final_screenshot = self.ui.take_screenshot()
                return ToolResult(
                    output="OrcaSheets is already open",
                    base64_image=final_screenshot
                )
            
            # Open Spotlight
            if not self.ui.open_spotlight_search():
                # Get detailed diagnostics
                diagnostics = self.ui.get_diagnostics()
                return ToolResult(
                    error="Failed to open Spotlight search. Please check:\n"
                          "1. macOS Accessibility permissions are enabled\n"
                          "2. Spotlight is enabled in System Preferences\n"
                          "3. Try manually: Cmd+Space\n\n"
                          f"System Diagnostics:\n{diagnostics}",
                    base64_image=screenshot
                )
            
            time.sleep(1)
            
            # Type "orcasheets"
            if not self.ui.type_text("orcasheets"):
                # Take screenshot to show current state
                error_screenshot = self.ui.take_screenshot()
                return ToolResult(
                    error="Failed to type 'orcasheets' in Spotlight. Check if Spotlight search box is active.",
                    base64_image=error_screenshot
                )
            
            time.sleep(2)  # Wait for search results
            
            # Press Enter to launch
            if not self.ui.press_key_combination("return"):
                error_screenshot = self.ui.take_screenshot()
                return ToolResult(
                    error="Failed to press Enter to launch OrcaSheets",
                    base64_image=error_screenshot
                )
            
            time.sleep(3)  # Wait for app to launch
            
            # Wait for OrcaSheets to open
            if not self.ui.wait_for_window("orcasheets", timeout=10):
                error_screenshot = self.ui.take_screenshot()
                return ToolResult(
                    error="OrcaSheets window did not appear within 10 seconds. Possible issues:\n"
                          "1. OrcaSheets is not installed\n"
                          "2. App name in Spotlight is different\n"
                          "3. App is taking longer to launch\n"
                          "4. Spotlight search didn't find the app",
                    base64_image=error_screenshot
                )
            
            # Take screenshot after opening
            final_screenshot = self.ui.take_screenshot()
            
            return ToolResult(
                output="Successfully opened OrcaSheets",
                base64_image=final_screenshot
            )
            
        except Exception as e:
            error_screenshot = self.ui.take_screenshot()
            return ToolResult(
                error=f"Unexpected error while opening OrcaSheets: {str(e)}",
                base64_image=error_screenshot
            )
    
    def _combined_open_and_upload(self, params: Dict[str, Any]) -> ToolResult:
        """Open OrcaSheets and upload a file."""
        file_path = params.get('file_path')
        project_name = params.get('project_name')
        
        if not file_path:
            return ToolResult(error="No file_path specified")
        
        # Check if file exists
        if not self.ui.file_exists(file_path):
            return ToolResult(error=f"File not found: {file_path}")
        
        try:
            # Step 1: Open OrcaSheets
            open_result = self._open_orcasheets()
            if open_result.error:
                return open_result
            
            time.sleep(2)  # Wait for app to fully load
            
            # Step 2: Handle project selection
            if project_name:
                project_result = self._select_project_by_name(project_name)
            else:
                project_result = self._select_default_project()
            
            if project_result.error:
                return project_result
            
            time.sleep(2)
            
            # Step 3: Upload file
            upload_result = self._upload_file_to_project(file_path)
            if upload_result.error:
                return upload_result
            
            return ToolResult(
                output=f"Successfully opened OrcaSheets and uploaded {file_path}",
                base64_image=upload_result.base64_image
            )
            
        except Exception as e:
            return ToolResult(error=f"Failed combined operation: {str(e)}")
    
    def _select_project_by_name(self, project_name: str) -> ToolResult:
        """Select a project by searching for its name."""
        try:
            # Take screenshot to see current state
            screenshot = self.ui.take_screenshot()
            
            # Look for search projects input box and type project name
            # This is a simplified implementation - in practice, you'd need
            # to identify the search box coordinates from the screenshot
            
            # For now, we'll simulate clicking in a typical search box location
            # and typing the project name
            
            # Click in search box (coordinates would be determined from screenshot analysis)
            search_box_x, search_box_y = 400, 200  # Placeholder coordinates
            if not self.ui.click_at_coordinates(search_box_x, search_box_y):
                return ToolResult(error="Failed to click search box")
            
            time.sleep(0.5)
            
            # Type project name
            if not self.ui.type_text(project_name):
                return ToolResult(error="Failed to type project name")
            
            time.sleep(1)
            
            # Press Enter or click on the project
            if not self.ui.press_key_combination("return"):
                return ToolResult(error="Failed to select project")
            
            final_screenshot = self.ui.take_screenshot()
            
            return ToolResult(
                output=f"Selected project: {project_name}",
                base64_image=final_screenshot
            )
            
        except Exception as e:
            return ToolResult(error=f"Failed to select project: {str(e)}")
    
    def _select_default_project(self) -> ToolResult:
        """Select the default project."""
        try:
            screenshot = self.ui.take_screenshot()
            
            # Click on default project (first project in list)
            # Coordinates would be determined from screenshot analysis
            default_project_x, default_project_y = 400, 300  # Placeholder
            
            if not self.ui.click_at_coordinates(default_project_x, default_project_y):
                return ToolResult(error="Failed to click default project")
            
            time.sleep(1)
            
            final_screenshot = self.ui.take_screenshot()
            
            return ToolResult(
                output=f"Selected default project: {self.config.default_project}",
                base64_image=final_screenshot
            )
            
        except Exception as e:
            return ToolResult(error=f"Failed to select default project: {str(e)}")
    
    def _upload_file_to_project(self, file_path: str) -> ToolResult:
        """Upload file to the current project."""
        try:
            screenshot = self.ui.take_screenshot()
            
            # Look for "Add new sheet" button or "+" symbol
            # This requires screenshot analysis to find the exact coordinates
            
            # Check if there's already a file loaded (look for + symbol)
            # or if we need to click "Add new sheet"
            
            # For demonstration, we'll try clicking "Add new sheet" first
            add_sheet_x, add_sheet_y = 500, 400  # Placeholder coordinates
            
            if not self.ui.click_at_coordinates(add_sheet_x, add_sheet_y):
                # Try looking for + symbol instead
                plus_x, plus_y = 600, 350  # Placeholder coordinates
                if not self.ui.click_at_coordinates(plus_x, plus_y):
                    return ToolResult(error="Failed to find upload button or + symbol")
            
            time.sleep(1)
            
            # File dialog should open - navigate to file
            expanded_path = self.ui.expand_path(file_path)
            
            # Use keyboard shortcut to go to file location
            if not self.ui.press_key_combination("cmd+shift+g"):
                return ToolResult(error="Failed to open Go to Folder dialog")
            
            time.sleep(0.5)
            
            # Type the file path
            folder_path = '/'.join(expanded_path.split('/')[:-1])
            if not self.ui.type_text(folder_path):
                return ToolResult(error="Failed to type folder path")
            
            if not self.ui.press_key_combination("return"):
                return ToolResult(error="Failed to navigate to folder")
            
            time.sleep(1)
            
            # Type filename to select it
            filename = expanded_path.split('/')[-1]
            if not self.ui.type_text(filename):
                return ToolResult(error="Failed to type filename")
            
            time.sleep(0.5)
            
            # Click Open/Upload button
            if not self.ui.press_key_combination("return"):
                return ToolResult(error="Failed to upload file")
            
            time.sleep(2)  # Wait for upload to complete
            
            final_screenshot = self.ui.take_screenshot()
            
            return ToolResult(
                output=f"Successfully uploaded file: {file_path}",
                base64_image=final_screenshot
            )
            
        except Exception as e:
            return ToolResult(error=f"Failed to upload file: {str(e)}")
    
    def _upload_file(self, params: Dict[str, Any]) -> ToolResult:
        """Upload file to current project (assumes OrcaSheets is already open)."""
        file_path = params.get('file_path')
        if not file_path:
            return ToolResult(error="No file_path specified")
        
        return self._upload_file_to_project(file_path)
    
    def _select_project(self, params: Dict[str, Any]) -> ToolResult:
        """Select a project (assumes OrcaSheets is already open)."""
        project_name = params.get('project_name')
        if not project_name:
            return self._select_default_project()
        else:
            return self._select_project_by_name(project_name)
    
    def _add_new_sheet(self) -> ToolResult:
        """Add a new sheet to current project."""
        try:
            screenshot = self.ui.take_screenshot()
            
            # Click "Add new sheet" button
            add_sheet_x, add_sheet_y = 500, 400  # Placeholder coordinates
            
            if not self.ui.click_at_coordinates(add_sheet_x, add_sheet_y):
                return ToolResult(error="Failed to click Add new sheet button")
            
            time.sleep(1)
            
            final_screenshot = self.ui.take_screenshot()
            
            return ToolResult(
                output="Successfully clicked Add new sheet",
                base64_image=final_screenshot
            )
            
        except Exception as e:
            return ToolResult(error=f"Failed to add new sheet: {str(e)}")
    
    def to_params(self) -> BetaToolUnionParam:
        """Return tool parameters for Anthropic API."""
        return {
            "type": "custom",
            "name": "orcasheets_automation",
            "description": "Automate OrcaSheets tasks including opening the app, selecting projects, and uploading files. Only OrcaSheets-related tasks are allowed.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task_type": {
                        "type": "string",
                        "enum": [
                            "open_orcasheets",
                            "upload_file", 
                            "select_project",
                            "add_new_sheet",
                            "combined_open_and_upload"
                        ],
                        "description": "Type of OrcaSheets task to perform"
                    },
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to file to upload (must be in Downloads, Documents, or Desktop)"
                            },
                            "project_name": {
                                "type": "string", 
                                "description": "Name of project to select (optional, uses default if not specified)"
                            }
                        },
                        "description": "Task-specific parameters"
                    }
                },
                "required": ["task_type"]
            }
        }