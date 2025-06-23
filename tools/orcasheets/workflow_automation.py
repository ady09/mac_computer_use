"""
Workflow-aware OrcaSheets automation that follows the proper process flow.
Understands the OrcaSheets UI states and transitions between them correctly.
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


class WorkflowOrcaSheetsAutomation:
    """
    Workflow-aware OrcaSheets automation that follows proper UI flow.
    """
    
    def __init__(self):
        self.computer = ComputerTool()
        self.visual_ai = VisualAI()
        self.applescript = AppleScriptHelper()
        self.wait_time = 2.0
        self.max_retries = 3
        self.current_state = "unknown"
        
    async def _wait(self, seconds: Optional[float] = None):
        """Wait for specified time or default wait time"""
        await asyncio.sleep(seconds or self.wait_time)
        
    async def _take_screenshot(self) -> ToolResult:
        """Take a screenshot and return the result"""
        return await self.computer(action="screenshot")
    
    async def _detect_current_state(self) -> str:
        """
        Detect what screen/state OrcaSheets is currently in.
        Returns: 'project_selection', 'main_interface', 'file_dialog', 'unknown'
        """
        screenshot = await self._take_screenshot()
        if not screenshot.base64_image:
            return "unknown"
        
        print("🔍 Detecting current OrcaSheets state...")
        
        # Look for key elements that identify each state
        state_indicators = {
            'project_selection': [
                'NEW PROJECT',
                'default',
                'Search projects',
                'World\'s Fastest Analytics Engine'
            ],
            'main_interface': [
                'Add new sheet',
                'Sheets',
                'DEFAULT',
                'industry.csv'
            ],
            'file_dialog': [
                'Open',
                'Cancel',
                'Downloads',
                'Desktop'
            ]
        }
        
        # Try to identify state using visual analysis
        for state, indicators in state_indicators.items():
            for indicator in indicators:
                coords = await self.visual_ai.find_element_by_description(
                    screenshot.base64_image, indicator
                )
                if coords:
                    print(f"✅ Detected state: {state} (found '{indicator}')")
                    self.current_state = state
                    return state
        
        print("⚠️  Could not detect current state")
        self.current_state = "unknown"
        return "unknown"
    
    async def execute_workflow_command(self, command: str) -> bool:
        """
        Execute a command following proper OrcaSheets workflow.
        """
        print(f"🎯 Executing workflow command: '{command}'")
        
        # Parse the command to understand what needs to be done
        if "upload" in command.lower() and any(ext in command for ext in ['.csv', '.xlsx', '.json']):
            # This is a file upload workflow
            file_name = self._extract_filename(command)
            project_name = self._extract_project_name(command) or "default"
            
            return await self._execute_upload_workflow(file_name, project_name)
        
        elif "close" in command.lower() and "tab" in command.lower():
            # This is a tab closing workflow
            tab_name = self._extract_tab_name(command)
            return await self._execute_close_tab_workflow(tab_name)
        
        elif "select" in command.lower() and "project" in command.lower():
            # This is a project selection workflow
            project_name = self._extract_project_name(command) or "default"
            return await self._execute_select_project_workflow(project_name)
        
        else:
            print(f"❌ Unknown workflow command: {command}")
            return False
    
    async def _execute_upload_workflow(self, file_name: str, project_name: str) -> bool:
        """
        Execute the complete file upload workflow:
        1. Open OrcaSheets → 2. Select project → 3. Click Add new sheet → 4. Upload file
        """
        print(f"📋 Executing upload workflow: {file_name} to {project_name}")
        
        try:
            # Step 1: Ensure OrcaSheets is open
            if not await self._ensure_orcasheets_open():
                return False
            
            # Step 2: Navigate to project selection if needed
            if not await self._ensure_project_selection_screen():
                return False
            
            # Step 3: Select the project
            if not await self._select_project_in_ui(project_name):
                return False
            
            # Step 4: Wait for main interface
            if not await self._wait_for_main_interface():
                return False
            
            # Step 5: Click "Add new sheet"
            if not await self._click_add_new_sheet():
                return False
            
            # Step 6: Wait for file dialog and upload
            if not await self._upload_file_in_dialog(file_name):
                return False
            
            print("✅ Upload workflow completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Upload workflow failed: {e}")
            return False
    
    async def _execute_close_tab_workflow(self, tab_name: str) -> bool:
        """Close a specific tab in the main interface"""
        print(f"🗙 Executing close tab workflow: {tab_name}")
        
        try:
            # Ensure we're in main interface
            if not await self._wait_for_main_interface():
                return False
            
            # Find and close the tab
            return await self._close_tab_in_ui(tab_name)
            
        except Exception as e:
            print(f"❌ Close tab workflow failed: {e}")
            return False
    
    async def _execute_select_project_workflow(self, project_name: str) -> bool:
        """Select a project"""
        print(f"📂 Executing select project workflow: {project_name}")
        
        try:
            if not await self._ensure_project_selection_screen():
                return False
            
            return await self._select_project_in_ui(project_name)
            
        except Exception as e:
            print(f"❌ Select project workflow failed: {e}")
            return False
    
    async def _ensure_orcasheets_open(self) -> bool:
        """Ensure OrcaSheets is open"""
        print("📱 Ensuring OrcaSheets is open...")
        
        # Try AppleScript first
        is_running = await self.applescript.is_application_running("OrcaSheets")
        if is_running:
            print("✅ OrcaSheets is already running")
            success = await self.applescript.open_application("OrcaSheets")
            if success:
                await self._wait(2.0)
                return True
        
        # Use Spotlight to open
        print("🔍 Opening OrcaSheets via Spotlight...")
        await self.computer(action="key", text="cmd+space")
        await self._wait(1.0)
        await self.computer(action="type", text="OrcaSheets")
        await self._wait(1.0)
        await self.computer(action="key", text="Return")
        await self._wait(4.0)  # Wait for app to fully launch
        
        return True
    
    async def _ensure_project_selection_screen(self) -> bool:
        """Ensure we're on the project selection screen"""
        print("📋 Ensuring project selection screen...")
        
        for attempt in range(self.max_retries):
            state = await self._detect_current_state()
            
            if state == "project_selection":
                print("✅ Already on project selection screen")
                return True
            elif state == "main_interface":
                print("🔄 Currently in main interface, need to go back to project selection")
                # Try to go back (this depends on OrcaSheets UI)
                # Could try clicking back button or using menu
                await self.computer(action="key", text="cmd+shift+h")  # Common "home" shortcut
                await self._wait(2.0)
            else:
                print(f"⚠️  Unknown state: {state}, waiting...")
                await self._wait(2.0)
        
        # Final check
        state = await self._detect_current_state()
        return state == "project_selection"
    
    async def _select_project_in_ui(self, project_name: str) -> bool:
        """Select a project from the project selection screen"""
        print(f"📂 Selecting project: {project_name}")
        
        screenshot = await self._take_screenshot()
        if not screenshot.base64_image:
            return False
        
        # First, check if there are existing projects by looking for project names/paths
        existing_project_indicators = [
            "default",  # Look for default project
            "freetime_agent",  # Look for the other project
            "/OrcaSheets/core_ocean/",  # Look for project path patterns
            "Application Support",  # Part of the project path
        ]
        
        # Check if we can find existing projects
        found_existing_project = False
        for indicator in existing_project_indicators:
            coords = await self.visual_ai.find_element_by_description(
                screenshot.base64_image, indicator
            )
            if coords:
                print(f"✅ Found existing project indicator: '{indicator}'")
                found_existing_project = True
                break
        
        # If no existing projects found, create a new one
        if not found_existing_project:
            print("🆕 No existing projects found - need to create a new project")
            return await self._create_new_project(project_name)
        
        # Method 1: Try to find and click the project name directly
        print("🔍 Method 1: Looking for existing project...")
        
        project_search_terms = [
            "default",     # Look for the default project first
            "freetime_agent",  # Look for the other project
            project_name,  # The specified project name
        ]
        
        for term in project_search_terms:
            coords = await self.visual_ai.find_element_by_description(
                screenshot.base64_image, term
            )
            if coords:
                print(f"🎯 Found project text '{term}' at {coords}")
                
                # Adjust coordinates to click on the folder icon area (left side of the project entry)
                # Based on the UI layout, the folder icon is typically to the left of the text
                folder_icon_x = 148  # Fixed X coordinate for the folder icon area
                project_line_y = coords[1]  # Use the Y coordinate from the found text
                
                print(f"🎯 Clicking folder icon at ({folder_icon_x}, {project_line_y})")
                
                # Double-click on the folder icon to open the project
                print("🖱️ Double-clicking folder icon to open project...")
                await self.computer(action="mouse_move", coordinate=[folder_icon_x, project_line_y])
                await self.computer(action="double_click")
                await self._wait(3.0)
                
                # Verify if the project opened
                new_state = await self._detect_current_state()
                if new_state == "main_interface":
                    print(f"✅ Successfully opened project '{term}' with double-click on folder")
                    return True
                
                # If folder icon didn't work, try clicking directly on the project name area
                project_name_x = 178  # X coordinate for project name area
                print(f"🎯 Trying project name area at ({project_name_x}, {project_line_y})")
                
                await self.computer(action="mouse_move", coordinate=[project_name_x, project_line_y])
                await self.computer(action="double_click")
                await self._wait(3.0)
                
                # Verify again
                new_state = await self._detect_current_state()
                if new_state == "main_interface":
                    print(f"✅ Successfully opened project '{term}' with double-click on name")
                    return True
                
                # Final attempt: single click + Enter on project name area
                print("🔑 Final attempt: single click + Enter on project name...")
                await self.computer(action="mouse_move", coordinate=[project_name_x, project_line_y])
                await self.computer(action="left_click")
                await self._wait(0.5)
                await self.computer(action="key", text="Return")
                await self._wait(3.0)
                
                # Final verification
                new_state = await self._detect_current_state()
                if new_state == "main_interface":
                    print(f"✅ Successfully opened project '{term}' with Enter key")
                    return True
        
        # Method 2: If no existing project found, create a new one
        print("🆕 No existing projects found - creating new project")
        return await self._create_new_project(project_name)
    
    async def _create_new_project(self, project_name: str) -> bool:
        """Create a new project when none exist"""
        print(f"🆕 Creating new project: {project_name}")
        
        screenshot = await self._take_screenshot()
        if not screenshot.base64_image:
            return False
        
        # Look for the "NEW PROJECT" button
        new_project_search_terms = [
            "NEW PROJECT",
            "New Project", 
            "new project",
            "Create Project"
        ]
        
        for term in new_project_search_terms:
            coords = await self.visual_ai.find_element_by_description(
                screenshot.base64_image, term
            )
            if coords:
                print(f"🎯 Found '{term}' button at {coords}")
                
                # Click the NEW PROJECT button
                await self.computer(action="mouse_move", coordinate=[coords[0], coords[1]])
                await self.computer(action="left_click")
                await self._wait(2.0)
                
                # Check if a dialog appeared for project name
                await self._wait(1.0)
                
                # Type the project name if there's a text field
                if project_name != "default":
                    await self.computer(action="type", text=project_name)
                    await self._wait(0.5)
                
                # Press Enter to create the project
                await self.computer(action="key", text="Return")
                await self._wait(3.0)
                
                # Verify if we're now in the main interface
                new_state = await self._detect_current_state()
                if new_state == "main_interface":
                    print(f"✅ Successfully created and opened new project '{project_name}'")
                    return True
                
                # Sometimes there might be another confirmation step
                await self.computer(action="key", text="Return")
                await self._wait(3.0)
                
                # Final verification
                final_state = await self._detect_current_state()
                if final_state == "main_interface":
                    print(f"✅ Successfully created and opened new project '{project_name}' after confirmation")
                    return True
        
        print(f"❌ Failed to create new project '{project_name}'")
        return False
    
    async def _wait_for_main_interface(self) -> bool:
        """Wait for the main OrcaSheets interface to load"""
        print("⏳ Waiting for main interface...")
        
        for attempt in range(10):  # Wait up to 20 seconds
            state = await self._detect_current_state()
            if state == "main_interface":
                print("✅ Main interface loaded")
                return True
            
            print(f"   Attempt {attempt + 1}/10: Current state = {state}")
            await self._wait(2.0)
        
        print("❌ Main interface did not load in time")
        return False
    
    async def _click_add_new_sheet(self) -> bool:
        """Click the 'Add new sheet' button in the main interface"""
        print("➕ Clicking 'Add new sheet' button...")
        
        screenshot = await self._take_screenshot()
        if not screenshot.base64_image:
            return False
        
        # Search terms for the Add new sheet button
        search_terms = [
            "Add new sheet",
            "+ Add new sheet",
            "Add new",
            "new sheet"
        ]
        
        # Method 1: Try AppleScript
        for term in search_terms:
            success = await self.applescript.find_and_click_text("OrcaSheets", term)
            if success:
                print(f"✅ Clicked 'Add new sheet' using AppleScript")
                await self._wait(3.0)
                return True
        
        # Method 2: Try visual detection
        for term in search_terms:
            coords = await self.visual_ai.find_element_by_description(
                screenshot.base64_image, term
            )
            if coords:
                await self.computer(action="mouse_move", coordinate=[coords[0], coords[1]])
                await self.computer(action="left_click")
                print(f"✅ Clicked 'Add new sheet' using visual detection")
                await self._wait(3.0)
                return True
        
        print("❌ Could not find 'Add new sheet' button")
        return False
    
    async def _upload_file_in_dialog(self, file_name: str) -> bool:
        """Handle file upload in the file dialog"""
        print(f"📎 Uploading file: {file_name}")
        
        # Wait for file dialog to appear
        await self._wait(2.0)
        
        # Construct file path
        file_path = f"~/Downloads/{file_name}"
        expanded_path = Path(file_path).expanduser()
        
        try:
            # Method 1: Try AppleScript file selection
            success = await self.applescript.select_file_in_dialog(str(expanded_path))
            if success:
                print("✅ File selected using AppleScript")
                return True
            
            # Method 2: Use keyboard navigation
            print("🔄 Using keyboard navigation...")
            
            # Go to Downloads folder
            await self.computer(action="key", text="cmd+shift+g")
            await self._wait(1.0)
            await self.computer(action="type", text=str(expanded_path.parent))
            await self.computer(action="key", text="Return")
            await self._wait(1.5)
            
            # Type filename to select it
            await self.computer(action="type", text=expanded_path.name)
            await self._wait(1.0)
            
            # Press Enter to open
            await self.computer(action="key", text="Return")
            await self._wait(2.0)
            
            print(f"✅ File uploaded: {file_name}")
            return True
            
        except Exception as e:
            print(f"❌ File upload failed: {e}")
            return False
    
    async def _close_tab_in_ui(self, tab_name: str) -> bool:
        """Close a specific tab in the main interface"""
        print(f"🗙 Closing tab: {tab_name}")
        
        screenshot = await self._take_screenshot()
        if not screenshot.base64_image:
            return False
        
        # Look for the tab and its close button
        tab_search_terms = [
            f"{tab_name} tab",
            tab_name,
            f"close {tab_name}",
            f"{tab_name} close"
        ]
        
        for term in tab_search_terms:
            coords = await self.visual_ai.find_element_by_description(
                screenshot.base64_image, term
            )
            if coords:
                # Try right-click for context menu first
                await self.computer(action="mouse_move", coordinate=[coords[0], coords[1]])
                await self.computer(action="right_click")
                await self._wait(0.5)
                
                # Look for close option in context menu
                close_coords = await self.visual_ai.find_element_by_description(
                    screenshot.base64_image, "close"
                )
                if close_coords:
                    await self.computer(action="mouse_move", coordinate=[close_coords[0], close_coords[1]])
                    await self.computer(action="left_click")
                    print(f"✅ Closed tab '{tab_name}' using context menu")
                    return True
        
        print(f"❌ Could not close tab: {tab_name}")
        return False
    
    # Helper methods for parsing commands
    def _extract_filename(self, command: str) -> str:
        """Extract filename from command"""
        import re
        # Look for filenames with extensions
        match = re.search(r'([a-zA-Z0-9_-]+\.(csv|xlsx?|json|txt))', command)
        return match.group(1) if match else ""
    
    def _extract_project_name(self, command: str) -> Optional[str]:
        """Extract project name from command"""
        import re
        # Look for project name patterns
        patterns = [
            r'select\s+([^,\s]+)\s+project',
            r'project\s+([^,\s]+)',
            r'to\s+([^,\s]+)\s+project'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Default fallback
        if 'default' in command.lower():
            return 'default'
        
        return None
    
    def _extract_tab_name(self, command: str) -> str:
        """Extract tab name from command"""
        import re
        # Look for tab name patterns
        match = re.search(r'close\s+([^,\s]+(?:\.\w+)?)\s+tab', command, re.IGNORECASE)
        return match.group(1) if match else ""
    
    async def take_debug_screenshot(self, filename: str = "workflow_debug.png") -> ToolResult:
        """Take a debug screenshot"""
        screenshot = await self._take_screenshot()
        if screenshot.base64_image:
            image_data = base64.b64decode(screenshot.base64_image)
            with open(filename, 'wb') as f:
                f.write(image_data)
            print(f"🖼️  Debug screenshot saved as {filename}")
        return screenshot


# Example usage functions
async def upload_file_workflow(file_name: str, project_name: str = "default") -> bool:
    """Upload a file following proper OrcaSheets workflow"""
    automation = WorkflowOrcaSheetsAutomation()
    return await automation._execute_upload_workflow(file_name, project_name)


async def execute_workflow_command(command: str) -> bool:
    """Execute any workflow command"""
    automation = WorkflowOrcaSheetsAutomation()
    return await automation.execute_workflow_command(command)