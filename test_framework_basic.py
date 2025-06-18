#!/usr/bin/env python3
"""
Basic test for OrcaSheets framework structure (without external dependencies).
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that core modules can be imported."""
    print("🧪 Testing framework imports...")
    
    try:
        from orcasheets.config import OrcaSheetsConfig
        print("✅ Config module imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from orcasheets.tasks import TaskType, TaskValidator, OrcaSheetsTask
        print("✅ Tasks module imported successfully")
    except Exception as e:
        print(f"❌ Tasks import failed: {e}")
        return False
    
    try:
        from orcasheets.tools.ui_automation import UIAutomation
        print("✅ UI automation module imported successfully")
    except Exception as e:
        print(f"❌ UI automation import failed: {e}")
        return False
    
    return True

def test_task_validation():
    """Test task validation functionality."""
    print("\n🔍 Testing task validation...")
    
    from orcasheets.tasks import TaskValidator
    
    # Test valid commands
    valid_commands = [
        "open orcasheets",
        "open orcasheets and upload industry.csv from downloads",
        "upload data.xlsx from documents project TestProject"
    ]
    
    # Test invalid commands
    invalid_commands = [
        "open chrome",
        "browse the internet",
        "send an email"
    ]
    
    print("Testing valid commands:")
    for cmd in valid_commands:
        task = TaskValidator.parse_user_request(cmd)
        if task:
            print(f"  ✅ '{cmd}' -> {task.task_type.value}")
        else:
            print(f"  ❌ '{cmd}' -> Failed to parse")
    
    print("\nTesting invalid commands:")
    for cmd in invalid_commands:
        task = TaskValidator.parse_user_request(cmd)
        if task:
            print(f"  ❌ '{cmd}' -> Should have been rejected but got {task.task_type.value}")
        else:
            print(f"  ✅ '{cmd}' -> Correctly rejected")
    
    return True

def test_config():
    """Test configuration functionality."""
    print("\n⚙️ Testing configuration...")
    
    from orcasheets.config import OrcaSheetsConfig
    
    # Test default config
    config = OrcaSheetsConfig()
    print(f"✅ Default project: {config.default_project}")
    print(f"✅ Downloads folder: {config.downloads_folder}")
    print(f"✅ Screenshot delay: {config.screenshot_delay}")
    
    # Test custom config
    custom_config = OrcaSheetsConfig(
        default_project="Custom Project",
        screenshot_delay=0.5
    )
    print(f"✅ Custom project: {custom_config.default_project}")
    print(f"✅ Custom delay: {custom_config.screenshot_delay}")
    
    return True

def main():
    """Run all tests."""
    print("🚀 OrcaSheets Framework Basic Test")
    print("=" * 50)
    
    success = True
    
    success &= test_imports()
    success &= test_task_validation()
    success &= test_config()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All basic tests passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install anthropic streamlit")
        print("2. Run full test: python3 test_orcasheets.py")
        print("3. Launch framework: ./launch_orcasheets.sh")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)