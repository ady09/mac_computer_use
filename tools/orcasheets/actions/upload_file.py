from .base import BaseAction
from tools.computer import ComputerTool
from tools.orcasheets.vision.ocr import find_text_location
from typing import Optional
import asyncio
import base64
import tempfile

class UploadFileAction(BaseAction):
    def __init__(self, computer: ComputerTool):
        super().__init__(computer)

    async def run(self, file_path: str, project_name: Optional[str] = None):
        print(f"[DEBUG] Uploading file {file_path} to project {project_name}")
        
        # Step 1: Take screenshot and find 'Add New Sheet' button or '+' button
        print("[DEBUG] Looking for Add New Sheet button")
        screenshot_result = await self.computer(action="screenshot")
        if not screenshot_result.base64_image:
            return {"status": "screenshot_failed"}
            
        img_bytes = base64.b64decode(screenshot_result.base64_image)
        with tempfile.NamedTemporaryFile(suffix="_upload.png", delete=False) as f:
            f.write(img_bytes)
            screenshot_path = f.name
        
        # Look for "Add New Sheet" text or similar
        add_sheet_coords = find_text_location(screenshot_path, "Add New Sheet")
        if not add_sheet_coords:
            # Try alternatives
            add_sheet_coords = find_text_location(screenshot_path, "Add")
            if not add_sheet_coords:
                add_sheet_coords = find_text_location(screenshot_path, "+")
                if not add_sheet_coords:
                    return {"status": "add_new_sheet_not_found", "screenshot": screenshot_path}
        
        # Step 2: Click on the Add New Sheet button
        print(f"[DEBUG] Clicking Add New Sheet button at {add_sheet_coords}")
        await self.computer(action="mouse_move", coordinate=list(add_sheet_coords))
        await asyncio.sleep(0.5)
        await self.computer(action="left_click")
        await asyncio.sleep(2)  # Wait for file dialog to open
        
        # Step 3: Type file path in the file dialog
        print(f"[DEBUG] Typing file path: {file_path}")
        await self.type_text(file_path)
        await asyncio.sleep(0.5)
        
        # Step 4: Press Enter to submit
        print("[DEBUG] Pressing Enter to submit")
        await self.press_key("Return")
        await asyncio.sleep(2)  # Wait for file to upload
        
        return {"status": "file_uploaded", "file": file_path, "project": project_name} 