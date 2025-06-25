from .base import BaseAction
from tools.computer import ComputerTool
from tools.orcasheets.vision.image_match import find_template_in_screenshot
from typing import Optional
import asyncio
import base64
import tempfile
import os

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../vision/templates')
ADD_NEW_SHEET_TEMPLATE = os.path.abspath(os.path.join(TEMPLATES_DIR, 'add_new_sheet.png'))

class UploadFileAction(BaseAction):
    def __init__(self, computer: ComputerTool):
        super().__init__(computer)

    async def run(self, file_path: str, project_name: Optional[str] = None):
        # Take a screenshot to find the 'Add New Sheet' button
        screenshot_result = await self.computer(action="screenshot")
        if not screenshot_result.base64_image:
            raise RuntimeError("No screenshot image returned.")
        img_bytes = base64.b64decode(screenshot_result.base64_image)
        with tempfile.NamedTemporaryFile(suffix="_add_new_sheet.png", delete=False) as f:
            f.write(img_bytes)
            screenshot_path = f.name
        add_new_sheet_coords = find_template_in_screenshot(screenshot_path, ADD_NEW_SHEET_TEMPLATE)
        if not add_new_sheet_coords:
            return {"status": "add_new_sheet_not_found", "screenshot": screenshot_path}
        # Click on 'Add New Sheet' or '+'
        await self.computer(action="mouse_move", coordinate=list(add_new_sheet_coords))
        await asyncio.sleep(0.5)
        await self.computer(action="left_click")
        await asyncio.sleep(1)
        # In the file dialog, type the file path and press Enter
        await self.type_text(file_path)
        await asyncio.sleep(0.5)
        await self.press_key("Return")
        await asyncio.sleep(1)
        return {"status": "file_uploaded", "file": file_path, "project": project_name} 