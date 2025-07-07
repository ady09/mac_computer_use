"""
UI element detection and positioning
"""

import os
import tempfile
import base64
from typing import List, Optional, Dict, Any
from PIL import Image
import io

from ..ocr import OCREngine


class ElementFinder:
    """Find UI elements using multiple detection methods"""
    
    def __init__(self, ocr_engine: OCREngine = None):
        self.ocr_engine = ocr_engine or OCREngine()
        self.templates_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
        
    async def find_element(self, target: str, screenshot_base64: str) -> Optional[List[int]]:
        """Find UI element using multiple detection methods"""
        try:
            print(f"[ELEMENT_FINDER] Searching for target: '{target}'")
            
            # METHOD 1: Primary OCR-based detection (generic, no app-specific logic)
            print(f"[ELEMENT_FINDER] Step 1: OCR-based detection")
            found_coordinate = await self.ocr_engine.find_text_on_screen(target, screenshot_base64)
            
            # METHOD 2: Try individual words if full phrase not found
            if not found_coordinate and len(target.split()) > 1:
                print(f"[ELEMENT_FINDER] Step 2: Trying individual words for: '{target}'")
                for word in target.split():
                    if len(word) >= 4:  # Only try meaningful words
                        print(f"[ELEMENT_FINDER] Searching for individual word: '{word}'")
                        word_coordinate = await self.ocr_engine.find_text_on_screen(word, screenshot_base64)
                        if word_coordinate:
                            print(f"[ELEMENT_FINDER] Found individual word '{word}' at {word_coordinate}")
                            found_coordinate = word_coordinate
                            break
            
            # METHOD 3: Smart position inference for common UI elements
            if not found_coordinate and target.lower() in ['search', 'search icon']:
                print(f"[ELEMENT_FINDER] Step 3: Smart position inference for search element")
                found_coordinate = await self._infer_search_position(screenshot_base64)
            
            # METHOD 4: Fallback to vision/template matching only if OCR fails
            if not found_coordinate:
                print(f"[ELEMENT_FINDER] Step 4: Vision/template fallback")
                found_coordinate = await self._find_using_vision_fallback(target, screenshot_base64)
            
            return found_coordinate
            
        except Exception as e:
            print(f"[ELEMENT_FINDER] Error finding element '{target}': {str(e)}")
            return None

    async def _infer_search_position(self, screenshot_base64: str) -> Optional[List[int]]:
        """Infer search icon position based on known UI elements like NEW PROJECT button"""
        try:
            print(f"[SEARCH_INFERENCE] Attempting to infer search icon position...")
            
            # First, find the NEW PROJECT button area
            new_coord = await self.ocr_engine.find_text_on_screen("NEW", screenshot_base64)
            project_coord = await self.ocr_engine.find_text_on_screen("PROJECT", screenshot_base64)
            
            if new_coord and project_coord:
                # Calculate center point between NEW and PROJECT
                center_x = (new_coord[0] + project_coord[0]) // 2
                center_y = (new_coord[1] + project_coord[1]) // 2
                
                print(f"[SEARCH_INFERENCE] Found NEW at {new_coord}, PROJECT at {project_coord}")
                print(f"[SEARCH_INFERENCE] Center point: ({center_x}, {center_y})")
                
                # Search icon is typically to the left of NEW PROJECT button
                # Try multiple positions to the left
                search_positions = [
                    [center_x - 100, center_y],  # 100px left
                    [center_x - 150, center_y],  # 150px left  
                    [center_x - 200, center_y],  # 200px left
                    [new_coord[0] - 80, new_coord[1]],  # 80px left of NEW
                    [new_coord[0] - 120, new_coord[1]],  # 120px left of NEW
                ]
                
                for pos in search_positions:
                    x, y = pos
                    print(f"[SEARCH_INFERENCE] Trying position ({x}, {y})")
                    # Return the first reasonable position (we could add more validation here)
                    if x > 50:  # Make sure we're not too close to screen edge
                        print(f"[SEARCH_INFERENCE] ✅ Using inferred search position: [{x}, {y}]")
                        return [x, y]
            
            # Fallback: try to find other UI indicators
            # Look for "default" project and infer search position relative to that
            default_coord = await self.ocr_engine.find_text_on_screen("default", screenshot_base64)
            if default_coord:
                # Search is often above or to the left of project listings
                fallback_x = default_coord[0] - 50
                fallback_y = default_coord[1] - 50
                if fallback_x > 50 and fallback_y > 50:
                    print(f"[SEARCH_INFERENCE] ✅ Using fallback search position: [{fallback_x}, {fallback_y}]")
                    return [fallback_x, fallback_y]
            
            print(f"[SEARCH_INFERENCE] ❌ Could not infer search position")
            return None
            
        except Exception as e:
            print(f"[SEARCH_INFERENCE] Error in search position inference: {e}")
            return None

    async def _find_using_vision_fallback(self, target: str, screenshot_base64: str) -> Optional[List[int]]:
        """Generic vision/template fallback when OCR fails"""
        try:
            print(f"[VISION_FALLBACK] Attempting vision-based detection for: '{target}'")
            
            # Try template matching if templates are available
            template_coordinate = await self._try_template_matching(target, screenshot_base64)
            if template_coordinate:
                print(f"[VISION_FALLBACK] ✅ Template matching found target at {template_coordinate}")
                return template_coordinate
            
            # If no templates available, this method returns None
            # In the future, could add other vision techniques like:
            # - Icon recognition
            # - Shape detection
            # - Color-based detection
            
            print(f"[VISION_FALLBACK] ❌ No vision fallback available for '{target}'")
            return None
            
        except Exception as e:
            print(f"[VISION_FALLBACK] Error in vision fallback: {e}")
            return None

    async def _try_template_matching(self, target: str, screenshot_base64: str) -> Optional[List[int]]:
        """Try template matching for specific elements"""
        try:
            # Only attempt template matching if templates directory exists
            if not os.path.exists(self.templates_dir):
                print(f"[TEMPLATE] No templates directory found at {self.templates_dir}")
                return None
            
            # Look for template files that might match the target
            target_lower = target.lower().replace(' ', '_')
            possible_templates = [
                f"{target_lower}.png",
                f"{target_lower}_button.png",
                f"{target_lower}_icon.png"
            ]
            
            for template_name in possible_templates:
                template_path = os.path.join(self.templates_dir, template_name)
                if os.path.exists(template_path):
                    print(f"[TEMPLATE] Found template: {template_path}")
                    coordinates = await self._match_template(screenshot_base64, template_path)
                    if coordinates:
                        return coordinates
            
            print(f"[TEMPLATE] No matching templates found for '{target}'")
            return None
            
        except Exception as e:
            print(f"[TEMPLATE] Error in template matching: {e}")
            return None

    async def _match_template(self, screenshot_base64: str, template_path: str) -> Optional[List[int]]:
        """Perform template matching between screenshot and template"""
        try:
            import cv2
            import numpy as np
            
            # Save screenshot to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_screenshot:
                screenshot_data = base64.b64decode(screenshot_base64)
                temp_screenshot.write(screenshot_data)
                temp_screenshot_path = temp_screenshot.name
            
            try:
                # Load images
                screenshot = cv2.imread(temp_screenshot_path)
                template = cv2.imread(template_path)
                
                if screenshot is None or template is None:
                    return None
                
                # Perform template matching
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Check if match is good enough
                if max_val > 0.7:  # 70% confidence threshold
                    # Calculate center of template
                    h, w = template.shape[:2]
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    print(f"[TEMPLATE] Match found with confidence {max_val:.2f} at ({center_x}, {center_y})")
                    return [center_x, center_y]
                else:
                    print(f"[TEMPLATE] Match confidence too low: {max_val:.2f}")
                    return None
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_screenshot_path)
                except:
                    pass
                    
        except ImportError:
            print(f"[TEMPLATE] OpenCV not available for template matching")
            return None
        except Exception as e:
            print(f"[TEMPLATE] Error in template matching: {e}")
            return None