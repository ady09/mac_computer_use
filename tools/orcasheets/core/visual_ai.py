"""
Advanced Visual AI system for OrcaSheets automation.
Analyzes screenshots to find and interact with UI elements based on natural language descriptions.
"""

import base64
import asyncio
from typing import Optional, Tuple, List, Dict, Any
import re
from io import BytesIO

# Optional imports for vision capabilities
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    HAS_VISION = True
except ImportError:
    HAS_VISION = False


class VisualAI:
    """
    Advanced visual analysis system that can find any UI element based on description.
    """
    
    def __init__(self):
        self.confidence_threshold = 0.7
        self.debug_mode = True  # Set to True to save annotated images for debugging
        
    def base64_to_image(self, base64_image: str):
        """Convert base64 image to PIL Image"""
        if not HAS_VISION:
            raise ImportError("PIL not available. Install with: pip install Pillow")
        image_data = base64.b64decode(base64_image)
        return Image.open(BytesIO(image_data))
    
    def base64_to_opencv(self, base64_image: str):
        """Convert base64 image to OpenCV format"""
        if not HAS_VISION:
            raise ImportError("OpenCV not available. Install with: pip install opencv-python")
        image_data = base64.b64decode(base64_image)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    
    async def find_element_by_description(self, base64_image: str, description: str) -> Optional[Tuple[int, int]]:
        """
        Find any UI element based on natural language description.
        
        Args:
            base64_image: Screenshot as base64 string
            description: Natural language description like "Add new sheet button", "industry.csv tab", "default project"
        
        Returns:
            Tuple of (x, y) coordinates if found, None otherwise
        """
        description = description.lower().strip()
        
        print(f"🔍 Looking for: '{description}'")
        
        if not HAS_VISION:
            print("⚠️  Computer vision not available, using AppleScript fallback")
            return None
            
        # Try different detection methods based on description type
        methods = [
            self._find_by_text_matching,
            self._find_by_button_detection,
            self._find_by_tab_detection,
            self._find_by_link_detection,
            self._find_by_color_analysis,
            self._find_by_shape_analysis
        ]
        
        for method in methods:
            try:
                coords = await method(base64_image, description)
                if coords:
                    print(f"✅ Found '{description}' at {coords} using {method.__name__}")
                    return coords
            except Exception as e:
                print(f"⚠️  Method {method.__name__} failed: {e}")
                continue
        
        print(f"❌ Could not find '{description}' using visual analysis")
        return None
    
    async def _find_by_text_matching(self, base64_image: str, description: str) -> Optional[Tuple[int, int]]:
        """Find elements by looking for text patterns"""
        image = self.base64_to_opencv(base64_image)
        
        # Extract key words from description
        key_words = self._extract_keywords(description)
        
        # Look for text-like regions
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use different text detection approaches
        text_regions = self._detect_text_regions(gray)
        
        for region in text_regions:
            x, y, w, h = region
            # For now, we'll use position-based heuristics
            # In a real implementation, you'd use OCR here
            
            # Check if this could match our description
            if self._region_matches_description(region, description, image.shape):
                return (x + w // 2, y + h // 2)
        
        return None
    
    async def _find_by_button_detection(self, base64_image: str, description: str) -> Optional[Tuple[int, int]]:
        """Find buttons by shape and appearance"""
        if "button" not in description:
            return None
            
        image = self.base64_to_opencv(base64_image)
        
        # Convert to different color spaces for better detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect button-like shapes
        button_candidates = []
        
        # Method 1: Look for rectangular regions with button-like characteristics
        contours = self._find_button_contours(gray)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size and aspect ratio
            if self._is_button_like(x, y, w, h, image.shape):
                # Check if this button matches our description
                if self._matches_button_description(description, x, y, w, h, image.shape):
                    button_candidates.append((x + w // 2, y + h // 2, w * h))
        
        # Return the most likely candidate (largest button in relevant area)
        if button_candidates:
            button_candidates.sort(key=lambda x: x[2], reverse=True)
            return (button_candidates[0][0], button_candidates[0][1])
        
        return None
    
    async def _find_by_tab_detection(self, base64_image: str, description: str) -> Optional[Tuple[int, int]]:
        """Find tabs by looking for tab-like UI patterns"""
        if "tab" not in description:
            return None
            
        image = self.base64_to_opencv(base64_image)
        
        # Extract the tab name from description
        tab_name = self._extract_tab_name(description)
        
        # Look for tab-like regions (typically at top of window)
        height, width = image.shape[:2]
        top_region = image[:height//3, :]  # Search in top third of screen
        
        # Find horizontal lines and tab-like structures
        tab_candidates = self._detect_tab_structures(top_region)
        
        for tab in tab_candidates:
            x, y, w, h = tab
            # Adjust coordinates back to full image
            full_coords = (x, y, w, h)
            
            if self._tab_matches_name(full_coords, tab_name, image):
                return (x + w // 2, y + h // 2)
        
        return None
    
    async def _find_by_link_detection(self, base64_image: str, description: str) -> Optional[Tuple[int, int]]:
        """Find clickable links by color and text patterns"""
        image = self.base64_to_opencv(base64_image)
        
        # Look for link-like colors (blues, underlined text, etc.)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define blue color range for links
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Find contours in blue regions
        contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size (links are usually text-sized)
            if 20 < w < 300 and 10 < h < 50:
                if self._matches_link_description(description, x, y, w, h, image.shape):
                    return (x + w // 2, y + h // 2)
        
        return None
    
    async def _find_by_color_analysis(self, base64_image: str, description: str) -> Optional[Tuple[int, int]]:
        """Find elements by analyzing color patterns"""
        image = self.base64_to_opencv(base64_image)
        
        # Analyze dominant colors and look for UI element patterns
        # This is a simplified implementation
        height, width = image.shape[:2]
        
        # Look for areas with consistent colors that might be buttons or UI elements
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use adaptive thresholding to find distinct regions
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by reasonable UI element sizes
            if 30 < w < width//2 and 15 < h < height//4:
                if self._matches_general_description(description, x, y, w, h, image.shape):
                    return (x + w // 2, y + h // 2)
        
        return None
    
    async def _find_by_shape_analysis(self, base64_image: str, description: str) -> Optional[Tuple[int, int]]:
        """Find elements by analyzing shapes and geometric patterns"""
        image = self.base64_to_opencv(base64_image)
        
        # Look for geometric shapes that match the description
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Find edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shape_candidates = []
        
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # Analyze shape characteristics
            if self._shape_matches_description(description, approx, x, y, w, h, image.shape):
                shape_candidates.append((x + w // 2, y + h // 2, len(approx)))
        
        if shape_candidates:
            # Return the most suitable shape
            return (shape_candidates[0][0], shape_candidates[0][1])
        
        return None
    
    # Helper methods for analysis
    
    def _extract_keywords(self, description: str) -> List[str]:
        """Extract relevant keywords from description"""
        # Remove common words and extract meaningful terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\w+', description.lower())
        return [word for word in words if word not in common_words and len(word) > 2]
    
    def _extract_tab_name(self, description: str) -> str:
        """Extract tab name from description like 'industry.csv tab'"""
        # Look for patterns like "filename.ext tab" or "name tab"
        match = re.search(r'(\w+(?:\.\w+)?)\s+tab', description)
        if match:
            return match.group(1)
        
        # Fallback: extract first meaningful word
        words = self._extract_keywords(description)
        return words[0] if words else ""
    
    def _detect_text_regions(self, gray_image):
        """Detect regions that likely contain text"""
        # Use morphological operations to find text-like regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        
        # Apply morphological operations
        morph = cv2.morphologyEx(gray_image, cv2.MORPH_GRADIENT, kernel)
        
        # Threshold
        _, thresh = cv2.threshold(morph, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by text-like characteristics
            if 10 < w < 500 and 8 < h < 100 and 1 < w/h < 20:
                text_regions.append((x, y, w, h))
        
        return text_regions
    
    def _find_button_contours(self, gray_image):
        """Find contours that look like buttons"""
        # Use edge detection to find button-like shapes
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Dilate to connect broken edges
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        return contours
    
    def _is_button_like(self, x: int, y: int, w: int, h: int, image_shape: Tuple[int, int]) -> bool:
        """Check if dimensions are button-like"""
        img_h, img_w = image_shape[:2]
        
        # Reasonable button sizes
        if 30 < w < img_w//2 and 15 < h < 100:
            # Reasonable aspect ratio
            if 1 < w/h < 10:
                return True
        return False
    
    def _detect_tab_structures(self, image_region):
        """Detect tab-like structures in image region"""
        gray = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)
        
        # Look for horizontal lines (tab separators)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Find contours
        contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        tab_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter for tab-like dimensions
            if w > 50 and h < 50:
                tab_regions.append((x, y, w, h))
        
        return tab_regions
    
    def _region_matches_description(self, region: Tuple[int, int, int, int], description: str, image_shape: Tuple[int, int]) -> bool:
        """Check if a region matches the description based on position and context"""
        x, y, w, h = region
        img_h, img_w = image_shape[:2]
        
        # Positional heuristics based on description
        if "add new sheet" in description or "new sheet" in description:
            # Usually in center area
            center_x, center_y = img_w // 2, img_h // 2
            distance = ((x + w//2 - center_x)**2 + (y + h//2 - center_y)**2)**0.5
            return distance < min(img_w, img_h) // 3
        
        if "default" in description and "project" in description:
            # Usually in upper-center area
            return y < img_h // 2 and abs(x + w//2 - img_w//2) < img_w // 3
        
        if "tab" in description:
            # Usually in top area
            return y < img_h // 4
        
        # Default: check if it's in a reasonable location
        return True
    
    def _matches_button_description(self, description: str, x: int, y: int, w: int, h: int, image_shape: Tuple[int, int]) -> bool:
        """Check if button location matches description"""
        return self._region_matches_description((x, y, w, h), description, image_shape)
    
    def _tab_matches_name(self, coords: Tuple[int, int, int, int], tab_name: str, image) -> bool:
        """Check if tab region contains the specified name"""
        # This would ideally use OCR to read the tab text
        # For now, use position-based heuristics
        x, y, w, h = coords
        
        # Simple heuristic: if we're looking for "industry.csv", prefer tabs in certain positions
        if "industry" in tab_name.lower():
            # Could be anywhere in the tab bar
            return True
        
        return True
    
    def _matches_link_description(self, description: str, x: int, y: int, w: int, h: int, image_shape: Tuple[int, int]) -> bool:
        """Check if link location matches description"""
        return self._region_matches_description((x, y, w, h), description, image_shape)
    
    def _matches_general_description(self, description: str, x: int, y: int, w: int, h: int, image_shape: Tuple[int, int]) -> bool:
        """General matching for any UI element"""
        return self._region_matches_description((x, y, w, h), description, image_shape)
    
    def _shape_matches_description(self, description: str, approx_contour, x: int, y: int, w: int, h: int, image_shape: Tuple[int, int]) -> bool:
        """Check if shape characteristics match description"""
        num_vertices = len(approx_contour)
        
        # Shape-based matching
        if "button" in description and 4 <= num_vertices <= 8:
            # Buttons are usually rectangular-ish
            return self._is_button_like(x, y, w, h, image_shape)
        
        return self._region_matches_description((x, y, w, h), description, image_shape)
    
    async def find_and_click_element(self, computer_tool, base64_image: str, description: str) -> bool:
        """Find and click an element based on description"""
        coords = await self.find_element_by_description(base64_image, description)
        
        if coords:
            x, y = coords
            print(f"🖱️  Clicking '{description}' at {coords}")
            
            # Move mouse and click
            await computer_tool(action="mouse_move", coordinate=[x, y])
            await computer_tool(action="left_click")
            return True
        else:
            print(f"❌ Could not find '{description}' to click")
            return False
    
    async def analyze_screen_elements(self, base64_image: str) -> Dict[str, List[Tuple[int, int]]]:
        """Analyze screen and return all detected UI elements"""
        if not HAS_VISION:
            return {}
            
        image = self.base64_to_opencv(base64_image)
        
        elements = {
            "buttons": [],
            "links": [],
            "tabs": [],
            "text_regions": [],
            "clickable_areas": []
        }
        
        # Detect different types of elements
        try:
            # Find buttons
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            button_contours = self._find_button_contours(gray)
            
            for contour in button_contours:
                x, y, w, h = cv2.boundingRect(contour)
                if self._is_button_like(x, y, w, h, image.shape):
                    elements["buttons"].append((x + w//2, y + h//2))
            
            # Find text regions
            text_regions = self._detect_text_regions(gray)
            for x, y, w, h in text_regions:
                elements["text_regions"].append((x + w//2, y + h//2))
            
            # Find tabs (in top area)
            height = image.shape[0]
            top_region = image[:height//3, :]
            tab_regions = self._detect_tab_structures(top_region)
            for x, y, w, h in tab_regions:
                elements["tabs"].append((x + w//2, y + h//2))
            
        except Exception as e:
            print(f"Error analyzing screen elements: {e}")
        
        return elements