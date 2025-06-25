from .base import BaseAction
from tools.computer import ComputerTool
from tools.orcasheets.vision.ocr import find_text_location
import asyncio
import base64
import tempfile

class NewProjectAction(BaseAction):
    def __init__(self, computer: ComputerTool):
        super().__init__(computer)

    async def run(self, file_path: str):
        print(f"[DEBUG] Starting new project creation with file: {file_path}")
        
        # Step 1: Ensure OrcaSheets is active and find NEW PROJECT button
        print("[DEBUG] Ensuring OrcaSheets is active")
        
        # Try keyboard shortcut first (most reliable)
        print("[DEBUG] Trying keyboard shortcut Cmd+N for New Project")
        await self.computer(action="key", text="command+n")
        await asyncio.sleep(2)
        
        # Take screenshot to see if a dropdown or dialog appeared
        screenshot_result = await self.computer(action="screenshot")
        if not screenshot_result.base64_image:
            return {"status": "screenshot_failed"}
            
        img_bytes = base64.b64decode(screenshot_result.base64_image)
        with tempfile.NamedTemporaryFile(suffix="_after_shortcut.png", delete=False) as f:
            f.write(img_bytes)
            screenshot_path = f.name
        
        # Check if we can see "Open files" option after the shortcut
        open_files_coords = find_text_location(screenshot_path, "Open files")
        if open_files_coords:
            print(f"[DEBUG] Keyboard shortcut worked! Found 'Open files' at {open_files_coords}")
        else:
            # Fallback: try to find and click NEW PROJECT button manually
            print("[DEBUG] Keyboard shortcut didn't work, looking for NEW PROJECT button")
            new_project_coords = find_text_location(screenshot_path, "NEW PROJECT")
            if not new_project_coords:
                return {"status": "new_project_button_not_found", "screenshot": screenshot_path}
            
            print(f"[DEBUG] Clicking NEW PROJECT button at {new_project_coords}")
            await self.computer(action="mouse_move", coordinate=list(new_project_coords))
            await asyncio.sleep(0.5)
            await self.computer(action="left_click")
            await asyncio.sleep(2)  # Wait for dropdown to appear
        
        # Step 2: Find and click "Open files" option
        if not open_files_coords:
            # Take another screenshot to find "Open files" option if we didn't find it already
            print("[DEBUG] Taking screenshot to find Open files option")
            dropdown_screenshot = await self.computer(action="screenshot")
            if not dropdown_screenshot.base64_image:
                return {"status": "dropdown_screenshot_failed"}
                
            img_bytes = base64.b64decode(dropdown_screenshot.base64_image)
            with tempfile.NamedTemporaryFile(suffix="_dropdown.png", delete=False) as f:
                f.write(img_bytes)
                dropdown_path = f.name
            
            # Find "Open files" option using OCR
            open_files_coords = find_text_location(dropdown_path, "Open files")
            if not open_files_coords:
                # Try alternative text patterns
                open_files_coords = find_text_location(dropdown_path, "files")
                if not open_files_coords:
                    return {"status": "open_files_option_not_found", "screenshot": dropdown_path}
        
        print(f"[DEBUG] Clicking 'Open files' option at {open_files_coords}")
        await self.computer(action="mouse_move", coordinate=list(open_files_coords))
        await asyncio.sleep(0.5)
        await self.computer(action="left_click")
        await asyncio.sleep(2)  # Wait for file dialog to open
        
        # Step 3: Type file path in file dialog
        print(f"[DEBUG] Typing file path: {file_path}")
        await self.type_text(file_path)
        await asyncio.sleep(0.5)
        
        # Step 4: Press Enter to submit
        print("[DEBUG] Pressing Enter to submit")
        await self.press_key("Return")
        await asyncio.sleep(3)  # Wait for file to upload
        
        return {"status": "file_uploaded_to_new_project", "file": file_path} 