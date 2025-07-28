"""
Click action handler
"""

import asyncio
from typing import Dict, Any

from ...base import ToolResult
from .base_handler import BaseActionHandler
from ..ui_detection import ElementFinder


class ClickHandler(BaseActionHandler):
    """Handle computer click actions"""
    
    def __init__(self, computer_tool, element_finder: ElementFinder = None, test_runner=None):
        super().__init__(computer_tool)
        self.element_finder = element_finder or ElementFinder()
        self.test_runner = test_runner  # Reference to test runner for similarity matching
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute click action with configurable retry parameters"""
        try:
            target = params.get('target', '')
            max_retries = params.get('max_retries', 1)  # Allow configurable retries
            wait_time = params.get('wait_time', 2)  # Allow configurable wait time
            
            print(f"[CLICK] Handling computer click with params: {params}")
            print(f"[CLICK] Searching for target: '{target}' with {max_retries} retries")
            
            return await self._find_and_click_target(target, max_retries, wait_time)
            
        except Exception as e:
            return ToolResult(error=f"Error in click action: {str(e)}")

    async def _find_and_click_target(self, target: str, max_retries: int = 1, wait_time: int = 2) -> ToolResult:
        """Find target element and click on it with wait and retry fallback"""
        try:
            for attempt in range(max_retries + 1):
                print(f"[FIND_CLICK] Attempt {attempt + 1}/{max_retries + 1} searching for target: '{target}'")
                
                # Take screenshot first
                screenshot_result = await self.computer_tool(action='screenshot')
                
                # Use ElementFinder to locate the target
                found_coordinate = await self.element_finder.find_element(target, screenshot_result.base64_image)
                
                # Execute click if target found
                if found_coordinate:
                    print(f"[FIND_CLICK] ✅ Found target '{target}' at {found_coordinate} on attempt {attempt + 1}")
                    
                    # First drag mouse to target to ensure accurate positioning
                    print(f"[FIND_CLICK] Moving mouse to target at {found_coordinate}")
                    await self.computer_tool(action='mouse_move', coordinate=found_coordinate)
                    
                    # Small delay for mouse positioning
                    await asyncio.sleep(0.3)
                    
                    print(f"[FIND_CLICK] Clicking at {found_coordinate}")
                    await self.computer_tool(action='left_click', coordinate=found_coordinate)
                    
                    # Reduced delay after clicking
                    await asyncio.sleep(0.5)
                    
                    # Take final screenshot to verify the click
                    final_screenshot = await self.computer_tool(action='screenshot')
                    
                    # Quick verification - see what changed after the click
                    print(f"[FIND_CLICK] Verifying post-click state...")
                    try:
                        # Do a quick OCR scan to see if anything obvious changed
                        post_click_text = await self.element_finder.ocr_engine.find_text_on_screen("Add New Sheet", final_screenshot.base64_image)
                        if post_click_text:
                            print(f"[FIND_CLICK] ✅ Post-click verification: 'Add New Sheet' found at {post_click_text}")
                        else:
                            print(f"[FIND_CLICK] ⚠️ Post-click verification: 'Add New Sheet' not found")
                            
                        # Also check for other signs the click worked
                        common_ui_changes = ["New", "Add", "Create", "Open", "Select"]
                        for ui_text in common_ui_changes:
                            if await self.element_finder.ocr_engine.find_text_on_screen(ui_text, final_screenshot.base64_image):
                                print(f"[FIND_CLICK] 📋 Post-click: Found UI element '{ui_text}'")
                                break
                                
                    except Exception as e:
                        print(f"[FIND_CLICK] Post-click verification failed: {e}")
                    
                    return ToolResult(
                        output=f"Found and clicked target '{target}' at {found_coordinate}",
                        base64_image=final_screenshot.base64_image
                    )
                elif attempt < max_retries:
                    print(f"[FIND_CLICK] ❌ Target '{target}' not found, waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[FIND_CLICK] ❌ Target '{target}' not found after {max_retries + 1} attempts")
                    
                    # Try similarity-based fallback as last resort
                    if self.test_runner and hasattr(self.test_runner, '_find_similar_elements'):
                        print(f"[FIND_CLICK] Attempting similarity-based fallback for '{target}'...")
                        similar_coordinate = await self.test_runner._find_similar_elements(target, screenshot_result.base64_image)
                        
                        if similar_coordinate:
                            print(f"[FIND_CLICK] ✅ Similarity fallback found target at {similar_coordinate}")
                            
                            # Move mouse and click on similar element
                            print(f"[FIND_CLICK] Moving mouse to similar target at {similar_coordinate}")
                            await self.computer_tool(action='mouse_move', coordinate=similar_coordinate)
                            await asyncio.sleep(0.3)
                            
                            print(f"[FIND_CLICK] Clicking similar target at {similar_coordinate}")
                            await self.computer_tool(action='left_click', coordinate=similar_coordinate)
                            await asyncio.sleep(0.5)
                            
                            # Take final screenshot
                            final_screenshot = await self.computer_tool(action='screenshot')
                            
                            return ToolResult(
                                output=f"Found similar element to '{target}' and clicked at {similar_coordinate} (similarity fallback)",
                                base64_image=final_screenshot.base64_image
                            )
                        else:
                            print(f"[FIND_CLICK] ❌ Similarity fallback also failed")
                    
                    return ToolResult(
                        error=f"Could not find target '{target}' on screen using OCR, vision systems, or similarity matching after {max_retries + 1} attempts.",
                        base64_image=screenshot_result.base64_image
                    )
                
        except Exception as e:
            return ToolResult(error=f"Error finding target '{target}': {str(e)}")