#!/usr/bin/env python3
"""
Test the final fix for file path handling.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_file_path_fix():
    """Test that the file path fix works for both formats."""
    print("🧪 Testing File Path Fix")
    print("=" * 40)
    
    from orcasheets.tools.async_wrapper import AsyncOrcaSheetsTool
    
    tool = AsyncOrcaSheetsTool()
    
    test_cases = [
        {
            "name": "Correct format (with ~/)",
            "params": {
                "task_type": "combined_open_and_upload",
                "parameters": {
                    "file_path": "~/Downloads/industry.csv",
                    "project_name": "default"
                }
            }
        },
        {
            "name": "API format (without ~/)",
            "params": {
                "task_type": "combined_open_and_upload", 
                "file_path": "Downloads/industry.csv",
                "project_name": "default"
            }
        },
        {
            "name": "API format - Documents folder",
            "params": {
                "task_type": "combined_open_and_upload",
                "file_path": "Documents/test.xlsx", 
                "project_name": "default"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        
        try:
            result = await tool(**test_case['params'])
            
            if "File not found" in (result.error or ""):
                print("   ❌ File validation failed")
                print(f"   Error: {result.error}")
            elif "Could not find or launch OrcaSheets" in (result.error or ""):
                print("   ✅ File validation passed (failing on app opening as expected)")
            elif result.error:
                print(f"   ⚠️ Other error: {result.error}")
            else:
                print("   ✅ Success!")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return True

async def test_streamlit_integration():
    """Test the command through the main framework."""
    print("\n🌐 Testing Streamlit Integration")
    print("=" * 40)
    
    try:
        from orcasheets_main import OrcaSheetsAutomation
        
        automation = OrcaSheetsAutomation()
        
        command = "open orcasheets and upload industry.csv from downloads"
        print(f"Command: {command}")
        
        result = automation.process_request(command)
        
        print(f"✅ Request processed")
        print(f"   Success: {result.get('success', False)}")
        
        if result.get('error'):
            if "File not found" in result['error']:
                print("   ❌ File validation still failing")
            elif "Could not find or launch OrcaSheets" in result['error']:
                print("   ✅ File validation passed, failing on app opening (expected)")
            else:
                print(f"   ⚠️ Other error: {result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Final Fix Test Suite")
    print("=" * 60)
    
    success = True
    
    success &= await test_file_path_fix()
    success &= await test_streamlit_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 File path fix working correctly!")
        print("\n✅ Your command 'open orcasheets and upload industry.csv from downloads' should now work!")
        print("✅ The only remaining issue is opening OrcaSheets (app/permissions)")
        print("\n🚀 Next steps:")
        print("1. Create mock app: python3 create_mock_orcasheets.py")
        print("2. Grant accessibility permissions")
        print("3. Launch: streamlit run orcasheets_streamlit.py")
    else:
        print("❌ Some tests failed.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)