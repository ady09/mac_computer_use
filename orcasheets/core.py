"""
Core framework for OrcaSheets automation.
"""

from typing import Optional, Dict, Any, List
from .config import OrcaSheetsConfig
from .tasks import OrcaSheetsTask, TaskValidator, TaskType
from .tools import OrcaSheetsTool


class OrcaSheetsFramework:
    """Main framework class for OrcaSheets automation."""
    
    def __init__(self, config: Optional[OrcaSheetsConfig] = None):
        """Initialize the framework with configuration."""
        self.config = config or OrcaSheetsConfig.load_from_env()
        self.orcasheets_tool = OrcaSheetsTool(self.config)
        self.validator = TaskValidator()
    
    def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """Process a user request and return the result."""
        try:
            # Parse the user request
            task = self.validator.parse_user_request(user_input)
            
            if not task:
                return {
                    "success": False,
                    "error": "Could not understand the request. Please specify an OrcaSheets task like 'open orcasheets and upload industry.csv from downloads'",
                    "allowed_commands": self._get_allowed_commands()
                }
            
            # Validate the task
            if not task.validate():
                return {
                    "success": False,
                    "error": "Invalid or unsafe task parameters",
                    "task": task.__dict__
                }
            
            # Execute the task
            result = self.orcasheets_tool(
                task_type=task.task_type.value,
                parameters=task.parameters
            )
            
            if result.error:
                return {
                    "success": False,
                    "error": result.error,
                    "task": task.__dict__
                }
            
            return {
                "success": True,
                "output": result.output,
                "screenshot": result.base64_image,
                "task": task.__dict__
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Framework error: {str(e)}"
            }
    
    def _get_allowed_commands(self) -> List[str]:
        """Get list of allowed command examples."""
        return [
            "open orcasheets",
            "open orcasheets and upload industry.csv from downloads",
            "open orcasheets and upload data.xlsx from documents project MyProject",
            "upload report.csv from downloads",
            "select project ProjectName",
            "add new sheet"
        ]
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools in the framework."""
        return ["orcasheets_automation"]
    
    def is_request_allowed(self, user_input: str) -> bool:
        """Check if a user request is allowed (OrcaSheets-related only)."""
        orcasheets_keywords = [
            'orcasheets', 'orca sheets', 'upload', 'sheet', 'project',
            'csv', 'xlsx', 'data', 'file'
        ]
        
        user_lower = user_input.lower()
        
        # Must contain at least one OrcaSheets-related keyword
        has_orcasheets_keyword = any(keyword in user_lower for keyword in orcasheets_keywords)
        
        # Blocked keywords that indicate non-OrcaSheets tasks
        blocked_keywords = [
            'browser', 'chrome', 'firefox', 'safari', 'internet', 'web',
            'email', 'mail', 'message', 'chat', 'social', 'facebook', 'twitter',
            'install', 'download', 'delete', 'remove', 'system', 'terminal',
            'password', 'login', 'account', 'financial', 'bank', 'purchase'
        ]
        
        has_blocked_keyword = any(keyword in user_lower for keyword in blocked_keywords)
        
        return has_orcasheets_keyword and not has_blocked_keyword
    
    def validate_and_execute(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and execute a task directly."""
        try:
            # Create task
            task_enum = TaskType(task_type)
            task = OrcaSheetsTask(task_type=task_enum, parameters=parameters)
            
            # Validate
            if not task.validate():
                return {
                    "success": False,
                    "error": "Task validation failed"
                }
            
            # Execute
            result = self.orcasheets_tool(
                task_type=task_type,
                parameters=parameters
            )
            
            return {
                "success": not result.error,
                "output": result.output,
                "error": result.error,
                "screenshot": result.base64_image
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }