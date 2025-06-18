"""
Main entry point for OrcaSheets automation framework.
"""

import sys
import os
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orcasheets import OrcaSheetsFramework, OrcaSheetsConfig


class OrcaSheetsAutomation:
    """Main automation class that integrates with the existing computer use system."""
    
    def __init__(self):
        """Initialize the OrcaSheets automation."""
        self.framework = OrcaSheetsFramework()
    
    def process_request(self, user_input: str) -> Dict[str, Any]:
        """Process a user request."""
        # First check if the request is allowed
        if not self.framework.is_request_allowed(user_input):
            return {
                "success": False,
                "error": "This framework only supports OrcaSheets-related tasks. Please specify a task related to OrcaSheets, file uploads, or sheet management.",
                "allowed_examples": self.framework._get_allowed_commands()
            }
        
        # Process the request
        return self.framework.process_user_request(user_input)
    
    def get_tool_for_anthropic(self):
        """Get the OrcaSheets tool for use with Anthropic API."""
        from orcasheets.tools import AsyncOrcaSheetsTool
        return AsyncOrcaSheetsTool(self.framework.config)


def main():
    """Main function for testing the framework."""
    automation = OrcaSheetsAutomation()
    
    # Test commands
    test_commands = [
        "open orcasheets",
        "open orcasheets and upload industry.csv from downloads",
        "open chrome",  # This should be blocked
        "upload data.xlsx from documents project TestProject"
    ]
    
    for command in test_commands:
        print(f"\nTesting command: {command}")
        result = automation.process_request(command)
        print(f"Result: {result}")


if __name__ == "__main__":
    main()