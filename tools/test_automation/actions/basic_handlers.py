"""
Basic action handlers for common operations
"""

import asyncio
import os
import subprocess
from typing import Dict, Any

from ...base import ToolResult
from .base_handler import BaseActionHandler
from ..ui_detection import ElementFinder


class ScreenshotHandler(BaseActionHandler):
    """Handle screenshot actions"""
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Take a screenshot"""
        try:
            screenshot_result = await self.computer_tool(action='screenshot')
            print(f"[TEST] Screenshot captured: {len(screenshot_result.base64_image)} bytes")
            return screenshot_result
        except Exception as e:
            return ToolResult(error=f"Error taking screenshot: {str(e)}")


class TypeHandler(BaseActionHandler):
    """Handle typing actions"""
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Type text"""
        try:
            text = params.get('text', '')
            return await self.computer_tool(action='type', text=text)
        except Exception as e:
            return ToolResult(error=f"Error typing text: {str(e)}")


class KeyHandler(BaseActionHandler):
    """Handle keyboard key actions"""
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Press keyboard keys"""
        try:
            key = params.get('key', '')
            return await self.computer_tool(action='key', text=key)
        except Exception as e:
            return ToolResult(error=f"Error pressing key: {str(e)}")


class WaitHandler(BaseActionHandler):
    """Handle wait actions"""
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Wait for specified duration"""
        try:
            duration = params.get('duration', 1)
            await asyncio.sleep(duration)
            return ToolResult(output=f"Waited {duration} seconds")
        except Exception as e:
            return ToolResult(error=f"Error waiting: {str(e)}")


class ApplicationHandler(BaseActionHandler):
    """Handle application open/close actions"""
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Default execute method - not used, use execute_open/execute_close instead"""
        return ToolResult(error="Use execute_open or execute_close methods")
    
    async def execute_open(self, params: Dict[str, Any]) -> ToolResult:
        """Handle open application action using Spotlight"""
        app_name = params.get('app', '')
        
        print(f"[OPEN_APP] Opening application: {app_name}")
        
        # Use Spotlight to open the application
        # First open Spotlight with Cmd+Space
        await self.computer_tool(action='key', text='cmd+space')
        await asyncio.sleep(0.5)  # Reduced wait for Spotlight to open
        
        # Type the application name
        await self.computer_tool(action='type', text=app_name)
        await asyncio.sleep(0.5)  # Reduced wait for search results
        
        # Press Enter to open the first result
        await self.computer_tool(action='key', text='Return')
        
        # Reduced wait for app to load
        print(f"[OPEN_APP] Waiting for {app_name} to load and come to foreground...")
        await asyncio.sleep(1.5)
        
        # Try to bring the app to foreground using AppleScript
        try:
            await self.computer_tool.shell(f'osascript -e "tell application \\"{app_name}\\" to activate"', take_screenshot=False)
            await asyncio.sleep(1)  # Reduced activation wait
            print(f"[OPEN_APP] Attempted to bring {app_name} to foreground")
        except Exception as e:
            print(f"[OPEN_APP] Could not bring to foreground via AppleScript: {e}")
        
        # Take screenshot after opening
        screenshot_result = await self.computer_tool(action='screenshot')
        
        return ToolResult(
            output=f"Opened {app_name} using Spotlight and brought to foreground",
            base64_image=screenshot_result.base64_image
        )

    async def execute_close(self, params: Dict[str, Any]) -> ToolResult:
        """Handle close application action"""
        app_name = params.get('app', '')
        # Use macOS quit command
        return await self.computer_tool.shell(f"osascript -e 'quit app \"{app_name}\"'", take_screenshot=True)


class FileHandler(BaseActionHandler):
    """Handle file operations"""
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Default execute method - not used, use specific methods instead"""
        return ToolResult(error="Use execute_upload or execute_ensure_exists methods")
    
    async def execute_upload(self, params: Dict[str, Any]) -> ToolResult:
        """Handle file upload action dynamically"""
        try:
            file_path = params.get('file_path', '')
            method = params.get('method', 'drag_drop')  # drag_drop, file_dialog, or paste
            
            print(f"[FILE_UPLOAD] Uploading file: '{file_path}' using method: '{method}'")
            
            if method == 'file_dialog':
                # Open file dialog and navigate to file
                await self.computer_tool(action='key', text='cmd+o')
                await asyncio.sleep(0.5)  # Reduced dialog wait
                
                # Navigate to file location
                await self.computer_tool(action='key', text='cmd+shift+g')
                await asyncio.sleep(0.3)  # Reduced nav wait
                
                # Type the directory path
                directory = os.path.dirname(os.path.expanduser(file_path))
                await self.computer_tool(action='type', text=directory)
                await self.computer_tool(action='key', text='Return')
                await asyncio.sleep(0.5)  # Reduced directory navigation wait
                
                # Type filename
                filename = os.path.basename(file_path)
                await self.computer_tool(action='type', text=filename)
                await self.computer_tool(action='key', text='Return')
                
            elif method == 'paste':
                # Copy file path to clipboard and paste
                await self.computer_tool.shell(f"echo '{file_path}' | pbcopy", take_screenshot=False)
                await self.computer_tool(action='key', text='cmd+v')
                
            else:  # drag_drop method
                # This would require more complex implementation
                # For now, fall back to file dialog method
                return await self.execute_upload({**params, 'method': 'file_dialog'})
            
            # Take screenshot after upload attempt
            screenshot_result = await self.computer_tool(action='screenshot')
            
            return ToolResult(
                output=f"File upload attempted for {file_path} using {method}",
                base64_image=screenshot_result.base64_image
            )
            
        except Exception as e:
            return ToolResult(error=f"Error uploading file: {str(e)}")

    async def execute_ensure_exists(self, params: Dict[str, Any]) -> ToolResult:
        """Handle ensure file exists action"""
        file_path = params.get('path', '')
        expanded_path = os.path.expanduser(file_path)
        
        if os.path.exists(expanded_path):
            return ToolResult(output=f"File exists: {expanded_path}")
        else:
            return ToolResult(error=f"File not found: {expanded_path}")


class VerificationHandler(BaseActionHandler):
    """Handle verification actions"""
    
    def __init__(self, computer_tool, element_finder: ElementFinder = None, test_runner=None):
        super().__init__(computer_tool)
        self.element_finder = element_finder or ElementFinder()
        self.test_runner = test_runner  # Reference to test runner for similarity matching
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Default execute method - not used, use specific verification methods instead"""
        return ToolResult(error="Use execute_verify_element, execute_verify_text, or execute_verify_window methods")
    
    async def execute_verify_element(self, params: Dict[str, Any]) -> ToolResult:
        """Handle verify element action with wait and retry fallback"""
        try:
            element = params.get('element', '')
            max_retries = params.get('max_retries', 1)  # Allow configurable retries
            wait_time = params.get('wait_time', 2)  # Allow configurable wait time
            
            for attempt in range(max_retries + 1):
                print(f"[VERIFY_ELEMENT] Attempt {attempt + 1}/{max_retries + 1} for element: '{element}'")
                
                # Take screenshot
                screenshot_result = await self.computer_tool(action='screenshot')
                
                # Search for the element
                coordinates = await self.element_finder.find_element(element, screenshot_result.base64_image)
                
                if coordinates:
                    print(f"[VERIFY_ELEMENT] ✅ Found element '{element}' at {coordinates} on attempt {attempt + 1}")
                    return ToolResult(
                        output=f"Element '{element}' found and verified at {coordinates}",
                        base64_image=screenshot_result.base64_image
                    )
                elif attempt < max_retries:
                    print(f"[VERIFY_ELEMENT] ❌ Element '{element}' not found, waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[VERIFY_ELEMENT] ❌ Element '{element}' not found after {max_retries + 1} attempts")
                    
                    # Try similarity-based fallback as last resort
                    if self.test_runner and hasattr(self.test_runner, '_find_similar_elements'):
                        print(f"[VERIFY_ELEMENT] Attempting similarity-based fallback for '{element}'...")
                        similar_coordinate = await self.test_runner._find_similar_elements(element, screenshot_result.base64_image)
                        
                        if similar_coordinate:
                            print(f"[VERIFY_ELEMENT] ✅ Similarity fallback found element at {similar_coordinate}")
                            return ToolResult(
                                output=f"Element similar to '{element}' found and verified at {similar_coordinate} (similarity fallback)",
                                base64_image=screenshot_result.base64_image
                            )
                        else:
                            print(f"[VERIFY_ELEMENT] ❌ Similarity fallback also failed")
                    
                    return ToolResult(
                        error=f"Element '{element}' not found on screen after {max_retries + 1} attempts (including similarity matching)",
                        base64_image=screenshot_result.base64_image
                    )
                
        except Exception as e:
            return ToolResult(error=f"Error verifying element: {str(e)}")

    async def execute_verify_text(self, params: Dict[str, Any]) -> ToolResult:
        """Handle verify text action with wait and retry fallback"""
        try:
            text = params.get('text', '')
            max_retries = params.get('max_retries', 1)  # Allow configurable retries
            wait_time = params.get('wait_time', 2)  # Allow configurable wait time
            
            for attempt in range(max_retries + 1):
                print(f"[VERIFY_TEXT] Attempt {attempt + 1}/{max_retries + 1} for text: '{text}'")
                
                # Take screenshot
                screenshot_result = await self.computer_tool(action='screenshot')
                
                # Search for the text
                coordinates = await self.element_finder.ocr_engine.find_text_on_screen(text, screenshot_result.base64_image)
                
                if coordinates:
                    print(f"[VERIFY_TEXT] ✅ Found text '{text}' at {coordinates} on attempt {attempt + 1}")
                    return ToolResult(
                        output=f"Text '{text}' found and verified at {coordinates}",
                        base64_image=screenshot_result.base64_image
                    )
                elif attempt < max_retries:
                    print(f"[VERIFY_TEXT] ❌ Text '{text}' not found, waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[VERIFY_TEXT] ❌ Text '{text}' not found after {max_retries + 1} attempts")
                    
                    # Try similarity-based fallback as last resort
                    if self.test_runner and hasattr(self.test_runner, '_find_similar_elements'):
                        print(f"[VERIFY_TEXT] Attempting similarity-based fallback for '{text}'...")
                        similar_coordinate = await self.test_runner._find_similar_elements(text, screenshot_result.base64_image)
                        
                        if similar_coordinate:
                            print(f"[VERIFY_TEXT] ✅ Similarity fallback found text at {similar_coordinate}")
                            return ToolResult(
                                output=f"Text similar to '{text}' found and verified at {similar_coordinate} (similarity fallback)",
                                base64_image=screenshot_result.base64_image
                            )
                        else:
                            print(f"[VERIFY_TEXT] ❌ Similarity fallback also failed")
                    
                    return ToolResult(
                        error=f"Text '{text}' not found on screen after {max_retries + 1} attempts (including similarity matching)",
                        base64_image=screenshot_result.base64_image
                    )
                
        except Exception as e:
            return ToolResult(error=f"Error verifying text: {str(e)}")

    async def execute_verify_window(self, params: Dict[str, Any]) -> ToolResult:
        """Handle window verification with wait and retry fallback"""
        try:
            app_name = params.get('app', '')
            max_retries = params.get('max_retries', 1)  # Allow configurable retries
            wait_time = params.get('wait_time', 2)  # Allow configurable wait time
            
            print(f"[VERIFY_WINDOW] Checking if '{app_name}' window is visible")
            
            # Check if process is running (only once, not in retry loop)
            try:
                result = subprocess.run(['pgrep', '-f', app_name], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    process_id = result.stdout.strip().split('\n')[0]
                    print(f"[VERIFY_WINDOW] {app_name} process found: {process_id}")
                else:
                    return ToolResult(error=f"No process found for {app_name}")
            except Exception as e:
                print(f"[VERIFY_WINDOW] Error checking process: {e}")
                return ToolResult(error=f"Error checking {app_name} process")
            
            # Retry loop for UI visibility
            for attempt in range(max_retries + 1):
                print(f"[VERIFY_WINDOW] Attempt {attempt + 1}/{max_retries + 1} to find UI for: '{app_name}'")
                
                # Take screenshot and look for app UI indicators
                screenshot_result = await self.computer_tool(action='screenshot')
                
                # Look for app name or other UI indicators
                coordinates = await self.element_finder.ocr_engine.find_text_on_screen(app_name, screenshot_result.base64_image)
                
                if coordinates:
                    print(f"[VERIFY_WINDOW] ✅ Found UI indicator '{app_name}' at {coordinates} on attempt {attempt + 1}")
                    return ToolResult(
                        output=f"Window '{app_name}' is visible and verified",
                        base64_image=screenshot_result.base64_image
                    )
                else:
                    # Try alternative indicators
                    alternative_indicators = [app_name.lower(), app_name.upper(), app_name.title()]
                    for indicator in alternative_indicators:
                        coords = await self.element_finder.ocr_engine.find_text_on_screen(indicator, screenshot_result.base64_image)
                        if coords:
                            print(f"[VERIFY_WINDOW] ✅ Found alternative UI indicator '{indicator}' at {coords} on attempt {attempt + 1}")
                            return ToolResult(
                                output=f"Window '{app_name}' is visible (found as '{indicator}')",
                                base64_image=screenshot_result.base64_image
                            )
                
                if attempt < max_retries:
                    print(f"[VERIFY_WINDOW] ❌ UI for '{app_name}' not visible, waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[VERIFY_WINDOW] ❌ UI for '{app_name}' not visible after {max_retries + 1} attempts")
                    return ToolResult(
                        error=f"Window '{app_name}' process running but UI not clearly visible after {max_retries + 1} attempts",
                        base64_image=screenshot_result.base64_image
                    )
                
        except Exception as e:
            return ToolResult(error=f"Error verifying window: {str(e)}")


class CustomHandler(BaseActionHandler):
    """Handle custom actions"""
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Handle custom action"""
        # Would allow custom action implementations
        return ToolResult(output="Custom action not implemented")