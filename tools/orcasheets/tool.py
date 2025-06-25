from tools.computer import ComputerTool
from .actions.base import BaseAction
from typing import Dict, Type, Any, Optional
from .actions.select_project import SelectProjectAction
from .actions.upload_file import UploadFileAction
from .actions.new_project import NewProjectAction
from .actions.open_orcasheets import OpenOrcaSheetsAction

class OrcaSheetsTool:
    """
    Main entry point for OrcaSheets automation tasks.
    Use run_task(task_name, **kwargs) to execute a workflow.
    Easily extensible: register new actions in the _actions dict.
    """
    _actions: Dict[str, Type[BaseAction]] = {}

    def __init__(self):
        self.computer = ComputerTool()

    @classmethod
    def register_action(cls, name: str, action_cls: Type[BaseAction]):
        cls._actions[name] = action_cls

    async def run_task(self, task_name: str, **kwargs) -> Any:
        action_cls = self._actions.get(task_name)
        if not action_cls:
            raise ValueError(f"Unknown task: {task_name}")
        action = action_cls(self.computer)
        return await action.run(**kwargs)

    async def run_workflow(self, prompt: str, file_path: str, project_name: Optional[str] = None) -> Any:
        """
        High-level workflow runner based on user prompt.
        Handles:
        1. Open OrcaSheets and select existing project and upload file  
        2. Open OrcaSheets and upload file as new project (default behavior)
        """
        prompt_lower = prompt.lower()
        
        # Check if user wants to upload to existing project
        if project_name and ("select" in prompt_lower):
            # Workflow 1: open, search/select existing project, upload to existing project  
            await self.run_task("open_orcasheets")
            select_result = await self.run_task("select_project", project_name=project_name)
            
            # Check if project selection was successful
            if select_result.get("status") == "project_selected":
                return await self.run_task("upload_file", file_path=file_path, project_name=project_name)
            else:
                # Project selection failed, return the error
                return select_result
        else:
            # Workflow 2: open, create new project via upload (default behavior)
            await self.run_task("open_orcasheets")
            return await self.run_task("new_project", file_path=file_path)

OrcaSheetsTool.register_action("select_project", SelectProjectAction)
OrcaSheetsTool.register_action("upload_file", UploadFileAction)
OrcaSheetsTool.register_action("new_project", NewProjectAction)
OrcaSheetsTool.register_action("open_orcasheets", OpenOrcaSheetsAction) 