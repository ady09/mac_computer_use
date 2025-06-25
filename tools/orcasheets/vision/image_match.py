import cv2
import numpy as np
from typing import Tuple

def find_template_in_screenshot(screenshot_path: str, template_path: str, threshold: float = 0.5) -> Tuple[int, int] | None:
    """
    Find the (x, y) center coordinates of the template in the screenshot.
    Returns None if not found above the threshold.
    Prints the max match value for debugging.
    """
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)
    if screenshot is None or template is None:
        raise ValueError("Could not load screenshot or template image.")
    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print(f"[DEBUG] Template match value for {template_path}: {max_val}")
    if max_val < threshold:
        return None
    t_height, t_width = template.shape[:2]
    center_x = max_loc[0] + t_width // 2
    center_y = max_loc[1] + t_height // 2
    return (center_x, center_y) 