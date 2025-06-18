# tools/orcasheets/adapter.py
"""
Adapter for OrcaSheets automation that bridges between high-level commands and low-level computer operations.
"""

import asyncio
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

from ..computer import ComputerTool


class OrcaSheetsAdapter:
    """Adapter that translates OrcaSheets operations to computer tool commands."""
    
    def __init__(self, computer_tool: ComputerTool):
        self.computer = computer_tool
        
    async def open_application(self, project_name: Optional[str] = None) -> bool:
        """Open OrcaSheets application using Spotlight."""
        try:
            # Use Spotlight to open OrcaSheets
            await self.computer(action="key", text="cmd+space")
            await asyncio.sleep(0.5)
            
            await self.computer(action="type", text="OrcaSheets")
            await asyncio.sleep(0.5)
            
            await self.computer(action="key", text="Return")
            await asyncio.sleep(3)  # Wait for app to launch
            
            # If project name is specified, try to select it
            if project_name:
                await asyncio.sleep(1)
                await self.computer(action="type", text=project_name)
                await self.computer(action="key", text="Return")
                await asyncio.sleep(2)
                
            return True
        except Exception:
            return False
    
    async def upload_file(self, file_path: str) -> bool:
        """Upload a file using the file dialog."""
        try:
            # Resolve file path
            resolved_path = self._resolve_file_path(file_path)
            if not resolved_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Open file dialog
            await self.computer(action="key", text="cmd+o")
            await asyncio.sleep(1)
            
            # Navigate to file location using Go to Folder
            await self.computer(action="key", text="cmd+shift+g")
            await asyncio.sleep(0.5)
            
            # Type the directory path
            await self.computer(action="type", text=str(resolved_path.parent))
            await self.computer(action="key", text="Return")
            await asyncio.sleep(1)
            
            # Type the filename to select it
            await self.computer(action="type", text=resolved_path.name)
            await asyncio.sleep(0.5)
            
            # Confirm selection
            await self.computer(action="key", text="Return")
            await asyncio.sleep(2)
            
            return True
        except Exception:
            return False
    
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

