"""
Action handlers module for test automation
"""

from .base_handler import BaseActionHandler
from .click_handler import ClickHandler
from .basic_handlers import (
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