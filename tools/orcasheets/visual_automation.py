"""
Visual-only OrcaSheets automation using AI-powered screen analysis.
No hardcoded coordinates - everything is found dynamically.
"""

import asyncio
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import base64

from ..computer import ComputerTool
from ..base import ToolResult
from .core.visual_ai import VisualAI
from .core.applescript_helper import AppleScriptHelper
from .core.task_parser import TaskParser, ParsedTask


class VisualOrcaSheetsAutomation:
    """
    Advanced OrcaSheets automation using only visual analysis.
    No hardcoded coordinates - finds all elements dynamically.
    """
    
    def __init__(self):
        self.computer = ComputerTool()
        self.visual_ai = VisualAI()
        self.applescript = AppleScriptHelper()
        self.task_parser = TaskParser()
        self.wait_time = 2.0
        self.max_retries = 3
        
    async def _wait(self, seconds: Optional[float] = None):
        """Wait for specified time or default wait time"""
        await asyncio.sleep(seconds or self.wait_time)
        
    async def _take_screenshot(self) -> ToolResult:
        """Take a screenshot and return the result"""
        return await self.computer(action="screenshot")
    
    async def execute_command(self, command: str) -> bool:
        """
        Execute a natural language command using visual analysis.
        
        Examples:
        - "open orcasheets and upload industry.csv from downloads"
        - "select default project and close industry.csv tab"
        - "click add new sheet button"
        """
        print(f"🎯 Executing command: '{command}'")
        
        try:
            # Parse the command into structured tasks
            tasks = self.task_parser.parse_command(command)
            
            if not tasks:
                print("❌ Could not parse command")
                return False
            
            print(f"📋 Parsed into {len(tasks)} tasks:")
            for i, task in enumerate(tasks, 1):
                print(f"   {i}. {task.description}")
            
            # Convert tasks to execution plan
            execution_plan = self.task_parser.tasks_to_execution_plan(tasks)
            
            # Execute each step in the plan
            for i, step in enumerate(execution_plan, 1):
                print(f"\n🔄 Step {i}/{len(execution_plan)}: {step['description']}")
                
                success = await self._execute_step(step)
                if not success:
                    print(f"❌ Step {i} failed: {step['description']}")
                    return False
                
                # Wait between steps
                await self._wait(1.0)
            
            print("✅ Command executed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Command execution failed: {e}")
            return False
    
    async def _execute_step(self, step: Dict[str, Any]) -> bool:
        """Execute a single step in the execution plan"""
        method = step['method']
        parameters = step.get('parameters', {})
        
        if method == 'open_application':
            return await self._open_application(parameters.get('app_name', 'OrcaSheets'))
        
        elif method == 'find_and_click':
            return await self._find_and_click_element(
                description=parameters.get('description', ''),
                search_terms=parameters.get('search_terms', [])
            )
        
        elif method == 'upload_file':
            return await self._upload_file(
                file_path=parameters.get('file_path', ''),
                filename=parameters.get('filename', '')
            )
        
        elif method == 'close_tab':
            return await self._close_tab(
                tab_name=parameters.get('tab_name', ''),
                search_terms=parameters.get('search_terms', [])
            )
        
        else:
            print(f"❌ Unknown method: {method}")
            return False
    
    async def _open_application(self, app_name: str) -> bool:
        """Open an application using Spotlight"""
        print(f"📱 Opening {app_name}...")
        
        try:
            # Method 1: Try AppleScript first
            is_running = await self.applescript.is_application_running(app_name)
            if is_running:
                print(f"✅ {app_name} is already running")
                success = await self.applescript.open_application(app_name)
                if success:
                    await self._wait(2.0)
                    return True
            
            # Method 2: Use Spotlight
            print(f"🔍 Using Spotlight to open {app_name}...")
            
            # Open Spotlight (Cmd+Space)
            await self.computer(action="key", text="cmd+space")
            await self._wait(1.0)
            
            # Type app name
            await self.computer(action="type", text=app_name)
            await self._wait(1.0)
            
            # Press Enter
            await self.computer(action="key", text="Return")
            await self._wait(3.0)  # Wait for app to launch
            
            print(f"✅ {app_name} opened via Spotlight")
            return True
            
        except Exception as e:
            print(f"❌ Failed to open {app_name}: {e}")
            return False
    
    async def _find_and_click_element(self, description: str, search_terms: List[str]) -> bool:
        """Find and click an element using visual analysis"""
        print(f"🔍 Looking for: {description}")
        
        # Take screenshot for analysis
        screenshot = await self._take_screenshot()
        if not screenshot.base64_image:
            print("❌ Could not take screenshot")
            return False
        
        # Try multiple search terms
        all_search_terms = [description] + search_terms
        
        for attempt in range(self.max_retries):
            print(f"🔄 Attempt {attempt + 1}/{self.max_retries}")
            
            # Method 1: Try AppleScript text detection first
            for search_term in all_search_terms:
                print(f"  🎯 AppleScript: '{search_term}'")
                success = await self.applescript.find_and_click_text("OrcaSheets", search_term)
                if success:
                    print(f"✅ Found and clicked '{search_term}' using AppleScript")
                    return True
            
            # Method 2: Use visual AI
            for search_term in all_search_terms:
                print(f"  🔍 Visual AI: '{search_term}'")
                success = await self.visual_ai.find_and_click_element(
                    self.computer, screenshot.base64_image, search_term
                )
                if success:
                    print(f"✅ Found and clicked '{search_term}' using Visual AI")
                    return True
            
            # If not found, wait and take a new screenshot
            if attempt < self.max_retries - 1:
                print("  ⏳ Element not found, waiting and retrying...")
                await self._wait(2.0)
                screenshot = await self._take_screenshot()
                if not screenshot.base64_image:
                    print("❌ Could not take screenshot for retry")
                    return False
        
        print(f"❌ Could not find element: {description}")
        return False
    
    async def _upload_file(self, file_path: str, filename: str) -> bool:
        """Handle file upload after file dialog opens"""
        print(f"📎 Uploading file: {file_path}")
        
        try:
            # Wait for file dialog to open
            await self._wait(2.0)
            
            # Method 1: Try AppleScript file selection
            success = await self.applescript.select_file_in_dialog(file_path)
            if success:
                print("✅ File selected using AppleScript")
                return True
            
            # Method 2: Use keyboard navigation
            print("🔄 Using keyboard navigation for file upload...")
            
            # Use Cmd+Shift+G to go to folder
            await self.computer(action="key", text="cmd+shift+g")
            await self._wait(1.0)
            
            # Type the directory path
            file_obj = Path(file_path).expanduser()
            directory_path = str(file_obj.parent)
            await self.computer(action="type", text=directory_path)
            await self.computer(action="key", text="Return")
            await self._wait(1.0)
            
            # Type filename to select it
            await self.computer(action="type", text=file_obj.name)
            await self._wait(0.5)
            
            # Press Enter or click Open
            await self.computer(action="key", text="Return")
            await self._wait(2.0)
            
            print(f"✅ File uploaded: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ File upload failed: {e}")
            return False
    
    async def _close_tab(self, tab_name: str, search_terms: List[str]) -> bool:
        """Close a specific tab using visual analysis"""
        print(f"🗙 Closing tab: {tab_name}")
        
        # Take screenshot for analysis
        screenshot = await self._take_screenshot()
        if not screenshot.base64_image:
            print("❌ Could not take screenshot")
            return False
        
        # Try to find and close the tab
        all_search_terms = [f"{tab_name} tab", f"close {tab_name}"] + search_terms
        
        for attempt in range(self.max_retries):
            print(f"🔄 Attempt {attempt + 1}/{self.max_retries}")
            
            # Method 1: Look for tab close button specifically
            close_button_terms = [
                f"{tab_name} close button",
                f"{tab_name} tab close",
                f"close {tab_name}",
                f"{tab_name} x button"
            ]
            
            for search_term in close_button_terms:
                print(f"  🎯 Looking for: '{search_term}'")
                coords = await self.visual_ai.find_element_by_description(
                    screenshot.base64_image, search_term
                )
                if coords:
                    await self.computer(action="mouse_move", coordinate=[coords[0], coords[1]])
                    await self.computer(action="left_click")
                    print(f"✅ Closed tab using close button")
                    return True
            
            # Method 2: Right-click on tab for context menu
            for search_term in [f"{tab_name} tab", tab_name]:
                print(f"  🖱️  Right-clicking: '{search_term}'")
                coords = await self.visual_ai.find_element_by_description(
                    screenshot.base64_image, search_term
                )
                if coords:
                    # Right-click on tab
                    await self.computer(action="mouse_move", coordinate=[coords[0], coords[1]])
                    await self.computer(action="right_click")
                    await self._wait(0.5)
                    
                    # Look for "Close" in context menu
                    close_coords = await self.visual_ai.find_element_by_description(
                        screenshot.base64_image, "close"
                    )
                    if close_coords:
                        await self.computer(action="mouse_move", coordinate=[close_coords[0], close_coords[1]])
                        await self.computer(action="left_click")
                        print(f"✅ Closed tab using context menu")
                        return True
            
            # Method 3: Try AppleScript
            for search_term in all_search_terms:
                print(f"  🎯 AppleScript: '{search_term}'")
                success = await self.applescript.find_and_click_text("OrcaSheets", search_term)
                if success:
                    print(f"✅ Closed tab using AppleScript")
                    return True
            
            # If not found, wait and retry
            if attempt < self.max_retries - 1:
                print("  ⏳ Tab not found, waiting and retrying...")
                await self._wait(2.0)
                screenshot = await self._take_screenshot()
        
        print(f"❌ Could not close tab: {tab_name}")
        return False
    
    async def analyze_current_screen(self) -> Dict[str, Any]:
        """Analyze the current screen and return detected elements"""
        print("🔍 Analyzing current screen...")
        
        screenshot = await self._take_screenshot()
        if not screenshot.base64_image:
            return {"error": "Could not take screenshot"}
        
        # Get all detected elements
        elements = await self.visual_ai.analyze_screen_elements(screenshot.base64_image)
        
        # Get clickable elements via AppleScript
        try:
            clickable_elements = await self.applescript.get_clickable_elements("OrcaSheets")
            elements["applescript_elements"] = clickable_elements
        except Exception as e:
            print(f"⚠️  Could not get AppleScript elements: {e}")
            elements["applescript_elements"] = []
        
        return elements
    
    async def take_debug_screenshot(self, filename: str = "visual_debug.png") -> ToolResult:
        """Take a screenshot for debugging purposes"""
        screenshot = await self._take_screenshot()
        if screenshot.base64_image:
            image_data = base64.b64decode(screenshot.base64_image)
            with open(filename, 'wb') as f:
                f.write(image_data)
            print(f"🖼️  Debug screenshot saved as {filename}")
        return screenshot


# Convenience function for easy usage
async def execute_visual_command(command: str) -> bool:
    """
    Execute a visual command using the new coordinate-free system.
    
    Examples:
    - "open orcasheets and upload industry.csv from downloads"
    - "select default project and close industry.csv tab"
    - "click add new sheet button"
    """
    automation = VisualOrcaSheetsAutomation()
    return await automation.execute_command(command)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Example commands
    commands = [
        "open orcasheets and upload industry.csv from downloads",
        "select default project and close industry.csv tab",
        "click add new sheet button"
    ]
    
    async def test_commands():
        for command in commands:
            print(f"\n{'='*60}")
            print(f"Testing: {command}")
            print('='*60)
            
            success = await execute_visual_command(command)
            print(f"Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Uncomment to run tests
    # asyncio.run(test_commands())