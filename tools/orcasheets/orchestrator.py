"""
Main orchestrator for OrcaSheets automation tasks.
"""

import asyncio
from typing import Any, Dict, Optional

from .adapter import OrcaSheetsAdapter
from .file_operations import FileOperations
from .ui_operations import UIOperations
from ..computer import ComputerTool
from ..base import ToolResult


class OrcaSheetsOrchestrator:
    """Main orchestrator that coordinates OrcaSheets automation tasks."""
    
    def __init__(self, computer_tool: ComputerTool):
        self.computer = computer_tool
        self.adapter = OrcaSheetsAdapter(computer_tool)
        self.file_ops = FileOperations()
        self.ui_ops = UIOperations(computer_tool)
    
    async def execute_task(self, action: str, **kwargs) -> ToolResult:
        """Execute an OrcaSheets task based on the action and parameters."""
        try:
            if action == "open":
                return await self._handle_open(**kwargs)
            elif action == "upload":
                return await self._handle_upload(**kwargs)
            elif action == "create_sheet":
                return await self._handle_create_sheet(**kwargs)
            elif action == "download":
                return await self._handle_download(**kwargs)
            elif action == "analyze":
                return await self._handle_analyze(**kwargs)
            else:
                return ToolResult(error=f"Unknown OrcaSheets action: {action}")
                
        except Exception as e:
            return ToolResult(error=f"OrcaSheets task failed: {str(e)}")
    
    async def _handle_open(self, project_name: Optional[str] = None, **kwargs) -> ToolResult:
        """Handle opening OrcaSheets application."""
        success = await self.adapter.open_application(project_name)
        
        if success:
            # Take a screenshot to show the result
            screenshot_result = await self.computer(action="screenshot")
            return ToolResult(
                output=f"Successfully opened OrcaSheets" + (f" with project: {project_name}" if project_name else ""),
                base64_image=screenshot_result.base64_image if screenshot_result else None
            )
        else:
            return ToolResult(error="Failed to open OrcaSheets application")
    
    async def _handle_upload(self, file_path: str, project_name: Optional[str] = None, **kwargs) -> ToolResult:
        """Handle file upload to OrcaSheets."""
        # First ensure OrcaSheets is open
        await self.adapter.open_application(project_name)
        
        # Validate file exists
        resolved_path = self.adapter._resolve_file_path(file_path)
        if not resolved_path.exists():
            return ToolResult(error=f"File not found: {file_path}")
        
        # Perform upload
        success = await self.adapter.upload_file(str(resolved_path))
        
        if success:
            # Take a screenshot to show the result
            screenshot_result = await self.computer(action="screenshot")
            return ToolResult(
                output=f"Successfully uploaded {resolved_path.name} to OrcaSheets",
                base64_image=screenshot_result.base64_image if screenshot_result else None
            )
        else:
            return ToolResult(error=f"Failed to upload {resolved_path.name}")
    
    async def _handle_create_sheet(self, sheet_name: Optional[str] = None, project_name: Optional[str] = None, **kwargs) -> ToolResult:
        """Handle creating a new sheet."""
        # Ensure OrcaSheets is open
        await self.adapter.open_application(project_name)
        
        # Try to create new sheet using keyboard shortcut
        await self.computer(action="key", text="cmd+n")
        await asyncio.sleep(1)
        
        # If sheet name provided, enter it
        if sheet_name:
            await self.ui_ops.type_in_field(sheet_name)
            await self.computer(action="key", text="Return")
        
        # Take screenshot
        screenshot_result = await self.computer(action="screenshot")
        
        return ToolResult(
            output=f"Created new sheet: {sheet_name or 'Untitled'}",
            base64_image=screenshot_result.base64_image if screenshot_result else None
        )
    
    async def _handle_download(self, file_path: Optional[str] = None, project_name: Optional[str] = None, **kwargs) -> ToolResult:
        """Handle downloading from OrcaSheets."""
        # Ensure OrcaSheets is open
        await self.adapter.open_application(project_name)
        
        # Use export/download functionality
        await self.computer(action="key", text="cmd+e")  # Export shortcut
        await asyncio.sleep(1)
        
        # If file path specified, navigate to save location
        if file_path:
            save_path = self.adapter._resolve_file_path(file_path)
            await self.computer(action="key", text="cmd+shift+g")
            await asyncio.sleep(0.5)
            await self.computer(action="type", text=str(save_path.parent))
            await self.computer(action="key", text="Return")
            await asyncio.sleep(0.5)
            await self.computer(action="type", text=save_path.name)
        
        await self.computer(action="key", text="Return")
        
        # Take screenshot
        screenshot_result = await self.computer(action="screenshot")
        
        return ToolResult(
            output="Initiated download from OrcaSheets",
            base64_image=screenshot_result.base64_image if screenshot_result else None
        )
    
    async def _handle_analyze(self, project_name: Optional[str] = None, sheet_name: Optional[str] = None, **kwargs) -> ToolResult:
        """Handle data analysis in OrcaSheets."""
        # Ensure OrcaSheets is open
        await self.adapter.open_application(project_name)
        
        # Take screenshot to analyze current state
        screenshot_result = await self.computer(action="screenshot")
        
        return ToolResult(
            output=f"Analyzing data in OrcaSheets" + (f" project: {project_name}" if project_name else "") + (f", sheet: {sheet_name}" if sheet_name else ""),
            base64_image=screenshot_result.base64_image if screenshot_result else None
        )