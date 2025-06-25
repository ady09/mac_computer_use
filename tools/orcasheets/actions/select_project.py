from .base import BaseAction
from tools.computer import ComputerTool
from tools.orcasheets.vision.ocr import find_text_location, extract_text_from_image
from typing import Optional
import asyncio
import base64
import tempfile

class SelectProjectAction(BaseAction):
    def __init__(self, computer: ComputerTool):
        super().__init__(computer)

    async def run(self, project_name: Optional[str] = None):
        if not project_name:
            return {"status": "no_project_name_provided"}
            
        print(f"[DEBUG] Selecting project: {project_name}")
        
        # Step 1: Take screenshot and find search bar
        print("[DEBUG] Looking for search bar")
        screenshot = await self.computer(action="screenshot")
        if not screenshot.base64_image:
            return {"status": "screenshot_failed"}
            
        img_bytes = base64.b64decode(screenshot.base64_image)
        with tempfile.NamedTemporaryFile(suffix="_search.png", delete=False) as f:
            f.write(img_bytes)
            screenshot_path = f.name
        
        # First try to find the project directly in the current view
        direct_project_coords = find_text_location(screenshot_path, project_name)
        if direct_project_coords:
            print(f"[DEBUG] Found project '{project_name}' directly at {direct_project_coords}")
            await self.computer(action="mouse_move", coordinate=list(direct_project_coords))
            await asyncio.sleep(0.5)
            await self.computer(action="left_click")
            await asyncio.sleep(2)  # Wait for project to load
            return {"status": "project_selected", "project": project_name}
        
        # If not found directly, try to find search bar
        search_bar_coords = find_text_location(screenshot_path, "Search projects")
        if not search_bar_coords:
            # Try alternative text
            search_bar_coords = find_text_location(screenshot_path, "Search")
            if not search_bar_coords:
                return {"status": "search_bar_not_found", "screenshot": screenshot_path}
        
        # Step 2: Click on search bar and type project name
        print(f"[DEBUG] Clicking search bar at {search_bar_coords}")
        await self.computer(action="mouse_move", coordinate=list(search_bar_coords))
        await asyncio.sleep(0.5)
        await self.computer(action="left_click")
        await asyncio.sleep(0.5)
        
        # Clear any existing text and type the project name
        await self.computer(action="key", text="command+a")  # Select all
        await asyncio.sleep(0.2)
        await self.type_text(project_name)
        await asyncio.sleep(1)
        
        # Step 3: Take screenshot after typing to find the project in results
        print("[DEBUG] Looking for project in search results")
        results_screenshot = await self.computer(action="screenshot")
        if not results_screenshot.base64_image:
            return {"status": "results_screenshot_failed"}
            
        img_bytes = base64.b64decode(results_screenshot.base64_image)
        with tempfile.NamedTemporaryFile(suffix="_results.png", delete=False) as f:
            f.write(img_bytes)
            results_path = f.name
        
        # Find the project name in the results
        project_coords = find_text_location(results_path, project_name)
        if not project_coords:
            # Try to find just "default" if that's what we're looking for
            if project_name.lower() == "default":
                project_coords = find_text_location(results_path, "default")
            if not project_coords:
                return {"status": "project_not_found", "project": project_name, "screenshot": results_path}
        
        # Step 4: Click on the found project
        print(f"[DEBUG] Clicking on project '{project_name}' at {project_coords}")
        await self.computer(action="mouse_move", coordinate=list(project_coords))
        await asyncio.sleep(0.5)
        await self.computer(action="left_click")
        await asyncio.sleep(2)  # Wait for project to load
        
        return {"status": "project_selected", "project": project_name} 