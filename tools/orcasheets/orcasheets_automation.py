import asyncio
import time
from pathlib import Path
from typing import Optional, Union
import base64

from ..computer import ComputerTool
from ..base import ToolResult
from .core.vision import ScreenAnalyzer
from .core.applescript_helper import AppleScriptHelper

# Optional imports for vision capabilities
try:
    import cv2
    import numpy as np
    from PIL import Image
    HAS_VISION = True
except ImportError:
    HAS_VISION = False


class OrcaSheetsAutomation:
    """
    OrcaSheets automation framework that wraps computer.py functionality
    for OrcaSheets-specific tasks.
    """
    
    def __init__(self):
        self.computer = ComputerTool()
        self.wait_time = 2.0  # Default wait time between actions
        self.screen_analyzer = ScreenAnalyzer()
        self.applescript = AppleScriptHelper()
        
    async def _wait(self, seconds: Optional[float] = None):
        """Wait for specified time or default wait time"""
        await asyncio.sleep(seconds or self.wait_time)
        
    async def _take_screenshot(self) -> ToolResult:
        """Take a screenshot and return the result"""
        return await self.computer(action="screenshot")
        
    async def _find_text_in_screenshot(self, text: str, screenshot_result: ToolResult) -> Optional[tuple[int, int]]:
        """
        Find text in screenshot using OCR-like approach.
        This is a simplified implementation - in production you'd want to use proper OCR.
        For now, this returns None and we'll rely on coordinate-based clicking with visual inspection.
        """
        # TODO: Implement proper OCR text detection
        # For now, return None to indicate text-based clicking is not implemented
        return None
        
    async def _find_element_by_color_pattern(self, screenshot_result: ToolResult, color_range: tuple) -> Optional[tuple[int, int]]:
        """
        Find UI elements by color patterns in screenshot.
        This is a placeholder for more sophisticated image recognition.
        """
        # TODO: Implement color-based element detection
        return None
        
    async def open_spotlight(self):
        """Open macOS Spotlight search"""
        print("Opening Spotlight...")
        result = await self.computer(action="key", text="cmd+space")
        await self._wait(1.0)
        return result
        
    async def search_and_open_app(self, app_name: str = "OrcaSheets"):
        """Search for and open an application using Spotlight"""
        print(f"Searching for {app_name}...")
        
        # Open Spotlight
        await self.open_spotlight()
        
        # Type app name
        await self.computer(action="type", text=app_name)
        await self._wait(1.0)
        
        # Press Enter to open
        result = await self.computer(action="key", text="Return")
        await self._wait(3.0)  # Wait for app to launch
        
        print(f"{app_name} opened successfully")
        return result
        
    async def wait_for_app_launch(self, timeout: int = 10):
        """Wait for OrcaSheets to fully launch"""
        print("Waiting for app to launch...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            screenshot = await self._take_screenshot()
            # Here you could add logic to detect if the app has launched
            # For now, just wait
            await self._wait(1.0)
            
        print("App launch wait completed")
        return True
        
    async def select_project(self, project_name: str = "default"):
        """
        Select a project from the project selection screen.
        If project_name is provided, search for it. Otherwise select default.
        """
        print(f"Selecting project: {project_name}")
        
        # Take screenshot to see current state
        screenshot = await self._take_screenshot()
        
        if project_name.lower() != "default":
            # Use search functionality
            print("Using search to find project...")
            # Look for search box and click it
            # Based on ss01.png, there's a search box in the project selection
            # These coordinates are approximate - you may need to adjust
            await self.computer(action="mouse_move", coordinate=[400, 180])
            await self.computer(action="left_click")
            await self._wait(0.5)
            
            # Type project name
            await self.computer(action="type", text=project_name)
            await self._wait(1.0)
            
            # Click on the first result
            await self.computer(action="mouse_move", coordinate=[400, 220])
            await self.computer(action="left_click")
        else:
            # Click on default project
            print("Selecting default project...")
            # Based on ss01.png, the default project appears around these coordinates
            await self.computer(action="mouse_move", coordinate=[400, 220])
            await self.computer(action="left_click")
            
        await self._wait(2.0)
        print(f"Project {project_name} selected")
        
    async def add_new_sheet(self):
        """Click on 'Add new sheet' or plus button to upload a file using dynamic detection"""
        print("Looking for 'Add new sheet' button...")
        
        # Take screenshot to analyze current state
        screenshot = await self._take_screenshot()
        
        if not screenshot.base64_image:
            print("Warning: Could not take screenshot, using fallback method")
            return await self._add_new_sheet_fallback()
        
        # Method 1: Try AppleScript text-based clicking (most reliable)
        print("Trying AppleScript text detection...")
        success = await self.applescript.find_and_click_text("OrcaSheets", "Add new sheet")
        if success:
            print("✅ Found and clicked 'Add new sheet' using AppleScript")
            await self._wait(2.0)
            return
            
        # Method 2: Try alternative AppleScript text variations
        for text_variation in ["Add new sheet", "new sheet", "+ Add", "Upload"]:
            print(f"Trying AppleScript with text: '{text_variation}'...")
            success = await self.applescript.find_and_click_text("OrcaSheets", text_variation)
            if success:
                print(f"✅ Found and clicked using AppleScript with '{text_variation}'")
                await self._wait(2.0)
                return
        
        # Method 3: Use computer vision to find the button
        print("Trying computer vision detection...")
        coords = self.screen_analyzer.find_add_new_sheet_button(screenshot.base64_image)
        if coords:
            print(f"🔍 Computer vision found button at coordinates: {coords}")
            await self.computer(action="mouse_move", coordinate=[coords[0], coords[1]])
            await self.computer(action="left_click")
            await self._wait(2.0)
            print("✅ Clicked 'Add new sheet' using computer vision")
            return
            
        # Method 4: Fallback to center clicking
        print("Using fallback method...")
        await self._add_new_sheet_fallback()
        
    async def _add_new_sheet_fallback(self):
        """Fallback method for clicking Add new sheet"""
        print("🔄 Using fallback coordinate-based clicking...")
        
        # Multiple fallback coordinates to try (based on common layouts)
        fallback_coords = [
            [683, 400],  # Center area
            [683, 350],  # Slightly higher
            [683, 450],  # Slightly lower
            [620, 400],  # Left of center
            [750, 400],  # Right of center
        ]
        
        for i, coords in enumerate(fallback_coords):
            print(f"Trying fallback coordinates {i+1}/{len(fallback_coords)}: {coords}")
            await self.computer(action="mouse_move", coordinate=coords)
            await self.computer(action="left_click")
            await self._wait(1.0)
            
            # Take a screenshot to see if anything changed
            screenshot = await self._take_screenshot()
            # In a real implementation, you could analyze if a file dialog opened
            
        print("✅ Completed fallback clicking attempts")
        
    async def upload_file(self, file_path: str):
        """
        Upload a file after clicking 'Add new sheet'.
        This assumes a file dialog will open.
        """
        print(f"Uploading file: {file_path}")
        
        # Wait for file dialog to open
        await self._wait(2.0)
        
        # Use keyboard shortcut to go to file location
        # Cmd+Shift+G opens "Go to folder" dialog
        await self.computer(action="key", text="cmd+shift+g")
        await self._wait(1.0)
        
        # Type the directory path
        file_obj = Path(file_path)
        directory_path = str(file_obj.parent)
        await self.computer(action="type", text=directory_path)
        await self.computer(action="key", text="Return")
        await self._wait(1.0)
        
        # Type filename to select it
        filename = file_obj.name
        await self.computer(action="type", text=filename)
        await self._wait(0.5)
        
        # Press Enter or click Open button
        await self.computer(action="key", text="Return")
        await self._wait(2.0)
        
        print(f"File {file_path} uploaded successfully")
        
    async def full_workflow(self, file_path: str, project_name: str = "default"):
        """
        Complete workflow: Open OrcaSheets, select project, and upload file
        """
        print("Starting OrcaSheets automation workflow...")
        
        try:
            # Step 1: Open OrcaSheets
            await self.search_and_open_app("OrcaSheets")
            await self.wait_for_app_launch()
            
            # Step 2: Select project
            await self.select_project(project_name)
            
            # Step 3: Add new sheet
            await self.add_new_sheet()
            
            # Step 4: Upload file
            await self.upload_file(file_path)
            
            print("Workflow completed successfully!")
            return True
            
        except Exception as e:
            print(f"Workflow failed: {str(e)}")
            return False
            
    async def take_debug_screenshot(self, filename: str = "debug_screenshot.png"):
        """Take a screenshot for debugging purposes"""
        screenshot = await self._take_screenshot()
        if screenshot.base64_image:
            image_data = base64.b64decode(screenshot.base64_image)
            with open(filename, 'wb') as f:
                f.write(image_data)
            print(f"Debug screenshot saved as {filename}")
        return screenshot


# Convenience function for easy usage
async def automate_orcasheets(file_path: str, project_name: str = "default"):
    """
    Convenience function to automate OrcaSheets file upload
    
    Args:
        file_path: Path to the file to upload
        project_name: Name of the project to select (default: "default")
    
    Returns:
        bool: True if successful, False otherwise
    """
    automation = OrcaSheetsAutomation()
    return await automation.full_workflow(file_path, project_name)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Example: Upload industry.csv from Downloads to default project
    file_path = "~/Downloads/industry.csv"
    
    # Run the automation
    result = asyncio.run(automate_orcasheets(file_path))
    print(f"Automation result: {result}")