"""
Async wrapper for OrcaSheets tool to work with ToolCollection.
"""

import asyncio
from typing import Any

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

from .orcasheets_tool import OrcaSheetsTool


class AsyncOrcaSheetsTool(BaseAnthropicTool):
    """Async wrapper around OrcaSheetsTool for compatibility with ToolCollection."""
    
    def __init__(self, config=None):
        self.orcasheets_tool = OrcaSheetsTool(config)
    
    async def __call__(self, **kwargs) -> ToolResult:
        """Execute OrcaSheets automation task asynchronously."""
        # Run the synchronous tool in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: self.orcasheets_tool(**kwargs)
        )
        return result
    
    def to_params(self):
        """Delegate to the wrapped tool."""
        return self.orcasheets_tool.to_params()