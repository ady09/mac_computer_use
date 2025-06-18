# tools/orcasheets_tool.py
"""
OrcaSheets automation tool for macOS computer use.
"""

import asyncio
import os
from pathlib import Path
from typing import Any, ClassVar, Literal, Optional

from anthropic.types.beta import BetaToolUnionParam

from .base import BaseAnthropicTool, ToolError, ToolResult
from .computer import ComputerTool


class OrcaSheetsTool(BaseAnthropicTool):
    """
    A tool that provides OrcaSheets-specific automation capabilities.
    This tool wraps around ComputerTool to provide higher-level OrcaSheets operations.
    """

    name: ClassVar[Literal["orcasheets"]] = "orcasheets"
    api_type: ClassVar[Literal["custom"]] = "custom"

    def __init__(self):
        self.computer_tool = ComputerTool()
        super().__init__()

    def to_params(self) -> BetaToolUnionParam:
        return {
            "type": "custom",
            "name": self.name,
            "description": "Automate OrcaSheets operations like opening projects, uploading files, creating sheets, and managing spreadsheet data. Use this tool when users mention OrcaSheets, spreadsheets, CSV uploads, or Excel files.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["open", "upload", "create_sheet", "download", "analyze"],
                        "description": "The OrcaSheets action to perform"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to file for upload/download operations (optional)"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Name of the OrcaSheets project (optional)"
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Name of the sheet to create or work with (optional)"
                    }
                },
                "required": ["action"]
            }
        }

    async def __call__(
        self,
        action: str,
        file_path: Optional[str] = None,
        project_name: Optional[str] = None,
        sheet_name: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        """Execute OrcaSheets automation tasks."""
        
        try:
            if action == "open":
                return await self._open_orcasheets(project_name)
            elif action == "upload":
                if not file_path:
                    raise ToolError("file_path is required for upload action")
                return await self._upload_file(file_path, project_name)
            elif action == "create_sheet":
                return await self._create_sheet(sheet_name, project_name)
            elif action == "download":
                return await self._download_file(file_path, project_name)
            elif action == "analyze":
                return await self._analyze_data(project_name, sheet_name)
            else:
                raise ToolError(f"Unknown action: {action}")
                
        except Exception as e:
            return ToolResult(error=f"OrcaSheets automation failed: {str(e)}")

    async def _open_orcasheets(self, project_name: Optional[str] = None) -> ToolResult:
        """Open OrcaSheets application and optionally select a project."""
        
        # Take initial screenshot
        screenshot_result = await self.computer_tool(action="screenshot")
        
        # Open Spotlight search
        await self.computer_tool(action="key", text="cmd+space")
        await asyncio.sleep(0.5)
        
        # Type OrcaSheets
        await self.computer_tool(action="type", text="OrcaSheets")
        await asyncio.sleep(0.5)
        
        # Press Enter to launch
        await self.computer_tool(action="key", text="Return")
        await asyncio.sleep(3)  # Wait for app to load
        
        # Take screenshot after opening
        final_screenshot = await self.computer_tool(action="screenshot")
        
        if project_name:
            # Look for project selection UI elements
            # This would need UI element detection in a real implementation
            await asyncio.sleep(1)
            await self.computer_tool(action="type", text=project_name)
            await self.computer_tool(action="key", text="Return")
            await asyncio.sleep(2)
            
            return ToolResult(
                output=f"Opened OrcaSheets and selected project: {project_name}",
                base64_image=final_screenshot.base64_image if final_screenshot else None
            )
        
        return ToolResult(
            output="Opened OrcaSheets application",
            base64_image=final_screenshot.base64_image if final_screenshot else None
        )

    async def _upload_file(self, file_path: str, project_name: Optional[str] = None) -> ToolResult:
        """Upload a file to OrcaSheets."""
        
        # Validate file exists
        resolved_path = self._resolve_file_path(file_path)
        if not resolved_path.exists():
            raise ToolError(f"File not found: {file_path}")
        
        # First ensure OrcaSheets is open
        await self._open_orcasheets(project_name)
        
        # Open file dialog (Command+O)
        await self.computer_tool(action="key", text="cmd+o")
        await asyncio.sleep(1)
        
        # Navigate to file location
        # Type the full path
        await self.computer_tool(action="key", text="cmd+shift+g")  # Go to folder
        await asyncio.sleep(0.5)
        await self.computer_tool(action="type", text=str(resolved_path.parent))
        await self.computer_tool(action="key", text="Return")
        await asyncio.sleep(1)
        
        # Select the file
        await self.computer_tool(action="type", text=resolved_path.name)
        await asyncio.sleep(0.5)
        await self.computer_tool(action="key", text="Return")
        
        # Wait for upload to complete
        await asyncio.sleep(3)
        
        # Take final screenshot
        final_screenshot = await self.computer_tool(action="screenshot")
        
        return ToolResult(
            output=f"Successfully uploaded {resolved_path.name} to OrcaSheets",
            base64_image=final_screenshot.base64_image if final_screenshot else None
        )

    async def _create_sheet(self, sheet_name: Optional[str] = None, project_name: Optional[str] = None) -> ToolResult:
        """Create a new sheet in OrcaSheets."""
        
        # Ensure OrcaSheets is open
        await self._open_orcasheets(project_name)
        
        # Look for "New Sheet" or "+" button
        # This would require UI element detection in a real implementation
        # For now, we'll use common keyboard shortcuts
        await self.computer_tool(action="key", text="cmd+n")  # New sheet shortcut
        await asyncio.sleep(1)
        
        if sheet_name:
            await self.computer_tool(action="type", text=sheet_name)
            await self.computer_tool(action="key", text="Return")
        
        # Take screenshot
        final_screenshot = await self.computer_tool(action="screenshot")
        
        return ToolResult(
            output=f"Created new sheet: {sheet_name or 'Untitled'}",
            base64_image=final_screenshot.base64_image if final_screenshot else None
        )

    async def _download_file(self, file_path: Optional[str] = None, project_name: Optional[str] = None) -> ToolResult:
        """Download a file from OrcaSheets."""
        
        # Ensure OrcaSheets is open
        await self._open_orcasheets(project_name)
        
        # Use Export/Download functionality
        await self.computer_tool(action="key", text="cmd+e")  # Export shortcut
        await asyncio.sleep(1)
        
        if file_path:
            resolved_path = self._resolve_file_path(file_path)
            await self.computer_tool(action="key", text="cmd+shift+g")
            await asyncio.sleep(0.5)
            await self.computer_tool(action="type", text=str(resolved_path.parent))
            await self.computer_tool(action="key", text="Return")
            await asyncio.sleep(0.5)
            await self.computer_tool(action="type", text=resolved_path.name)
        
        await self.computer_tool(action="key", text="Return")
        
        # Take screenshot
        final_screenshot = await self.computer_tool(action="screenshot")
        
        return ToolResult(
            output="Initiated download from OrcaSheets",
            base64_image=final_screenshot.base64_image if final_screenshot else None
        )

    async def _analyze_data(self, project_name: Optional[str] = None, sheet_name: Optional[str] = None) -> ToolResult:
        """Analyze data in OrcaSheets."""
        
        # Ensure OrcaSheets is open
        await self._open_orcasheets(project_name)
        
        # Take screenshot to analyze current state
        screenshot = await self.computer_tool(action="screenshot")
        
        return ToolResult(
            output=f"Analyzing data in OrcaSheets project: {project_name or 'current'}, sheet: {sheet_name or 'current'}",
            base64_image=screenshot.base64_image if screenshot else None
        )

    def _resolve_file_path(self, file_path: str) -> Path:
        """Resolve various file path formats to absolute paths."""
        # Handle home directory
        if file_path.startswith('~/'):
            return Path(os.path.expanduser(file_path))
        
        # Handle absolute paths
        if file_path.startswith('/'):
            return Path(file_path)
        
        # Handle relative paths that mention common directories
        file_lower = file_path.lower()
        if 'download' in file_lower and not file_path.startswith('/'):
            downloads_dir = Path.home() / "Downloads"
            filename = os.path.basename(file_path)
            return downloads_dir / filename
        
        # Handle bare filenames - assume they're in Downloads
        if '/' not in file_path:
            downloads_dir = Path.home() / "Downloads" 
            return downloads_dir / file_path
        
        # Default to treating as relative to current directory
        return Path(file_path).resolve()

    @staticmethod
    def is_orcasheets_command(command: str) -> bool:
        """Check if a command is related to OrcaSheets."""
        orcasheets_keywords = {
            'orcasheets', 'orca sheets', 'spreadsheet',
            'upload', 'download', 'csv', 'excel',
            'project', 'sheet', 'workbook'
        }
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in orcasheets_keywords)