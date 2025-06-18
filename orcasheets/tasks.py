"""
Task definitions and validation for OrcaSheets automation.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import re


class TaskType(Enum):
    """Supported OrcaSheets task types."""
    OPEN_ORCASHEETS = "open_orcasheets"
    UPLOAD_FILE = "upload_file"
    SELECT_PROJECT = "select_project"
    ADD_NEW_SHEET = "add_new_sheet"
    COMBINED_OPEN_AND_UPLOAD = "combined_open_and_upload"


@dataclass
class OrcaSheetsTask:
    """Represents a task to be performed in OrcaSheets."""
    task_type: TaskType
    parameters: Dict[str, Any]
    
    def validate(self) -> bool:
        """Validate task parameters."""
        return TaskValidator.validate_task(self)


class TaskValidator:
    """Validates OrcaSheets tasks and ensures they are safe."""
    
    ALLOWED_TASK_TYPES = {
        TaskType.OPEN_ORCASHEETS,
        TaskType.UPLOAD_FILE,
        TaskType.SELECT_PROJECT,
        TaskType.ADD_NEW_SHEET,
        TaskType.COMBINED_OPEN_AND_UPLOAD
    }
    
    ALLOWED_FILE_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.txt'}
    
    @classmethod
    def validate_task(cls, task: OrcaSheetsTask) -> bool:
        """Validate that a task is allowed and safe."""
        if task.task_type not in cls.ALLOWED_TASK_TYPES:
            return False
        
        if task.task_type == TaskType.UPLOAD_FILE:
            return cls._validate_upload_task(task.parameters)
        elif task.task_type == TaskType.SELECT_PROJECT:
            return cls._validate_project_task(task.parameters)
        elif task.task_type == TaskType.COMBINED_OPEN_AND_UPLOAD:
            return cls._validate_combined_task(task.parameters)
        
        return True
    
    @classmethod
    def _validate_upload_task(cls, params: Dict[str, Any]) -> bool:
        """Validate file upload task parameters."""
        file_path = params.get('file_path', '')
        if not file_path:
            return False
        
        # Check file extension
        file_ext = '.' + file_path.split('.')[-1].lower()
        if file_ext not in cls.ALLOWED_FILE_EXTENSIONS:
            return False
        
        # Ensure file is in allowed directories (Downloads, Documents, Desktop)
        allowed_dirs = ['Downloads', 'Documents', 'Desktop']
        if not any(allowed_dir in file_path for allowed_dir in allowed_dirs):
            return False
        
        return True
    
    @classmethod
    def _validate_project_task(cls, params: Dict[str, Any]) -> bool:
        """Validate project selection task parameters."""
        project_name = params.get('project_name', '')
        # Allow alphanumeric, spaces, and common project characters
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', project_name):
            return False
        return True
    
    @classmethod
    def _validate_combined_task(cls, params: Dict[str, Any]) -> bool:
        """Validate combined open and upload task."""
        return (cls._validate_upload_task(params) and 
                cls._validate_project_task(params))
    
    @classmethod
    def parse_user_request(cls, user_input: str) -> Optional[OrcaSheetsTask]:
        """Parse user input and create appropriate task."""
        user_input = user_input.lower().strip()
        
        # Pattern for combined open and upload task
        combined_pattern = r'open orcasheets.*upload\s+(\S+\.(?:csv|xlsx|xls|json|txt))\s+from\s+(\w+)'
        match = re.search(combined_pattern, user_input)
        if match:
            filename = match.group(1)
            folder = match.group(2)
            
            # Extract project name if mentioned
            project_match = re.search(r'project\s+([a-zA-Z0-9\s\-_\.]+)', user_input)
            project_name = project_match.group(1) if project_match else None
            
            return OrcaSheetsTask(
                task_type=TaskType.COMBINED_OPEN_AND_UPLOAD,
                parameters={
                    'file_path': f'~/{folder.title()}/{filename}',
                    'project_name': project_name
                }
            )
        
        # Pattern for just opening OrcaSheets
        if 'open orcasheets' in user_input:
            return OrcaSheetsTask(
                task_type=TaskType.OPEN_ORCASHEETS,
                parameters={}
            )
        
        # Pattern for file upload only
        upload_pattern = r'upload\s+(\S+\.(?:csv|xlsx|xls|json|txt))\s+from\s+(\w+)'
        match = re.search(upload_pattern, user_input)
        if match:
            filename = match.group(1)
            folder = match.group(2)
            return OrcaSheetsTask(
                task_type=TaskType.UPLOAD_FILE,
                parameters={
                    'file_path': f'~/{folder.title()}/{filename}'
                }
            )
        
        return None