import base64
from typing import Optional, Tuple, List
import asyncio

# Optional imports for vision capabilities
try:
    import cv2
    import numpy as np
    from PIL import Image
    HAS_VISION = True
except ImportError:
    HAS_VISION = False


class ScreenAnalyzer:
    """
    Analyzes screenshots to find UI elements dynamically.
    This reduces reliance on hardcoded coordinates.
    """
    
    def __init__(self):
        self.confidence_threshold = 0.8
        
    def base64_to_opencv(self, base64_image: str):
        """Convert base64 image to OpenCV format"""
        if not HAS_VISION:
            raise ImportError("OpenCV not available. Install with: pip install opencv-python")
        image_data = base64.b64decode(base64_image)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
        
    def find_button_by_text_area(self, image: np.ndarray, text_region: Tuple[int, int, int, int]) -> Optional[Tuple[int, int]]:
        """
        Find a clickable button near a text region.
        This is a simplified approach - in production you'd use OCR.
        """
        x, y, w, h = text_region
        # Return center of the text region as click point
        return (x + w // 2, y + h // 2)
        
    def find_add_new_sheet_button(self, base64_image: str) -> Optional[Tuple[int, int]]:
        """
        Find the 'Add new sheet' button in the screenshot.
        Uses color and pattern matching.
        """
        image = self.base64_to_opencv(base64_image)
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Look for blue-ish colors (common in buttons)
        # These ranges might need adjustment based on the actual app colors
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for button-like shapes (rectangular contours)
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 5000:  # Filter by size
                x, y, w, h = cv2.boundingRect(contour)
                # Check if it's roughly button-shaped
                if 0.3 < h/w < 3:  # Reasonable aspect ratio
                    return (x + w // 2, y + h // 2)
                    
        # Fallback: return approximate location based on screenshots
        # From ss02.png, the "Add new sheet" appears around the center
        height, width = image.shape[:2]
        return (width // 2, height // 2)
        
    def find_project_in_list(self, base64_image: str, project_name: str) -> Optional[Tuple[int, int]]:
        """
        Find a project in the project list.
        This is a placeholder for proper OCR implementation.
        """
        image = self.base64_to_opencv(base64_image)
        
        # For now, return approximate coordinates based on the screenshot
        # In a real implementation, you'd use OCR to find the text
        
        if project_name.lower() == "default":
            # From ss01.png, default project is roughly here
            return (400, 220)
        else:
            # For other projects, assume they're in a similar location
            # You'd need OCR to find the exact text
            return (400, 220)
            
    def find_search_box(self, base64_image: str) -> Optional[Tuple[int, int]]:
        """Find the search box in the project selection screen"""
        image = self.base64_to_opencv(base64_image)
        
        # Look for input field characteristics
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look for rectangular regions that might be input fields
        # This is a simplified approach
        height, width = gray.shape
        
        # From ss01.png, search appears to be in the upper area
        return (width // 2, 180)
        
    def detect_file_dialog(self, base64_image: str) -> bool:
        """Detect if a file dialog is open"""
        image = self.base64_to_opencv(base64_image)
        
        # Look for common file dialog characteristics
        # This is a placeholder - you'd look for specific UI elements
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look for typical file dialog patterns
        # For now, assume it's open if we call this method
        return True
        
    def find_file_in_dialog(self, base64_image: str, filename: str) -> Optional[Tuple[int, int]]:
        """Find a specific file in the file dialog"""
        # This would require OCR to read file names
        # For now, return a generic location where files typically appear
        image = self.base64_to_opencv(base64_image)
        height, width = image.shape[:2]
        
        # Files typically appear in the center-left area of file dialogs
        return (width // 3, height // 2)
        
    async def wait_for_element(self, automation_instance, element_finder, timeout: int = 10) -> Optional[Tuple[int, int]]:
        """
        Wait for a UI element to appear and return its coordinates.
        
        Args:
            automation_instance: Instance of OrcaSheetsAutomation
            element_finder: Function that takes base64_image and returns coordinates
            timeout: Maximum time to wait in seconds
        """
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            screenshot = await automation_instance._take_screenshot()
            if screenshot.base64_image:
                coords = element_finder(screenshot.base64_image)
                if coords:
                    return coords
                    
            await asyncio.sleep(0.5)
            
        return None
        
    def analyze_screen_state(self, base64_image: str) -> dict:
        """
        Analyze the current screen state to determine what UI elements are visible.
        Returns a dictionary describing the current state.
        """
        image = self.base64_to_opencv(base64_image)
        
        # This is a placeholder for more sophisticated screen analysis
        # You could detect:
        # - Whether we're on the project selection screen
        # - Whether we're in the main app
        # - Whether a dialog is open
        # - What buttons/elements are visible
        
        height, width = image.shape[:2]
        
        state = {
            "screen_width": width,
            "screen_height": height,
            "has_project_selection": False,  # Would detect based on UI elements
            "has_main_interface": False,     # Would detect based on UI elements
            "has_dialog_open": False,        # Would detect based on UI elements
            "detected_buttons": [],          # Would list detected clickable elements
            "detected_text_regions": []      # Would list detected text areas
        }
        
        return state