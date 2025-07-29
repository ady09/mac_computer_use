"""
Test automation framework for UI testing
"""

from .ocr import OCREngine
from .ui_detection import ElementFinder
from .actions import (
    BaseActionHandler,
    ClickHandler,
    ScreenshotHandler,
    TypeHandler,
    KeyHandler,
    WaitHandler,
    ApplicationHandler,
    FileHandler,
    VerificationHandler,
    CustomHandler
)
from .actions.icon_handler import IconHandler
from .vision import IconDetector

__all__ = [
    'OCREngine',
    'ElementFinder',
    'BaseActionHandler',
    'ClickHandler',
    'ScreenshotHandler',
    'TypeHandler',
    'KeyHandler',
    'WaitHandler',
    'ApplicationHandler',
    'FileHandler',
    'VerificationHandler',
    'CustomHandler',
    'IconHandler',
    'IconDetector'
]