"""
Configuration for OrcaSheets automation framework.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OrcaSheetsConfig:
    """Configuration for OrcaSheets automation."""
    
    # Default project to select if none specified
    default_project: str = "Default Project"
    
    # Common file paths
    downloads_folder: str = "~/Downloads"
    
    # UI interaction settings
    screenshot_delay: float = 1.0
    click_delay: float = 0.5
    typing_delay: float = 0.1
    
    # Spotlight search settings
    spotlight_shortcut: str = "cmd+space"
    
    # Window detection timeouts
    window_timeout: float = 10.0
    
    @classmethod
    def load_from_env(cls) -> 'OrcaSheetsConfig':
        """Load configuration from environment variables."""
        import os
        
        # Try to load .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # python-dotenv not installed, try manual loading
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            os.environ[key] = value
        
        return cls(
            default_project=os.getenv('ORCASHEETS_DEFAULT_PROJECT', 'Default Project'),
            downloads_folder=os.getenv('DOWNLOADS_FOLDER', '~/Downloads'),
            screenshot_delay=float(os.getenv('SCREENSHOT_DELAY', '1.0')),
            click_delay=float(os.getenv('CLICK_DELAY', '0.5')),
            typing_delay=float(os.getenv('TYPING_DELAY', '0.1')),
            window_timeout=float(os.getenv('WINDOW_TIMEOUT', '10.0'))
        )