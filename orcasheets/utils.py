"""
Utility functions for OrcaSheets framework.
"""

import os


def get_api_key() -> str:
    """Get Anthropic API key from environment or .env file."""
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
                    if line.startswith('ANTHROPIC_API_KEY='):
                        key_value = line.split('=', 1)[1].strip()
                        # Remove quotes if present
                        if key_value.startswith('"') and key_value.endswith('"'):
                            key_value = key_value[1:-1]
                        elif key_value.startswith("'") and key_value.endswith("'"):
                            key_value = key_value[1:-1]
                        os.environ['ANTHROPIC_API_KEY'] = key_value
                        break
    
    api_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    if not api_key or api_key == 'your_api_key_here':
        raise ValueError(
            "Anthropic API key not found. Please set ANTHROPIC_API_KEY in your .env file.\n"
            "Get your API key from: https://console.anthropic.com/"
        )
    
    return api_key


def validate_api_key(api_key: str) -> bool:
    """Validate that API key looks correct."""
    if not api_key:
        return False
    
    # Basic validation - Anthropic keys typically start with 'sk-ant-'
    if not api_key.startswith('sk-ant-'):
        return False
    
    # Should be reasonable length
    if len(api_key) < 20:
        return False
    
    return True