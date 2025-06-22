"""
OrcaSheets automation tool for Anthropic's computer use API.
"""

from typing import Literal, Optional
from anthropic.types.beta import BetaToolUseBlock

from .base import BaseAnthropicTool, ToolError, ToolResult
from .orcasheets.orcasheets_automation import OrcaSheetsAutomation


class OrcaSheetsTool(BaseAnthropicTool):
    """
    A tool for automating OrcaSheets application tasks.
    Provides functionality to open OrcaSheets, select projects, and upload files.
    """

    name: Literal["orcasheets"] = "orcasheets"
    api_type: Literal["orcasheets"] = "orcasheets"

    def __init__(self):
        super().__init__()
        self.automation = OrcaSheetsAutomation()

    def to_params(self):
        return {
            "name": self.name,
            "type": "custom",
            "description": "Automate OrcaSheets application tasks including opening the app, selecting projects, and uploading files",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "open_app",
                            "select_project", 
                            "upload_file",
                            "full_workflow",
                            "take_screenshot"
                        ],
                        "description": "The action to perform in OrcaSheets"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project to select (optional, defaults to 'default')"
                    },
                    "file_path": {
                        "type": "string", 
                        "description": "Path to the file to upload (required for upload_file and full_workflow actions)"
                    }
                },
                "required": ["action"]
            }
        }

    async def __call__(
        self,
        *,
        action: str,
        project_name: Optional[str] = "default",
        file_path: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        """
        Execute OrcaSheets automation actions.
        
        Args:
            action: The action to perform
            project_name: Name of project to select (optional)
            file_path: Path to file to upload (required for upload actions)
        """
        
        try:
            if action == "open_app":
                await self.automation.search_and_open_app("OrcaSheets")
                await self.automation.wait_for_app_launch()
                return ToolResult(
                    output="OrcaSheets application opened successfully",
                    error=None,
                    base64_image=None
                )
                
            elif action == "select_project":
                if not project_name:
                    project_name = "default"
                await self.automation.select_project(project_name)
                return ToolResult(
                    output=f"Selected project: {project_name}",
                    error=None,
                    base64_image=None
                )
                
            elif action == "upload_file":
                if not file_path:
                    raise ToolError("file_path is required for upload_file action")
                
                await self.automation.add_new_sheet()
                await self.automation.upload_file(file_path)
                return ToolResult(
                    output=f"File uploaded successfully: {file_path}",
                    error=None,
                    base64_image=None
                )
                
            elif action == "full_workflow":
                if not file_path:
                    raise ToolError("file_path is required for full_workflow action")
                
                if not project_name:
                    project_name = "default"
                    
                success = await self.automation.full_workflow(file_path, project_name)
                
                if success:
                    return ToolResult(
                        output=f"Complete workflow executed successfully: opened OrcaSheets, selected project '{project_name}', and uploaded '{file_path}'",
                        error=None,
                        base64_image=None
                    )
                else:
                    return ToolResult(
                        output=None,
                        error="Workflow execution failed",
                        base64_image=None
                    )
                    
            elif action == "take_screenshot":
                screenshot_result = await self.automation.take_debug_screenshot("orcasheets_debug.png")
                return ToolResult(
                    output="Debug screenshot taken and saved as orcasheets_debug.png",
                    error=None,
                    base64_image=screenshot_result.base64_image
                )
                
            else:
                raise ToolError(f"Unknown action: {action}")
                
        except Exception as e:
            return ToolResult(
                output=None,
                error=f"OrcaSheets automation error: {str(e)}",
                base64_image=None
            )