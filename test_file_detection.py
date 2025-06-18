#!/usr/bin/env python3
"""
Test file detection and path expansion.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_file_detection():
    """Test file detection logic."""
    print("🧪 Testing File Detection")
    print("=" * 40)
    
    try:
        from orcasheets.config import OrcaSheetsConfig
        from orcasheets.tools.ui_automation import UIAutomation
        
        config = OrcaSheetsConfig()
        ui = UIAutomation(config)
        
        # Test different path formats
        test_paths = [
            "~/Downloads/industry.csv",
            "/Users/aditya/Downloads/industry.csv",
            "Downloads/industry.csv",
            "industry.csv"
        ]
        
        for path in test_paths:
            print(f"\nTesting path: {path}")
            
            # Test expansion
            expanded = ui.expand_path(path)
            print(f"  Expanded to: {expanded}")
            
            # Test existence
            exists = ui.file_exists(path)
            print(f"  File exists: {'✅' if exists else '❌'}")
            
            # Test with os.path directly
            if expanded != path:
                direct_exists = os.path.isfile(expanded)
                print(f"  Direct check: {'✅' if direct_exists else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ File detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_parameters():
    """Test how task parameters are constructed."""
    print("\n🔍 Testing Task Parameter Construction")
    print("=" * 50)
    
    try:
        from orcasheets.tasks import TaskValidator
        
        # Test the exact command
        user_input = "open orcasheets and upload industry.csv from downloads"
        print(f"Command: {user_input}")
        
        task = TaskValidator.parse_user_request(user_input)
        if task:
            print(f"✅ Parsed successfully")
            print(f"  Task type: {task.task_type.value}")
            print(f"  File path: {task.parameters.get('file_path')}")
            print(f"  Project name: {task.parameters.get('project_name')}")
            
            # Test validation
            is_valid = task.validate()
            print(f"  Validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
            
        else:
            print("❌ Failed to parse")
        
        return True
        
    except Exception as e:
        print(f"❌ Task parameter test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 File Detection Test Suite")
    print("=" * 60)
    
    success = True
    
    success &= test_file_detection()
    success &= test_task_parameters()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 File detection tests completed!")
    else:
        print("❌ Some tests failed.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)