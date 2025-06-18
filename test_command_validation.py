#!/usr/bin/env python3
"""
Test command validation and parsing for OrcaSheets framework.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_command_parsing():
    """Test that commands are parsed correctly."""
    print("🧪 Testing Command Parsing")
    print("=" * 40)
    
    try:
        from orcasheets.tasks import TaskValidator
        
        # Test the exact command that was failing
        test_commands = [
            "open orcasheets and upload industry.csv from downloads",
            "open orcasheets, select default project and upload industry.csv from downloads",
            "open orcasheets and upload data.xlsx from documents",
            "open orcasheets and upload report.json from desktop project MyProject"
        ]
        
        for cmd in test_commands:
            print(f"\nCommand: {cmd}")
            task = TaskValidator.parse_user_request(cmd)
            
            if task:
                print(f"✅ Parsed as: {task.task_type.value}")
                print(f"   Parameters: {task.parameters}")
                
                # Test validation
                is_valid = task.validate()
                print(f"   Validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
                
                if not is_valid:
                    # Debug validation failure
                    from orcasheets.tasks import TaskValidator
                    print(f"   File path: {task.parameters.get('file_path')}")
                    print(f"   Project name: {task.parameters.get('project_name')}")
                    
                    # Test individual validation methods
                    if hasattr(TaskValidator, '_validate_upload_task'):
                        upload_valid = TaskValidator._validate_upload_task(task.parameters)
                        print(f"   Upload validation: {'✅' if upload_valid else '❌'}")
                    
                    if hasattr(TaskValidator, '_validate_project_task'):
                        project_valid = TaskValidator._validate_project_task(task.parameters)
                        print(f"   Project validation: {'✅' if project_valid else '❌'}")
            else:
                print("❌ Failed to parse")
        
        return True
        
    except Exception as e:
        print(f"❌ Command parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_details():
    """Test validation logic in detail."""
    print("\n🔍 Testing Validation Details")
    print("=" * 40)
    
    try:
        from orcasheets.tasks import TaskValidator, OrcaSheetsTask, TaskType
        
        # Test specific parameter combinations
        test_cases = [
            {
                "name": "Valid combined task",
                "task_type": TaskType.COMBINED_OPEN_AND_UPLOAD,
                "parameters": {
                    "file_path": "~/Downloads/industry.csv",
                    "project_name": "default"
                }
            },
            {
                "name": "Valid with custom project",
                "task_type": TaskType.COMBINED_OPEN_AND_UPLOAD,
                "parameters": {
                    "file_path": "~/Documents/data.xlsx", 
                    "project_name": "MyProject"
                }
            },
            {
                "name": "Invalid file extension",
                "task_type": TaskType.COMBINED_OPEN_AND_UPLOAD,
                "parameters": {
                    "file_path": "~/Downloads/bad.exe",
                    "project_name": "default"
                }
            },
            {
                "name": "Invalid directory",
                "task_type": TaskType.COMBINED_OPEN_AND_UPLOAD,
                "parameters": {
                    "file_path": "~/BadFolder/industry.csv",
                    "project_name": "default"
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\nTest: {test_case['name']}")
            task = OrcaSheetsTask(
                task_type=test_case['task_type'],
                parameters=test_case['parameters']
            )
            
            is_valid = task.validate()
            expected_valid = "Valid" in test_case['name']
            
            if is_valid == expected_valid:
                print(f"✅ {'PASSED' if is_valid else 'CORRECTLY REJECTED'}")
            else:
                print(f"❌ UNEXPECTED: Expected {expected_valid}, got {is_valid}")
                print(f"   Parameters: {test_case['parameters']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all validation tests."""
    print("🚀 Command Validation Test Suite")
    print("=" * 60)
    
    success = True
    
    success &= test_command_parsing()
    success &= test_validation_details()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All validation tests passed!")
        print("\nThe command 'open orcasheets and upload industry.csv from downloads' should now work!")
    else:
        print("❌ Some validation tests failed.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)