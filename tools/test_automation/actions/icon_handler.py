"""
Icon Click Handler using Computer Vision
Specialized for finding and clicking small UI icons
"""

import asyncio
from typing import Dict, Any, Optional, List

from ...base import ToolResult
from .base_handler import BaseActionHandler
from ..vision.icon_detector import IconDetector


class IconHandler(BaseActionHandler):
    """Handle icon detection and clicking using computer vision"""
    
    def __init__(self, computer_tool, test_runner=None):
        super().__init__(computer_tool)
        self.icon_detector = IconDetector()
        self.test_runner = test_runner
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute icon click action"""
        try:
            icon_name = params.get('icon', '')
            confidence = params.get('confidence', 0.7)
            max_retries = params.get('max_retries', 2)
            wait_time = params.get('wait_time', 1)
            save_template = params.get('save_template', False)
            
            print(f"[ICON_HANDLER] Looking for icon: '{icon_name}' with confidence {confidence}")
            
            return await self._find_and_click_icon(
                icon_name, confidence, max_retries, wait_time, save_template
            )
            
        except Exception as e:
            return ToolResult(error=f"Error in icon click action: {str(e)}")
    
    async def _find_and_click_icon(self, icon_name: str, confidence: float, 
                                  max_retries: int, wait_time: int, 
                                  save_template: bool) -> ToolResult:
        """Find and click icon with retry logic"""
        try:
            for attempt in range(max_retries + 1):
                print(f"[ICON_HANDLER] Attempt {attempt + 1}/{max_retries + 1} searching for icon: '{icon_name}'")
                
                # Take screenshot
                screenshot_result = await self.computer_tool(action='screenshot')
                if screenshot_result.error:
                    return ToolResult(error=f"Failed to take screenshot: {screenshot_result.error}")
                
                # Use icon detector to find the icon
                coordinates = await self.icon_detector.find_icon(
                    icon_name, screenshot_result.base64_image, confidence
                )
                
                if coordinates:
                    print(f"[ICON_HANDLER] ✅ Found icon '{icon_name}' at {coordinates}")
                    
                    # Save as template if requested
                    if save_template:
                        template_path = self.icon_detector.save_icon_template(
                            icon_name, screenshot_result.base64_image, coordinates
                        )
                        if template_path:
                            print(f"[ICON_HANDLER] Saved template: {template_path}")
                    
                    # Move mouse to icon
                    print(f"[ICON_HANDLER] Moving mouse to icon at {coordinates}")
                    await self.computer_tool(action='mouse_move', coordinate=coordinates)
                    await asyncio.sleep(0.2)  # Small delay for precision
                    
                    # Click the icon
                    print(f"[ICON_HANDLER] Clicking icon at {coordinates}")
                    await self.computer_tool(action='left_click', coordinate=coordinates)
                    await asyncio.sleep(0.3)  # Wait for click to register
                    
                    # Take post-click screenshot
                    final_screenshot = await self.computer_tool(action='screenshot')
                    
                    # Verify click had an effect (basic verification)
                    verification_result = await self._verify_icon_click(
                        icon_name, final_screenshot.base64_image if final_screenshot else None
                    )
                    
                    return ToolResult(
                        output=f"Successfully found and clicked icon '{icon_name}' at {coordinates}. {verification_result}",
                        base64_image=final_screenshot.base64_image if final_screenshot else screenshot_result.base64_image
                    )
                
                elif attempt < max_retries:
                    print(f"[ICON_HANDLER] ❌ Icon '{icon_name}' not found, waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"[ICON_HANDLER] ❌ Icon '{icon_name}' not found after {max_retries + 1} attempts")
                    
                    # Try similarity fallback if available
                    if self.test_runner and hasattr(self.test_runner, '_find_similar_elements'):
                        print(f"[ICON_HANDLER] Attempting similarity-based fallback for icon '{icon_name}'...")
                        similar_coordinate = await self.test_runner._find_similar_elements(
                            icon_name, screenshot_result.base64_image
                        )
                        
                        if similar_coordinate:
                            print(f"[ICON_HANDLER] ✅ Similarity fallback found similar element at {similar_coordinate}")
                            
                            # Click on similar element
                            await self.computer_tool(action='mouse_move', coordinate=similar_coordinate)
                            await asyncio.sleep(0.2)
                            await self.computer_tool(action='left_click', coordinate=similar_coordinate)
                            await asyncio.sleep(0.3)
                            
                            final_screenshot = await self.computer_tool(action='screenshot')
                            
                            return ToolResult(\n                                output=f\"Found similar element to icon '{icon_name}' and clicked at {similar_coordinate} (similarity fallback)\",\n                                base64_image=final_screenshot.base64_image if final_screenshot else screenshot_result.base64_image\n                            )\n                        else:\n                            print(f\"[ICON_HANDLER] ❌ Similarity fallback also failed\")\n                    \n                    return ToolResult(\n                        error=f\"Could not find icon '{icon_name}' using computer vision, template matching, or similarity fallback after {max_retries + 1} attempts.\",\n                        base64_image=screenshot_result.base64_image\n                    )\n                \n        except Exception as e:\n            return ToolResult(error=f\"Error finding icon '{icon_name}': {str(e)}\")\n    \n    async def _verify_icon_click(self, icon_name: str, screenshot_base64: Optional[str]) -> str:\n        \"\"\"Basic verification that the icon click had an effect\"\"\"\n        try:\n            if not screenshot_base64:\n                return \"Click completed (no post-click verification)\"\n            \n            # Look for common UI changes that indicate successful icon clicks\n            verification_indicators = {\n                'search': ['Search', 'Find', 'Query', 'search'],\n                'add': ['New', 'Create', 'Add', 'Plus'],\n                'settings': ['Settings', 'Preferences', 'Options', 'Configuration'],\n                'close': [],  # Close actions remove elements, hard to verify\n                'menu': ['Menu', 'Options', 'File', 'Edit', 'View'],\n                'play': ['Playing', 'Pause', 'Stop'],\n                'pause': ['Paused', 'Play', 'Resume'],\n                'home': ['Home', 'Dashboard', 'Main'],\n                'back': ['Back', 'Previous'],\n                'refresh': ['Loading', 'Refreshing', 'Updated'],\n                'save': ['Saved', 'Save successful', 'Saved to'],\n                'delete': ['Deleted', 'Removed', 'Trash'],\n                'edit': ['Edit', 'Modify', 'Change']\n            }\n            \n            indicators = verification_indicators.get(icon_name.lower(), [])\n            \n            if indicators:\n                # Use OCR to check for verification text\n                try:\n                    import pytesseract\n                    from PIL import Image\n                    import io\n                    import base64\n                    \n                    screenshot_data = base64.b64decode(screenshot_base64)\n                    image = Image.open(io.BytesIO(screenshot_data))\n                    text = pytesseract.image_to_string(image).lower()\n                    \n                    found_indicators = []\n                    for indicator in indicators:\n                        if indicator.lower() in text:\n                            found_indicators.append(indicator)\n                    \n                    if found_indicators:\n                        return f\"Click verification: Found expected UI changes - {', '.join(found_indicators)}\"\n                    else:\n                        return \"Click completed (no verification indicators found)\"\n                        \n                except Exception as e:\n                    return f\"Click completed (verification error: {e})\"\n            else:\n                return \"Click completed (no verification configured for this icon type)\"\n                \n        except Exception as e:\n            return f\"Click completed (verification failed: {e})\"\n    \n    async def execute_find_only(self, params: Dict[str, Any]) -> ToolResult:\n        \"\"\"Find icon without clicking (for verification purposes)\"\"\"\n        try:\n            icon_name = params.get('icon', '')\n            confidence = params.get('confidence', 0.7)\n            save_template = params.get('save_template', False)\n            \n            print(f\"[ICON_HANDLER] Finding icon (no click): '{icon_name}'\")\n            \n            # Take screenshot\n            screenshot_result = await self.computer_tool(action='screenshot')\n            if screenshot_result.error:\n                return ToolResult(error=f\"Failed to take screenshot: {screenshot_result.error}\")\n            \n            # Find icon\n            coordinates = await self.icon_detector.find_icon(\n                icon_name, screenshot_result.base64_image, confidence\n            )\n            \n            if coordinates:\n                print(f\"[ICON_HANDLER] ✅ Found icon '{icon_name}' at {coordinates}\")\n                \n                # Save as template if requested\n                if save_template:\n                    template_path = self.icon_detector.save_icon_template(\n                        icon_name, screenshot_result.base64_image, coordinates\n                    )\n                    if template_path:\n                        print(f\"[ICON_HANDLER] Saved template: {template_path}\")\n                \n                return ToolResult(\n                    output=f\"Found icon '{icon_name}' at {coordinates}\",\n                    base64_image=screenshot_result.base64_image\n                )\n            else:\n                return ToolResult(\n                    error=f\"Icon '{icon_name}' not found on screen\",\n                    base64_image=screenshot_result.base64_image\n                )\n                \n        except Exception as e:\n            return ToolResult(error=f\"Error finding icon: {str(e)}\")\n    \n    async def execute_save_template(self, params: Dict[str, Any]) -> ToolResult:\n        \"\"\"Save an icon template by clicking on it first\"\"\"\n        try:\n            icon_name = params.get('icon', '')\n            coordinates = params.get('coordinates')  # [x, y] if known\n            crop_size = params.get('crop_size', 50)\n            \n            print(f\"[ICON_HANDLER] Saving template for icon: '{icon_name}'\")\n            \n            # Take screenshot\n            screenshot_result = await self.computer_tool(action='screenshot')\n            if screenshot_result.error:\n                return ToolResult(error=f\"Failed to take screenshot: {screenshot_result.error}\")\n            \n            # If coordinates not provided, try to find the icon first\n            if not coordinates:\n                coordinates = await self.icon_detector.find_icon(\n                    icon_name, screenshot_result.base64_image\n                )\n                \n                if not coordinates:\n                    return ToolResult(\n                        error=f\"Cannot save template: Icon '{icon_name}' not found and no coordinates provided\",\n                        base64_image=screenshot_result.base64_image\n                    )\n            \n            # Save template\n            template_path = self.icon_detector.save_icon_template(\n                icon_name, screenshot_result.base64_image, coordinates, crop_size\n            )\n            \n            if template_path:\n                return ToolResult(\n                    output=f\"Successfully saved icon template for '{icon_name}' at {template_path}\",\n                    base64_image=screenshot_result.base64_image\n                )\n            else:\n                return ToolResult(\n                    error=f\"Failed to save icon template for '{icon_name}'\",\n                    base64_image=screenshot_result.base64_image\n                )\n                \n        except Exception as e:\n            return ToolResult(error=f\"Error saving icon template: {str(e)}\")