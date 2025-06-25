#!/usr/bin/env python3
"""
Debug OCR to see what text is found in the screenshot
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.computer import ComputerTool
from tools.orcasheets.vision.ocr import extract_text_from_image, find_text_location
import base64
import tempfile

async def debug_ocr():
    """Debug what OCR finds in the current screenshot"""
    computer = ComputerTool()
    
    print("Taking screenshot...")
    screenshot = await computer(action="screenshot")
    
    img_bytes = base64.b64decode(screenshot.base64_image)
    with tempfile.NamedTemporaryFile(suffix="_debug.png", delete=False) as f:
        f.write(img_bytes)
        screenshot_path = f.name
    
    print(f"Screenshot saved to: {screenshot_path}")
    
    # Extract all text
    print("\n=== ALL TEXT FOUND ===")
    all_text = extract_text_from_image(screenshot_path)
    print(all_text)
    
    print("\n=== SEARCHING FOR SPECIFIC TEXT ===")
    
    # Try to find different variations
    targets = ["NEW PROJECT", "NEW", "PROJECT", "Open files", "files", "Open"]
    
    for target in targets:
        coords = find_text_location(screenshot_path, target)
        if coords:
            print(f"Found '{target}' at: {coords}")
        else:
            print(f"NOT found: '{target}'")

if __name__ == "__main__":
    asyncio.run(debug_ocr())