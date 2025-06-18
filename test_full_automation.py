#!/usr/bin/env python3
"""
Test the full automation flow step by step.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_automation_step_by_step():
    """Test automation step by step."""
    print("🧪 Testing Full Automation Flow")
    print("=" * 50)
    
    try:
        from orcasheets.tools.async_wrapper import AsyncOrcaSheetsTool
        
        tool = AsyncOrcaSheetsTool()
        
        # Test 1: Simple open command
        print("\n1️⃣ Testing simple open command...")
        result1 = await tool(
            task_type="open_orcasheets",
            parameters={}
        )
        
        print(f"   Result: {'✅ SUCCESS' if not result1.error else '❌ ERROR'}")
        if result1.error:
            print(f"   Error: {result1.error}")
        if result1.output:
            print(f"   Output: {result1.output}")
        
        # Test 2: File validation
        print("\n2️⃣ Testing file validation...")
        test_file_path = "~/Downloads/industry.csv"
        
        from orcasheets.config import OrcaSheetsConfig
        from orcasheets.tools.ui_automation import UIAutomation
        
        ui = UIAutomation(OrcaSheetsConfig())
        file_exists = ui.file_exists(test_file_path)
        expanded_path = ui.expand_path(test_file_path)
        
        print(f"   File path: {test_file_path}")
        print(f"   Expanded: {expanded_path}")
        print(f"   Exists: {'✅' if file_exists else '❌'}")
        
        # Test 3: Combined command
        print("\n3️⃣ Testing combined open and upload...")
        result3 = await tool(
            task_type="combined_open_and_upload",
            parameters={
                "file_path": "~/Downloads/industry.csv",
                "project_name": "default"
            }
        )
        
        print(f"   Result: {'✅ SUCCESS' if not result3.error else '❌ ERROR'}")
        if result3.error:
            print(f"   Error: {result3.error}")
        if result3.output:
            print(f"   Output: {result3.output}")
        
        return True
        
    except Exception as e:
        print(f"❌ Automation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_mock_app():
    """Test with mock OrcaSheets app."""
    print("\n🎭 Testing with Mock App")
    print("=" * 30)
    
    # Check if mock app exists
    mock_app_path = "/Applications/MockOrcaSheets.app"
    if not os.path.exists(mock_app_path):
        print("ℹ️ Mock app not found. Creating it...")
        import subprocess
        result = subprocess.run([
            "python3", "create_mock_orcasheets.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Mock app created successfully")
        else:
            print(f"❌ Failed to create mock app: {result.stderr}")
            return False
    
    # Test automation with mock app
    try:
        from orcasheets.tools.async_wrapper import AsyncOrcaSheetsTool
        
        tool = AsyncOrcaSheetsTool()
        
        print("\n🚀 Testing automation with mock app...")
        result = await tool(
            task_type="combined_open_and_upload",
            parameters={
                "file_path": "~/Downloads/industry.csv",
                "project_name": "default"
            }
        )
        
        print(f"   Result: {'✅ SUCCESS' if not result3.error else '❌ ERROR'}")
        if result.error:
            print(f"   Error: {result.error}")
        if result.output:
            print(f"   Output: {result.output}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock app test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Full Automation Test Suite")
    print("=" * 60)
    
    success = True
    
    success &= await test_automation_step_by_step()
    
    # Ask user if they want to test with mock app
    try:
        response = input("\n❓ Test with mock OrcaSheets app? (y/n): ").lower().strip()
        if response == 'y':
            success &= await test_with_mock_app()
    except (EOFError, KeyboardInterrupt):
        print("\n⏭️ Skipping mock app test")
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Full automation tests completed!")
        print("\n💡 If OrcaSheets isn't opening:")
        print("1. Install OrcaSheets or create mock app")
        print("2. Check accessibility permissions")
        print("3. Try opening OrcaSheets manually first")
    else:
        print("❌ Some automation tests failed.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)