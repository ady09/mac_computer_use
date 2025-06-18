"""Base class for OrcaSheets automation."""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any
from ..computer import ComputerTool

@dataclass
class OrcaSheetsConfig:
    """Configuration for OrcaSheets automation."""
    default_project: str = "Default Project"
    app_name: str = "OrcaSheets"
    search_timeout: int = 10
    upload_timeout: int = 30
    retry_attempts: int = 3

class OrcaSheetsAutomation:
    """Base class for OrcaSheets automation functionality.
    This is a wrapper around ComputerTool for OrcaSheets-specific operations."""

    async def handle_upload(self, file_path: str, project_name: Optional[str] = None, **kwargs):
        """Handle file upload to OrcaSheets."""
        # Validate file path
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")
            
        # Open OrcaSheets using Spotlight
        await self._press_key("cmd+space")
        await asyncio.sleep(0.5)
        await self._type_text(self.config.app_name)
        await asyncio.sleep(0.5)
        await self._press_key("Return")
        await asyncio.sleep(2)
        
        # Select project if specified
        if project_name:
            await self._type_text(project_name)
            await asyncio.sleep(0.5)
            await self._press_key("Return")
            await asyncio.sleep(2)
            
        # Handle file upload
        await self._press_key("cmd+o")  # Open file dialog
        await asyncio.sleep(1)
        await self._type_text(str(path.absolute()))
        await asyncio.sleep(0.5)
        await self._press_key("Return")
        
        # Wait for upload to complete
        await asyncio.sleep(self.config.upload_timeout)
        return True

    async def handle_open_project(self, project_name: Optional[str] = None, **kwargs):
        """Handle opening an OrcaSheets project."""
        # Open OrcaSheets using Spotlight
        await self._press_key("cmd+space")
        await asyncio.sleep(0.5)
        await self._type_text(self.config.app_name)
        await asyncio.sleep(0.5)
        await self._press_key("Return")
        await asyncio.sleep(2)
        
        # Select project if specified
        if project_name:
            await self._type_text(project_name)
            await asyncio.sleep(0.5)
            await self._press_key("Return")
            await asyncio.sleep(2)
        
        return True

    async def handle_new_sheet(self, project_name: Optional[str] = None, **kwargs):
        """Handle creating a new sheet."""
        # First open/select project
        await self.handle_open_project(project_name)
        
        # Take screenshot to analyze UI for "Add new sheet" button
        await self._take_screenshot()
        
        # This is a placeholder - actual coordinates would need to be determined
        # In a real implementation, you'd use image recognition to find the button
        await self._click(100, 100)
        await asyncio.sleep(1)
        
        return True
    
    def __init__(self, computer_tool: ComputerTool, config: Optional[OrcaSheetsConfig] = None):
        """Initialize with a computer tool instance and optional config."""
        self.computer = computer_tool
        self.config = config or OrcaSheetsConfig()
        
    async def _type_text(self, text: str) -> None:
        """Type text using the computer tool."""
        await self.computer("type", text=text)
        
    async def _press_key(self, key: str) -> None:
        """Press a key using the computer tool."""
        await self.computer("key", text=key)
        
    async def _click(self, x: int, y: int) -> None:
        """Click at coordinates using the computer tool."""
        await self.computer("left_click", coordinate=(x, y))
        
    async def _take_screenshot(self) -> str:
        """Take a screenshot using the computer tool."""
        result = await self.computer("screenshot")
        return result.base64_image if result and result.base64_image else ""

    def is_orcasheets_task(self, task: str) -> bool:
        """Determine if a task is related to OrcaSheets."""
        orcasheets_keywords = {
            'orcasheets', 'orca sheets', 'spreadsheet', 
            'upload', 'download', 'csv', 'excel',
            'project', 'sheet', 'workbook'
        }
        return any(keyword in task.lower() for keyword in orcasheets_keywords)

    async def dispatch_task(self, task: str, **kwargs: Any):
        """Dispatch OrcaSheets tasks to appropriate handlers."""
        if not self.is_orcasheets_task(task):
            raise ValueError("This task is not related to OrcaSheets")
            
        task_lower = task.lower()
        if 'upload' in task_lower:
            return await self.handle_upload(**kwargs)
        elif 'open' in task_lower:
            return await self.handle_open_project(**kwargs)
        elif 'new sheet' in task_lower:
            return await self.handle_new_sheet(**kwargs)
        else:
            raise ValueError(f"Unknown OrcaSheets task: {task}")
            
    async def handle_upload(self, **kwargs: Any):
        """Handle file upload tasks."""
        raise NotImplementedError("Child classes must implement handle_upload")
        
    async def handle_open_project(self, **kwargs: Any):
        """Handle project opening tasks."""
        raise NotImplementedError("Child classes must implement handle_open_project")
        
    async def handle_new_sheet(self, **kwargs: Any):
        """Handle new sheet creation tasks."""
        raise NotImplementedError("Child classes must implement handle_new_sheet")
