#!/usr/bin/env python3
"""
Simple test script for OrcaSheets framework.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orcasheets_main import OrcaSheetsAutomation

def test_framework():
    """Test the OrcaSheets framework."""
    print("🧪 Testing OrcaSheets Framework...")
    
    automation = OrcaSheetsAutomation()
    
    # Test valid commands
    test_commands = [
        "open orcasheets",
        "open orcasheets and upload test.csv from downloads",
        "upload data.xlsx from documents project TestProject"
    ]
    
    # Test invalid commands (should be blocked)
    blocked_commands = [
        "open chrome",
        "browse the internet", 
        "send an email"
    ]
    
    print("\n✅ Testing valid commands:")
    for command in test_commands:
        print(f"  Command: {command}")
        result = automation.process_request(command)
        if result['success'] or 'file not found' in result.get('error', '').lower():
            print(f"  ✅ Accepted (validation passed)")
        else:
            print(f"  ❌ Rejected: {result.get('error')}")
    
    print("\n🚫 Testing blocked commands:")
    for command in blocked_commands:
        print(f"  Command: {command}")
        result = automation.process_request(command)
        if not result['success']:
            print(f"  ✅ Correctly blocked: {result.get('error')}")
        else:
            print(f"  ❌ Incorrectly allowed!")
    
    print("\n🎉 Framework test completed!")

if __name__ == "__main__":
    test_framework()
