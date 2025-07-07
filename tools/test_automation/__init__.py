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
    'CustomHandler'
]