"""
OCR engine for text detection and recognition in screenshots
"""

import base64
import io
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np


class OCREngine:
    """Main OCR engine for text detection and recognition"""
    
    def __init__(self):
        self.confidence_threshold = 0.5
        
    async def find_text_on_screen(self, text: str, screenshot_base64: str) -> Optional[List[int]]:
        """Use OCR to find text on screen and return coordinates - purely generic approach"""
        try:
            print(f"[OCR] Starting generic OCR search for: '{text}'")
            
            # Try to use OCR with pytesseract if available
            try:
                import pytesseract
                
                # Decode screenshot
                screenshot_data = base64.b64decode(screenshot_base64)
                original_image = Image.open(io.BytesIO(screenshot_data))
                
                print(f"[OCR] Applying image preprocessing for better text detection...")
                
                # Try multiple preprocessing approaches for better OCR
                ocr_results = []
                
                # Method 1: Original image (baseline)
                data_original = pytesseract.image_to_data(original_image, output_type=pytesseract.Output.DICT)
                ocr_results.append(("original", data_original, original_image.size))
                
                # Method 2: Enhanced contrast for light text on grey backgrounds
                enhanced_image = self._enhance_image_for_ocr(original_image)
                data_enhanced = pytesseract.image_to_data(enhanced_image, output_type=pytesseract.Output.DICT)
                ocr_results.append(("enhanced", data_enhanced, enhanced_image.size))
                
                # Method 3: Inverted image (white text becomes black)
                inverted_image = self._invert_image_colors(original_image)
                data_inverted = pytesseract.image_to_data(inverted_image, output_type=pytesseract.Output.DICT)
                ocr_results.append(("inverted", data_inverted, inverted_image.size))
                
                # Method 4: Specialized for grey backgrounds (threshold-based)
                threshold_image = self._apply_threshold_for_grey_backgrounds(original_image)
                data_threshold = pytesseract.image_to_data(threshold_image, output_type=pytesseract.Output.DICT)
                ocr_results.append(("threshold", data_threshold, threshold_image.size))
                
                # Combine results from all methods
                combined_data = self._combine_ocr_results(ocr_results)
                data = combined_data
                image = original_image  # Use original for coordinate calculations
                
                return self._process_ocr_results(text, data, image)
                            
            except ImportError:
                print("[OCR] ❌ pytesseract not available")
                return None
            except Exception as e:
                print(f"[OCR] ❌ OCR failed: {e}")
                return None
            
        except Exception as e:
            print(f"[OCR] Error in text detection: {e}")
            return None

    def _process_ocr_results(self, text: str, data: Dict, image: Image.Image) -> Optional[List[int]]:
        """Process OCR results and find the best match"""
        text_lower = text.lower().strip()
        
        # Debug: Show all detected text first
        print(f"[OCR] All detected text on screen:")
        all_text = []
        for i, detected_text in enumerate(data['text']):
            if detected_text and len(detected_text.strip()) > 0:
                x = data['left'][i] + data['width'][i] // 2
                y = data['top'][i] + data['height'][i] // 2
                all_text.append((detected_text.strip(), x, y))
                
        # Show limited text items for debugging (reduce screen clutter)
        print(f"[OCR] Found {len(all_text)} text items total")
        
        # Only show items that might be relevant to our target
        relevant_items = []
        target_words = text_lower.split()
        for text_item, x, y in all_text:
            # Show if it contains our target or looks like UI elements
            if (any(word in text_item.lower() for word in target_words) or
                any(ui_word in text_item.lower() for ui_word in ['button', 'default', 'new', 'add', 'project', 'sheet'])):
                relevant_items.append((text_item, x, y))
        
        if relevant_items:
            print(f"[OCR] Relevant text items found:")
            for i, (text_item, x, y) in enumerate(relevant_items[:10]):  # Show top 10 relevant items
                print(f"[OCR] {i+1}. '{text_item}' at ({x}, {y})")
        else:
            print(f"[OCR] No obviously relevant text found. Showing first 10 items:")
            for i, (text_item, x, y) in enumerate(all_text[:10]):
                print(f"[OCR] {i+1}. '{text_item}' at ({x}, {y})")
                
        # Specifically search for any text containing our target
        target_containing = [item for item in all_text if text_lower in item[0].lower()]
        if target_containing:
            print(f"[OCR] Found {len(target_containing)} text items containing '{text}':")
            for text_item, x, y in target_containing:
                # Add context information about the location
                y_percent = (y / image.size[1]) * 100
                x_percent = (x / image.size[0]) * 100
                location_desc = ""
                if y_percent < 15:
                    location_desc = "📍 TOP AREA (menu/title bar)"
                elif y_percent > 85:
                    location_desc = "📍 BOTTOM AREA (status bar)"
                elif 25 < y_percent < 75:
                    location_desc = "✅ MAIN CONTENT AREA"
                else:
                    location_desc = "📍 MIDDLE AREA"
                
                print(f"[OCR] 📍 '{text_item}' at ({x}, {y}) - {location_desc}")
        else:
            print(f"[OCR] ⚠️ No text containing '{text}' found on screen!")
        
        # Search for exact matches first
        print(f"[OCR] Searching for exact matches of '{text}'...")
        exact_matches = []
        for i, detected_text in enumerate(data['text']):
            if detected_text and len(detected_text.strip()) > 0:
                detected_lower = detected_text.lower().strip()
                if text_lower == detected_lower:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    confidence = self._calculate_generic_confidence(text, detected_text, x, y, image.size)
                    exact_matches.append((x, y, detected_text, confidence))
                    print(f"[OCR] EXACT MATCH: '{detected_text}' at ({x}, {y}) confidence: {confidence}")
        
        # If exact matches found, use the best one
        if exact_matches:
            best_match = max(exact_matches, key=lambda m: m[3])
            x, y, matched_text, conf = best_match
            print(f"[OCR] ✅ BEST EXACT MATCH! Using '{matched_text}' at ({x}, {y}) confidence: {conf}")
            return [int(x), int(y)]
        
        # Search for partial matches
        print(f"[OCR] No exact matches, searching for partial matches...")
        partial_matches = []
        for i, detected_text in enumerate(data['text']):
            if detected_text and len(detected_text.strip()) > 1:
                detected_lower = detected_text.lower().strip()
                # Check if the search text is contained in detected text
                if text_lower in detected_lower:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    confidence = self._calculate_generic_confidence(text, detected_text, x, y, image.size) - 10
                    partial_matches.append((x, y, detected_text, confidence))
                    print(f"[OCR] PARTIAL MATCH: '{detected_text}' contains '{text}' at ({x}, {y}) confidence: {confidence}")
        
        # If partial matches found, use the best one
        if partial_matches:
            best_match = max(partial_matches, key=lambda m: m[3])
            x, y, matched_text, conf = best_match
            print(f"[OCR] ✅ BEST PARTIAL MATCH! Using '{matched_text}' at ({x}, {y}) confidence: {conf}")
            return [int(x), int(y)]
        
        # Search for proximity-based multi-word matches
        search_words = text_lower.split()
        if len(search_words) > 1:
            print(f"[OCR] Searching for proximity-based multi-word matches...")
            proximity_matches = self._find_proximity_word_matches(search_words, data, image.size)
            if proximity_matches:
                best_match = max(proximity_matches, key=lambda m: m[3])
                x, y, matched_text, conf = best_match
                print(f"[OCR] ✅ BEST PROXIMITY MATCH! Using '{matched_text}' at ({x}, {y}) confidence: {conf}")
                return [int(x), int(y)]
        
        # Search for individual word-based matches (stricter criteria)
        print(f"[OCR] Searching for individual word matches...")
        word_matches = []
        
        # Only proceed with word matching if search text has multiple words or is a common UI term
        if len(search_words) > 1 or any(term in text_lower for term in ['default', 'button', 'menu', 'save', 'open', 'close', 'ok', 'cancel']):
            for i, detected_text in enumerate(data['text']):
                if detected_text and len(detected_text.strip()) > 1:
                    detected_lower = detected_text.lower().strip()
                    detected_words = detected_lower.split()
                    
                    # More strict word matching - require substantial overlap
                    matching_words = 0
                    for search_word in search_words:
                        if len(search_word) >= 3:  # Only match words with 3+ characters
                            for detected_word in detected_words:
                                if (search_word in detected_word and len(search_word) >= len(detected_word) * 0.7) or \
                                   (detected_word in search_word and len(detected_word) >= len(search_word) * 0.7):
                                    matching_words += 1
                                    break
                    
                    # Require at least 50% of search words to match
                    if matching_words >= len(search_words) * 0.5 and matching_words > 0:
                        x = data['left'][i] + data['width'][i] // 2
                        y = data['top'][i] + data['height'][i] // 2
                        confidence = self._calculate_generic_confidence(text, detected_text, x, y, image.size) - 30
                        word_matches.append((x, y, detected_text, confidence))
                        print(f"[OCR] INDIVIDUAL WORD MATCH: '{detected_text}' has {matching_words}/{len(search_words)} matching words at ({x}, {y}) confidence: {confidence}")
        
        # If word matches found, use the best one
        if word_matches:
            best_match = max(word_matches, key=lambda m: m[3])
            x, y, matched_text, conf = best_match
            print(f"[OCR] ✅ BEST INDIVIDUAL WORD MATCH! Using '{matched_text}' at ({x}, {y}) confidence: {conf}")
            return [int(x), int(y)]
        else:
            print(f"[OCR] No individual word matches found either")
        
        print(f"[OCR] ❌ No OCR matches found for '{text}'")
        return None

    def _find_proximity_word_matches(self, search_words: list, ocr_data: dict, image_size: tuple) -> list:
        """Find words that appear close to each other, like 'Add New Sheet' as separate words"""
        try:
            width, height = image_size
            matches = []
            
            # Create list of all detected words with positions
            detected_items = []
            for i, detected_text in enumerate(ocr_data['text']):
                if detected_text and len(detected_text.strip()) > 1:
                    x = ocr_data['left'][i] + ocr_data['width'][i] // 2
                    y = ocr_data['top'][i] + ocr_data['height'][i] // 2
                    detected_items.append((detected_text.lower().strip(), x, y, i))
            
            # For each search word, find nearby detected words
            for primary_word in search_words:
                if len(primary_word) < 3:  # Skip very short words
                    continue
                    
                # Find instances of this primary word
                primary_matches = []
                for detected_word, x, y, idx in detected_items:
                    if primary_word in detected_word or detected_word in primary_word:
                        if len(primary_word) >= len(detected_word) * 0.6 or len(detected_word) >= len(primary_word) * 0.6:
                            primary_matches.append((detected_word, x, y, idx))
                
                # For each primary word match, look for other search words nearby
                for primary_text, px, py, pidx in primary_matches:
                    nearby_words = [primary_text]
                    total_confidence = 50  # Base confidence for primary word
                    
                    # Look for other search words within reasonable proximity (100 pixels)
                    for other_word in search_words:
                        if other_word == primary_word:
                            continue
                        if len(other_word) < 3:
                            continue
                            
                        for detected_word, x, y, idx in detected_items:
                            if idx == pidx:  # Skip the primary word itself
                                continue
                                
                            # Check if this detected word matches the search word
                            if other_word in detected_word or detected_word in other_word:
                                if len(other_word) >= len(detected_word) * 0.6 or len(detected_word) >= len(other_word) * 0.6:
                                    # Check proximity
                                    distance = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
                                    if distance < 100:  # Within 100 pixels
                                        nearby_words.append(detected_word)
                                        total_confidence += 30
                                        break
                    
                    # If we found multiple words nearby, this is a good match
                    if len(nearby_words) >= 2:
                        combined_text = ' '.join(nearby_words)
                        # Calculate confidence including spatial quality
                        spatial_confidence = self._calculate_generic_confidence(' '.join(search_words), combined_text, px, py, image_size)
                        final_confidence = total_confidence + spatial_confidence - 50  # Adjust base
                        
                        matches.append((px, py, combined_text, final_confidence))
                        print(f"[OCR] PROXIMITY MATCH: '{combined_text}' at ({px}, {py}) confidence: {final_confidence}")
            
            return matches
            
        except Exception as e:
            print(f"[OCR] Error in proximity matching: {e}")
            return []

    def _enhance_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Enhance image contrast and sharpness for better OCR detection"""
        try:
            # Convert to grayscale first
            if image.mode != 'L':
                gray_image = image.convert('L')
            else:
                gray_image = image.copy()
            
            # Enhance contrast significantly for light text
            contrast_enhancer = ImageEnhance.Contrast(gray_image)
            high_contrast = contrast_enhancer.enhance(3.0)  # Increase contrast by 300% for very light text
            
            # Enhance sharpness
            sharpness_enhancer = ImageEnhance.Sharpness(high_contrast)
            sharp_image = sharpness_enhancer.enhance(2.0)  # Increase sharpness by 200%
            
            # Apply edge enhancement filter
            enhanced = sharp_image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            
            print(f"[OCR] Applied contrast and sharpness enhancement")
            return enhanced
            
        except Exception as e:
            print(f"[OCR] Error in image enhancement: {e}")
            return image

    def _invert_image_colors(self, image: Image.Image) -> Image.Image:
        """Invert image colors to make light text dark for better OCR"""
        try:
            # Convert to grayscale first
            if image.mode != 'L':
                gray_image = image.convert('L')
            else:
                gray_image = image.copy()
            
            # Invert colors (white becomes black, black becomes white)
            inverted = ImageOps.invert(gray_image)
            
            print(f"[OCR] Applied color inversion")
            return inverted
            
        except Exception as e:
            print(f"[OCR] Error in color inversion: {e}")
            return image

    def _apply_threshold_for_grey_backgrounds(self, image: Image.Image) -> Image.Image:
        """Apply threshold-based processing specifically for light text on grey backgrounds"""
        try:
            # Convert to grayscale first
            if image.mode != 'L':
                gray_image = image.convert('L')
            else:
                gray_image = image.copy()
            
            # Convert to numpy array for advanced processing
            img_array = np.array(gray_image)
            
            # Apply adaptive thresholding for grey backgrounds
            # This helps separate light text from grey backgrounds
            
            # Method 1: Simple threshold - pixels above certain value become white, below become black
            # Good for light text on grey backgrounds
            threshold_value = 140  # Slightly higher threshold for very light text
            binary_image = img_array.copy()
            binary_image[binary_image >= threshold_value] = 255  # Light areas become white
            binary_image[binary_image < threshold_value] = 0     # Dark areas become black
            
            # Method 2: More sophisticated - detect grey background and enhance contrast
            # Find the most common grey values (likely the background)
            hist, bin_edges = np.histogram(img_array, bins=256, range=(0, 255))
            
            # Find peaks in histogram - these are likely background colors
            peak_indices = []
            for i in range(10, 246):  # Avoid pure black/white
                if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > len(img_array.flatten()) * 0.01:
                    peak_indices.append(i)
            
            # If we found grey peaks, enhance contrast around them
            if peak_indices:
                # Use the most prominent peak as likely background
                main_peak = max(peak_indices, key=lambda i: hist[i])
                print(f"[OCR] Detected likely grey background at value {main_peak}")
                
                # Create enhanced version targeting this background
                enhanced_array = img_array.copy().astype(np.float32)
                
                # Enhance contrast around the background value
                # Pixels close to background become darker, others lighter
                for i in range(enhanced_array.shape[0]):
                    for j in range(enhanced_array.shape[1]):
                        pixel_val = enhanced_array[i, j]
                        diff_from_bg = abs(pixel_val - main_peak)
                        
                        if diff_from_bg < 30:  # Close to background
                            # This is likely background, make it darker
                            enhanced_array[i, j] = max(0, pixel_val - 40)
                        elif pixel_val > main_peak:
                            # Lighter than background, make it much lighter
                            enhanced_array[i, j] = min(255, pixel_val + 50)
                        else:
                            # Darker than background, make it much darker
                            enhanced_array[i, j] = max(0, pixel_val - 30)
                
                # Convert back to PIL Image
                enhanced_array = np.clip(enhanced_array, 0, 255).astype(np.uint8)
                threshold_image = Image.fromarray(enhanced_array)
            else:
                # Fallback to simple binary threshold
                threshold_image = Image.fromarray(binary_image)
            
            print(f"[OCR] Applied grey background threshold processing")
            return threshold_image
            
        except Exception as e:
            print(f"[OCR] Error in grey background threshold processing: {e}")
            return image

    def _combine_ocr_results(self, ocr_results: List[Tuple[str, Dict, Tuple]]) -> Dict:
        """Combine OCR results from multiple preprocessing methods"""
        try:
            print(f"[OCR] Combining results from {len(ocr_results)} preprocessing methods...")
            
            combined_text = []
            combined_left = []
            combined_top = []
            combined_width = []
            combined_height = []
            combined_conf = []
            
            # Track unique text items to avoid duplicates
            seen_items = set()
            
            for method_name, data, image_size in ocr_results:
                method_items = 0
                for i, text_item in enumerate(data['text']):
                    if text_item and len(text_item.strip()) > 0:
                        # Create a unique key based on text and approximate position
                        x = data['left'][i] + data['width'][i] // 2
                        y = data['top'][i] + data['height'][i] // 2
                        # Round position to nearest 20 pixels to group similar locations
                        pos_key = (text_item.strip().lower(), round(x/20)*20, round(y/20)*20)
                        
                        if pos_key not in seen_items:
                            seen_items.add(pos_key)
                            combined_text.append(text_item)
                            combined_left.append(data['left'][i])
                            combined_top.append(data['top'][i])
                            combined_width.append(data['width'][i])
                            combined_height.append(data['height'][i])
                            combined_conf.append(data.get('conf', [0])[i] if i < len(data.get('conf', [])) else 50)
                            method_items += 1
                
                print(f"[OCR] {method_name} method contributed {method_items} unique text items")
            
            # Create combined data structure
            combined_data = {
                'text': combined_text,
                'left': combined_left,
                'top': combined_top,
                'width': combined_width,
                'height': combined_height,
                'conf': combined_conf
            }
            
            print(f"[OCR] Combined total: {len(combined_text)} unique text items")
            return combined_data
            
        except Exception as e:
            print(f"[OCR] Error combining results: {e}")
            # Fallback to first result
            return ocr_results[0][1] if ocr_results else {'text': [], 'left': [], 'top': [], 'width': [], 'height': [], 'conf': []}

    def _calculate_generic_confidence(self, target_text: str, detected_text: str, x: int, y: int, image_size: tuple) -> float:
        """Calculate confidence score for detected text match - completely generic"""
        confidence = 0.0
        width, height = image_size
        
        # Base confidence from text matching quality
        if target_text.lower().strip() == detected_text.lower().strip():
            confidence += 100  # Exact match
        elif target_text.lower() in detected_text.lower():
            confidence += 50   # Partial match
        else:
            confidence += 20   # Word match
        
        # Generic UI element quality scoring
        # Favor shorter text (likely to be buttons/labels vs paragraphs)
        if len(detected_text) <= 20:
            confidence += 20
        elif len(detected_text) <= 50:
            confidence += 10
        else:
            confidence -= 10  # Long text less likely to be clickable UI
        
        # Penalize file paths and technical text (universal patterns)
        if '/' in detected_text and len(detected_text) > 10:
            confidence -= 60
            print(f"[CONFIDENCE] Heavy file path penalty: '{detected_text}'")
        if any(tech in detected_text.lower() for tech in ['.com', '.org', 'http', 'www', 'file:', 'path:', '@', 'users', 'library', 'application']):
            confidence -= 50
            print(f"[CONFIDENCE] Technical text penalty: '{detected_text}'")
        if any(code in detected_text for code in ['/', '\\', ':', ';', '{', '}', '<', '>']):
            confidence -= 25
            print(f"[CONFIDENCE] Code/symbol penalty: '{detected_text}'")
        
        # Extra penalty for long paths or technical strings
        if len(detected_text) > 30 and ('/' in detected_text or '\\' in detected_text):
            confidence -= 40
            print(f"[CONFIDENCE] Long path penalty: '{detected_text}'")
        
        # Favor standalone words that match the target exactly
        if target_text.lower().strip() == detected_text.lower().strip() and len(detected_text.strip()) < 15:
            confidence += 30
            print(f"[CONFIDENCE] Standalone word bonus: '{detected_text}'")
        
        # Heavily penalize menu bar and title bar areas (top 15% of screen)
        if y < height * 0.15:
            confidence -= 50
            print(f"[CONFIDENCE] Penalizing menu/title bar text: '{detected_text}' at y={y} (top {y/height:.1%})")
        
        # Penalize very top edge (likely app name, window controls)
        if y < height * 0.08:
            confidence -= 30
            print(f"[CONFIDENCE] Extra penalty for very top area: '{detected_text}'")
        
        # Favor main content area (middle 60% of screen)
        if 0.25 < y/height < 0.85:
            confidence += 25
            print(f"[CONFIDENCE] Bonus for main content area: '{detected_text}'")
        
        # Bonus for common UI terms
        if any(ui_term in detected_text.lower() for ui_term in ['button', 'menu', 'save', 'open', 'close', 'new', 'edit', 'delete', 'cancel', 'ok']):
            confidence += 10
            print(f"[CONFIDENCE] UI word bonus for: '{detected_text}'")
        
        return confidence