"""
Icon Detection System using Computer Vision and Template Matching
Specialized for detecting and locating small UI icons
"""

import os
import base64
import io
import tempfile
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IconDetector:
    """Computer vision-based icon detection system"""
    
    def __init__(self, templates_dir: str = None):
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(__file__), '..', '..', 'templates', 'icons'
        )
        self.confidence_threshold = 0.7  # Default confidence for icon matching
        self.multi_scale_factors = [0.5, 0.75, 1.0, 1.25, 1.5]  # For different icon sizes
        
        # Ensure templates directory exists
        Path(self.templates_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"[ICON_DETECTOR] Initialized with templates directory: {self.templates_dir}")
    
    async def find_icon(self, icon_name: str, screenshot_base64: str, confidence: float = None) -> Optional[List[int]]:
        """
        Find an icon on screen using multiple detection methods
        
        Args:
            icon_name: Name of the icon to find (e.g., 'search', 'add', 'settings')
            screenshot_base64: Base64 encoded screenshot
            confidence: Confidence threshold (0.0 to 1.0)
            
        Returns:
            [x, y] coordinates if icon found, None otherwise
        """
        try:
            confidence = confidence or self.confidence_threshold
            print(f"[ICON_DETECTOR] Searching for icon: '{icon_name}' with confidence {confidence}")
            
            # Method 1: Template matching with stored templates
            template_result = await self._template_matching(icon_name, screenshot_base64, confidence)
            if template_result:
                print(f"[ICON_DETECTOR] ✅ Template matching found '{icon_name}' at {template_result}")
                return template_result
            
            # Method 2: Feature-based detection (for common UI elements)
            feature_result = await self._feature_based_detection(icon_name, screenshot_base64)
            if feature_result:
                print(f"[ICON_DETECTOR] ✅ Feature detection found '{icon_name}' at {feature_result}")
                return feature_result
            
            # Method 3: Shape and color-based detection
            shape_result = await self._shape_based_detection(icon_name, screenshot_base64)
            if shape_result:
                print(f"[ICON_DETECTOR] ✅ Shape detection found '{icon_name}' at {shape_result}")
                return shape_result
            
            print(f"[ICON_DETECTOR] ❌ Icon '{icon_name}' not found using any method")
            return None
            
        except Exception as e:
            print(f"[ICON_DETECTOR] Error finding icon '{icon_name}': {e}")
            return None
    
    async def _template_matching(self, icon_name: str, screenshot_base64: str, confidence: float) -> Optional[List[int]]:
        """Template matching with multi-scale detection for small icons"""
        try:
            # Check if OpenCV is available
            try:
                import cv2
            except ImportError:
                print("[ICON_DETECTOR] OpenCV not available for template matching")
                return None
            
            # Find template files for this icon
            template_files = self._find_template_files(icon_name)
            if not template_files:
                print(f"[ICON_DETECTOR] No template files found for icon '{icon_name}'")
                return None
            
            # Decode screenshot
            screenshot_data = base64.b64decode(screenshot_base64)
            screenshot_image = Image.open(io.BytesIO(screenshot_data))
            
            # Convert to OpenCV format
            screenshot_cv = cv2.cvtColor(np.array(screenshot_image), cv2.COLOR_RGB2BGR)
            
            best_match = None
            best_confidence = 0
            
            # Try each template file
            for template_path in template_files:
                print(f"[ICON_DETECTOR] Trying template: {template_path}")
                
                # Load template
                template = cv2.imread(template_path)
                if template is None:
                    continue
                
                # Multi-scale template matching for different icon sizes
                for scale in self.multi_scale_factors:
                    scaled_template = self._resize_template(template, scale)
                    if scaled_template is None:
                        continue
                    
                    # Perform template matching
                    result = cv2.matchTemplate(screenshot_cv, scaled_template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    print(f"[ICON_DETECTOR] Scale {scale:.2f}: confidence {max_val:.3f}")
                    
                    if max_val > best_confidence and max_val >= confidence:
                        best_confidence = max_val
                        h, w = scaled_template.shape[:2]
                        center_x = max_loc[0] + w // 2
                        center_y = max_loc[1] + h // 2
                        best_match = [center_x, center_y]
                        print(f"[ICON_DETECTOR] New best match at scale {scale:.2f}: {best_match} (confidence: {best_confidence:.3f})")
            
            if best_match:
                print(f"[ICON_DETECTOR] Template matching successful: {best_match} (confidence: {best_confidence:.3f})")
                return best_match
            else:
                print(f"[ICON_DETECTOR] Template matching failed (best confidence: {best_confidence:.3f})")
                return None
                
        except Exception as e:
            print(f"[ICON_DETECTOR] Error in template matching: {e}")
            return None
    
    async def _feature_based_detection(self, icon_name: str, screenshot_base64: str) -> Optional[List[int]]:
        """Feature-based detection for common UI icons"""
        try:
            # This method detects common UI icons by their visual features
            icon_detectors = {
                'search': self._detect_search_icon,
                'magnifying_glass': self._detect_search_icon,
                'add': self._detect_add_icon,
                'plus': self._detect_add_icon,
                'settings': self._detect_settings_icon,
                'gear': self._detect_settings_icon,
                'close': self._detect_close_icon,
                'x': self._detect_close_icon,
                'menu': self._detect_menu_icon,
                'hamburger': self._detect_menu_icon,
                'play': self._detect_play_icon,
                'pause': self._detect_pause_icon,
                'stop': self._detect_stop_icon,
                'home': self._detect_home_icon,
                'back': self._detect_back_icon,
                'forward': self._detect_forward_icon,
                'refresh': self._detect_refresh_icon,
                'download': self._detect_download_icon,
                'upload': self._detect_upload_icon,
                'edit': self._detect_edit_icon,
                'delete': self._detect_delete_icon,
                'trash': self._detect_delete_icon,
                'save': self._detect_save_icon,
                'share': self._detect_share_icon
            }
            
            detector = icon_detectors.get(icon_name.lower())
            if detector:
                return await detector(screenshot_base64)
            else:
                print(f"[ICON_DETECTOR] No feature detector available for '{icon_name}'")
                return None
                
        except Exception as e:
            print(f"[ICON_DETECTOR] Error in feature-based detection: {e}")
            return None
    
    async def _shape_based_detection(self, icon_name: str, screenshot_base64: str) -> Optional[List[int]]:
        """Shape and color-based detection for icons"""
        try:
            # This method detects icons by their geometric shapes
            shape_detectors = {
                'circle': self._detect_circular_icons,
                'square': self._detect_square_icons,
                'triangle': self._detect_triangular_icons,
                'arrow': self._detect_arrow_icons
            }
            
            # Try shape-based detection based on icon name
            for shape, detector in shape_detectors.items():
                if shape in icon_name.lower():
                    return await detector(screenshot_base64)
            
            return None
            
        except Exception as e:
            print(f"[ICON_DETECTOR] Error in shape-based detection: {e}")
            return None
    
    def _find_template_files(self, icon_name: str) -> List[str]:
        """Find all template files for a given icon name"""
        templates = []
        
        # Common file extensions for icon templates
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        
        # Common naming patterns
        patterns = [
            f"{icon_name}",
            f"{icon_name}_icon",
            f"{icon_name}_button",
            f"icon_{icon_name}",
            f"btn_{icon_name}",
            f"{icon_name}_small",
            f"{icon_name}_large"
        ]
        
        for pattern in patterns:
            for ext in extensions:
                template_path = os.path.join(self.templates_dir, f"{pattern}{ext}")
                if os.path.exists(template_path):
                    templates.append(template_path)
        
        return templates
    
    def _resize_template(self, template: np.ndarray, scale: float) -> Optional[np.ndarray]:
        """Resize template for multi-scale matching"""
        try:
            import cv2
            
            h, w = template.shape[:2]
            new_h, new_w = int(h * scale), int(w * scale)
            
            # Don't resize if too small or too large
            if new_h < 5 or new_w < 5 or new_h > 200 or new_w > 200:
                return None
                
            return cv2.resize(template, (new_w, new_h))
            
        except Exception as e:
            print(f"[ICON_DETECTOR] Error resizing template: {e}")
            return None
    
    # Feature-based icon detectors
    async def _detect_search_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect magnifying glass/search icons"""
        try:
            import cv2
            
            # Decode screenshot
            screenshot_data = base64.b64decode(screenshot_base64)
            image = Image.open(io.BytesIO(screenshot_data))
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Detect circles (magnifying glass lens)
            circles = cv2.HoughCircles(
                img_cv,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=20,
                param1=50,
                param2=30,
                minRadius=5,
                maxRadius=25
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                
                # Look for circles that might be magnifying glass icons
                for (x, y, r) in circles:
                    # Check if there's a handle-like structure near the circle
                    if self._has_search_handle(img_cv, x, y, r):
                        print(f"[ICON_DETECTOR] Found search icon at ({x}, {y})")
                        return [int(x), int(y)]
            
            return None
            
        except Exception as e:
            print(f"[ICON_DETECTOR] Error detecting search icon: {e}")
            return None
    
    async def _detect_add_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect plus/add icons"""
        try:
            import cv2
            
            # Decode screenshot
            screenshot_data = base64.b64decode(screenshot_base64)
            image = Image.open(io.BytesIO(screenshot_data))
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Create a plus-shaped kernel
            kernel_size = 15
            plus_kernel = np.zeros((kernel_size, kernel_size), dtype=np.uint8)
            center = kernel_size // 2
            
            # Horizontal line
            plus_kernel[center, :] = 1
            # Vertical line  
            plus_kernel[:, center] = 1
            
            # Template matching with plus shape
            result = cv2.matchTemplate(img_cv, plus_kernel * 255, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > 0.6:  # Lower threshold for simple shapes
                center_x = max_loc[0] + kernel_size // 2
                center_y = max_loc[1] + kernel_size // 2
                print(f"[ICON_DETECTOR] Found add icon at ({center_x}, {center_y})")
                return [center_x, center_y]
            
            return None
            
        except Exception as e:
            print(f"[ICON_DETECTOR] Error detecting add icon: {e}")
            return None
    
    async def _detect_settings_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect gear/settings icons"""
        try:
            import cv2
            
            # Decode screenshot
            screenshot_data = base64.b64decode(screenshot_base64)
            image = Image.open(io.BytesIO(screenshot_data))
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Detect gear-like shapes using contour analysis
            edges = cv2.Canny(img_cv, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter by area (small icons)
                area = cv2.contourArea(contour)
                if 50 < area < 500:
                    # Calculate circularity (gears are roughly circular with teeth)
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        
                        # Gears have lower circularity due to teeth
                        if 0.3 < circularity < 0.8:
                            M = cv2.moments(contour)
                            if M["m00"] != 0:
                                cx = int(M["m10"] / M["m00"])
                                cy = int(M["m01"] / M["m00"])
                                print(f"[ICON_DETECTOR] Found settings icon at ({cx}, {cy})")
                                return [cx, cy]
            
            return None
            
        except Exception as e:
            print(f"[ICON_DETECTOR] Error detecting settings icon: {e}")
            return None
    
    async def _detect_close_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect X/close icons"""
        try:
            import cv2
            
            # Decode screenshot
            screenshot_data = base64.b64decode(screenshot_base64)
            image = Image.open(io.BytesIO(screenshot_data))
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Create X-shaped kernels of different sizes
            for size in [10, 15, 20]:
                x_kernel = np.zeros((size, size), dtype=np.uint8)
                
                # Create X pattern
                for i in range(size):
                    x_kernel[i, i] = 1  # Main diagonal
                    x_kernel[i, size-1-i] = 1  # Anti-diagonal
                
                # Template matching
                result = cv2.matchTemplate(img_cv, x_kernel * 255, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > 0.5:
                    center_x = max_loc[0] + size // 2
                    center_y = max_loc[1] + size // 2
                    print(f"[ICON_DETECTOR] Found close icon at ({center_x}, {center_y})")
                    return [center_x, center_y]
            
            return None
            
        except Exception as e:
            print(f"[ICON_DETECTOR] Error detecting close icon: {e}")
            return None
    
    async def _detect_menu_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect hamburger menu icons (three horizontal lines)"""
        try:
            import cv2
            
            # Decode screenshot
            screenshot_data = base64.b64decode(screenshot_base64)
            image = Image.open(io.BytesIO(screenshot_data))
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Create hamburger menu kernel (three horizontal lines)
            kernel_h, kernel_w = 20, 15
            menu_kernel = np.zeros((kernel_h, kernel_w), dtype=np.uint8)
            
            # Three horizontal lines
            line_positions = [4, 10, 16]
            for pos in line_positions:
                menu_kernel[pos, 2:kernel_w-2] = 255
            
            # Template matching
            result = cv2.matchTemplate(img_cv, menu_kernel, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > 0.6:
                center_x = max_loc[0] + kernel_w // 2
                center_y = max_loc[1] + kernel_h // 2
                print(f"[ICON_DETECTOR] Found menu icon at ({center_x}, {center_y})")
                return [center_x, center_y]
            
            return None
            
        except Exception as e:
            print(f"[ICON_DETECTOR] Error detecting menu icon: {e}")
            return None
    
    # Placeholder methods for other icon types
    async def _detect_play_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect play button (triangle)"""
        # Implementation for play icon detection
        return None
    
    async def _detect_pause_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect pause button (two vertical bars)"""
        # Implementation for pause icon detection
        return None
    
    async def _detect_stop_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect stop button (square)"""
        # Implementation for stop icon detection
        return None
    
    async def _detect_home_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect home icon (house shape)"""
        # Implementation for home icon detection
        return None
    
    async def _detect_back_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect back arrow"""
        # Implementation for back arrow detection
        return None
    
    async def _detect_forward_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect forward arrow"""
        # Implementation for forward arrow detection
        return None
    
    async def _detect_refresh_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect refresh/reload icon"""
        # Implementation for refresh icon detection
        return None
    
    async def _detect_download_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect download icon"""
        # Implementation for download icon detection
        return None
    
    async def _detect_upload_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect upload icon"""
        # Implementation for upload icon detection
        return None
    
    async def _detect_edit_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect edit icon (pencil)"""
        # Implementation for edit icon detection
        return None
    
    async def _detect_delete_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect delete/trash icon"""
        # Implementation for delete icon detection
        return None
    
    async def _detect_save_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect save icon (floppy disk)"""
        # Implementation for save icon detection
        return None
    
    async def _detect_share_icon(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect share icon"""
        # Implementation for share icon detection
        return None
    
    # Shape-based detectors
    async def _detect_circular_icons(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect circular icons"""
        # Implementation for circular icon detection
        return None
    
    async def _detect_square_icons(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect square icons"""
        # Implementation for square icon detection
        return None
    
    async def _detect_triangular_icons(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect triangular icons"""
        # Implementation for triangular icon detection
        return None
    
    async def _detect_arrow_icons(self, screenshot_base64: str) -> Optional[List[int]]:
        """Detect arrow-shaped icons"""
        # Implementation for arrow icon detection
        return None
    
    def _has_search_handle(self, img: np.ndarray, x: int, y: int, radius: int) -> bool:
        """Check if a circle has a handle-like structure (for magnifying glass)"""
        try:
            import cv2
            
            # Look for lines extending from the circle (magnifying glass handle)
            # Check several angles around the circle
            angles = np.linspace(0, 2*np.pi, 8)
            
            for angle in angles:
                # Point on circle circumference
                start_x = int(x + radius * np.cos(angle))
                start_y = int(y + radius * np.sin(angle))
                
                # Point further out (potential handle end)
                end_x = int(x + (radius + 10) * np.cos(angle))
                end_y = int(y + (radius + 10) * np.sin(angle))
                
                # Check if there's a line-like structure
                if (0 <= start_x < img.shape[1] and 0 <= start_y < img.shape[0] and
                    0 <= end_x < img.shape[1] and 0 <= end_y < img.shape[0]):
                    
                    # Sample pixels along the potential handle
                    line_pixels = []
                    steps = 5
                    for i in range(steps):
                        t = i / (steps - 1)
                        px = int(start_x + t * (end_x - start_x))
                        py = int(start_y + t * (end_y - start_y))
                        if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                            line_pixels.append(img[py, px])
                    
                    # If most pixels are dark (indicating a line), this might be a handle
                    if line_pixels and np.mean(line_pixels) < 100:  # Dark pixels
                        return True
            
            return False
            
        except Exception as e:
            print(f"[ICON_DETECTOR] Error checking search handle: {e}")
            return False
    
    def save_icon_template(self, icon_name: str, screenshot_base64: str, 
                          coordinates: List[int], crop_size: int = 50) -> str:
        """
        Save a cropped icon as a template for future use
        
        Args:
            icon_name: Name to save the template as
            screenshot_base64: Screenshot containing the icon
            coordinates: [x, y] center coordinates of the icon
            crop_size: Size of the square crop around the icon
            
        Returns:
            Path to saved template file
        """
        try:
            # Decode screenshot
            screenshot_data = base64.b64decode(screenshot_base64)
            image = Image.open(io.BytesIO(screenshot_data))
            
            # Calculate crop box
            x, y = coordinates
            half_size = crop_size // 2
            
            left = max(0, x - half_size)
            top = max(0, y - half_size)
            right = min(image.width, x + half_size)
            bottom = min(image.height, y + half_size)
            
            # Crop icon
            icon_crop = image.crop((left, top, right, bottom))
            
            # Save template
            template_path = os.path.join(self.templates_dir, f"{icon_name}.png")
            icon_crop.save(template_path)
            
            print(f"[ICON_DETECTOR] Saved icon template: {template_path}")
            return template_path
            
        except Exception as e:
            print(f"[ICON_DETECTOR] Error saving icon template: {e}")
            return ""