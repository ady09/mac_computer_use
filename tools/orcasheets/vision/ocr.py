from PIL import Image
import pytesseract
from typing import Tuple, Optional

def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image file using pytesseract."""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def find_text_location(image_path: str, target_text: str) -> Optional[Tuple[int, int]]:
    """
    Find the center coordinates of target text in an image.
    Returns (x, y) coordinates or None if not found.
    """
    try:
        image = Image.open(image_path)
        # Get bounding boxes for all text
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # Look for the target text (case insensitive)
        target_lower = target_text.lower()
        
        for i, text in enumerate(data['text']):
            if text.strip() and target_lower in text.lower():
                # Get bounding box coordinates
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                
                # Return center coordinates
                center_x = x + w // 2
                center_y = y + h // 2
                print(f"[DEBUG] Found '{target_text}' at ({center_x}, {center_y})")
                return (center_x, center_y)
        
        # If exact match not found, try partial matching with individual words
        words = target_text.lower().split()
        for word in words:
            if len(word) >= 3:  # Only check words with 3+ characters
                for i, text in enumerate(data['text']):
                    if text.strip() and word in text.lower():
                        x = data['left'][i]
                        y = data['top'][i]
                        w = data['width'][i]
                        h = data['height'][i]
                        center_x = x + w // 2
                        center_y = y + h // 2
                        print(f"[DEBUG] Found partial match '{word}' from '{target_text}' at ({center_x}, {center_y})")
                        return (center_x, center_y)
        
        print(f"[DEBUG] Text '{target_text}' not found in image")
        return None
        
    except Exception as e:
        print(f"[DEBUG] OCR error: {e}")
        return None 