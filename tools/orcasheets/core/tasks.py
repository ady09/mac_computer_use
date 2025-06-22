from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio


class OrcaSheetsTask(ABC):
    """Base class for all OrcaSheets automation tasks"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    async def execute(self, automation_instance, **kwargs) -> bool:
        """Execute the task with the given automation instance"""
        pass
        
    @abstractmethod
    def validate_params(self, **kwargs) -> bool:
        """Validate the parameters for this task"""
        pass


class OpenAppTask(OrcaSheetsTask):
    """Task to open OrcaSheets application"""
    
    def __init__(self):
        super().__init__("open_app", "Open OrcaSheets application using Spotlight")
        
    def validate_params(self, **kwargs) -> bool:
        # No parameters needed for this task
        return True
        
    async def execute(self, automation_instance, **kwargs) -> bool:
        """Open OrcaSheets application"""
        try:
            await automation_instance.search_and_open_app("OrcaSheets")
            await automation_instance.wait_for_app_launch()
            return True
        except Exception as e:
            print(f"Failed to open app: {e}")
            return False


class SelectProjectTask(OrcaSheetsTask):
    """Task to select a project"""
    
    def __init__(self):
        super().__init__("select_project", "Select a project from the project list")
        
    def validate_params(self, **kwargs) -> bool:
        # project_name is optional, defaults to "default"
        return True
        
    async def execute(self, automation_instance, **kwargs) -> bool:
        """Select a project"""
        try:
            project_name = kwargs.get("project_name", "default")
            await automation_instance.select_project(project_name)
            return True
        except Exception as e:
            print(f"Failed to select project: {e}")
            return False


class UploadFileTask(OrcaSheetsTask):
    """Task to upload a file"""
    
    def __init__(self):
        super().__init__("upload_file", "Upload a file to OrcaSheets")
        
    def validate_params(self, **kwargs) -> bool:
        return "file_path" in kwargs and kwargs["file_path"] is not None
        
    async def execute(self, automation_instance, **kwargs) -> bool:
        """Upload a file"""
        try:
            file_path = kwargs["file_path"]
            await automation_instance.add_new_sheet()
            await automation_instance.upload_file(file_path)
            return True
        except Exception as e:
            print(f"Failed to upload file: {e}")
            return False


class TaskRegistry:
    """Registry for managing OrcaSheets automation tasks"""
    
    def __init__(self):
        self._tasks: Dict[str, OrcaSheetsTask] = {}
        self._register_default_tasks()
        
    def _register_default_tasks(self):
        """Register default tasks"""
        self.register_task(OpenAppTask())
        self.register_task(SelectProjectTask())
        self.register_task(UploadFileTask())
        
    def register_task(self, task: OrcaSheetsTask):
        """Register a new task"""
        self._tasks[task.name] = task
        
    def get_task(self, name: str) -> Optional[OrcaSheetsTask]:
        """Get a task by name"""
        return self._tasks.get(name)
        
    def list_tasks(self) -> List[str]:
        """List all available task names"""
        return list(self._tasks.keys())
        
    def get_task_info(self, name: str) -> Optional[Dict[str, str]]:
        """Get task information"""
        task = self._tasks.get(name)
        if task:
            return {
                "name": task.name,
                "description": task.description
            }
        return None
        
    async def execute_task(self, task_name: str, automation_instance, **kwargs) -> bool:
        """Execute a task by name"""
        task = self.get_task(task_name)
        if not task:
            print(f"Task '{task_name}' not found")
            return False
            
        if not task.validate_params(**kwargs):
            print(f"Invalid parameters for task '{task_name}'")
            return False
            
        return await task.execute(automation_instance, **kwargs)
        
    async def execute_workflow(self, task_names: List[str], automation_instance, **kwargs) -> bool:
        """Execute multiple tasks in sequence"""
        for task_name in task_names:
            success = await self.execute_task(task_name, automation_instance, **kwargs)
            if not success:
                print(f"Workflow failed at task: {task_name}")
                return False
        return True


# Predefined workflows
WORKFLOWS = {
    "upload_file": ["open_app", "select_project", "upload_file"],
    "open_project": ["open_app", "select_project"],
    "open_app_only": ["open_app"]
}