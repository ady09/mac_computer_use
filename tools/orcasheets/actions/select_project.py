from .base import BaseAction
from tools.computer import ComputerTool
from tools.orcasheets.vision.ocr import extract_text_from_image
from tools.orcasheets.vision.image_match import find_template_in_screenshot
from typing import Optional
import asyncio
import base64
import tempfile
import os

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../vision/templates')
SEARCH_BAR_TEMPLATE = os.path.abspath(os.path.join(TEMPLATES_DIR, 'search_bar.png'))
PROJECT_LIST_TEMPLATE = os.path.abspath(os.path.join(TEMPLATES_DIR, 'project_list.png'))

class SelectProjectAction(BaseAction):
    def __init__(self, computer: ComputerTool):
        super().__init__(computer)

    async def run(self, project_name: Optional[str] = None):
        if not project_name:
            return {"status": "no_project_name_provided"}
        # Take a screenshot after opening OrcaSheets
        pre_click_screenshot = await self.computer(action="screenshot")
        if not pre_click_screenshot.base64_image:
            raise RuntimeError("No screenshot image returned.")
        img_bytes = base64.b64decode(pre_click_screenshot.base64_image)
        with tempfile.NamedTemporaryFile(suffix="_pre_click.png", delete=False) as f:
            f.write(img_bytes)
            pre_click_img_path = f.name
        # Find search bar in screenshot
        search_bar_coords = find_template_in_screenshot(pre_click_img_path, SEARCH_BAR_TEMPLATE)
        if not search_bar_coords:
            return {"status": "search_bar_not_found", "screenshot": pre_click_img_path}
        # Click on the search bar
        await self.computer(action="mouse_move", coordinate=list(search_bar_coords))
        await asyncio.sleep(0.5)
        await self.computer(action="left_click")
        await asyncio.sleep(0.5)
        # Type the project name
        await self.type_text(project_name)
        await asyncio.sleep(1)
        # Take a screenshot of the project list
        screenshot_result = await self.computer(action="screenshot")
        if not screenshot_result.base64_image:
            raise RuntimeError("No screenshot image returned.")
        img_bytes = base64.b64decode(screenshot_result.base64_image)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(img_bytes)
            img_path = f.name
        # Find project list in screenshot
        project_list_coords = find_template_in_screenshot(img_path, PROJECT_LIST_TEMPLATE)
        if project_list_coords:
            # Click on the project in the list (center of detected area)
            await self.computer(action="mouse_move", coordinate=list(project_list_coords))
            await asyncio.sleep(0.5)
            await self.computer(action="left_click")
            await asyncio.sleep(1)
            return {"status": "selected", "project": project_name, "pre_click_screenshot": pre_click_img_path}
        else:
            # Fallback: OCR to check if project name is present
            text = extract_text_from_image(img_path) if img_path else ""
            return {"status": "not_found", "project": project_name, "ocr_text": text, "pre_click_screenshot": pre_click_img_path} 