"""
Base action handler for test automation
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any

from ...base import ToolResult


class BaseActionHandler(ABC):
    """Base class for all action handlers"""
    
    def __init__(self, computer_tool):
        self.computer_tool = computer_tool
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute the action with given parameters"""
        pass
    
    def validate_params(self, params: Dict[str, Any], required_params: list) -> bool:
        """Validate that all required parameters are present"""
        for param in required_params:
            if param not in params:
                return False
        return True