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
    
    def __init__(self, computer_tool, element_finder: ElementFinder = None):
        super().__init__(computer_tool)
        self.element_finder = element_finder or ElementFinder()
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute click action"""
        try:
            target = params.get('target', '')
            print(f"[CLICK] Handling computer click with params: {params}")
            print(f"[CLICK] Searching for target: '{target}'")
            
            return await self._find_and_click_target(target)
            
        except Exception as e:
            return ToolResult(error=f"Error in click action: {str(e)}")

    async def _find_and_click_target(self, target: str) -> ToolResult:
        """Find target element and click on it"""
        try:
            print(f"[FIND_CLICK] Generic search for target: '{target}'")
            
            # Take screenshot first
            screenshot_result = await self.computer_tool(action='screenshot')
            
            found_coordinate = None
            
            # Use ElementFinder to locate the target
            found_coordinate = await self.element_finder.find_element(target, screenshot_result.base64_image)
            
            # Execute click if target found
            if found_coordinate:
                print(f"[FIND_CLICK] ✅ Found target '{target}' at {found_coordinate}")
                
                # Add small delay before clicking
                await asyncio.sleep(0.5)
                
                print(f"[FIND_CLICK] Clicking directly at {found_coordinate}")
                click_result = await self.computer_tool(action='left_click', coordinate=found_coordinate)
                
                # Add small delay after clicking
                await asyncio.sleep(1)
                
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
            else:
                return ToolResult(
                    error=f"Could not find target '{target}' on screen using OCR or vision systems.",
                    base64_image=screenshot_result.base64_image
                )
                
        except Exception as e:
            return ToolResult(error=f"Error finding target '{target}': {str(e)}")