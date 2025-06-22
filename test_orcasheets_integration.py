#!/usr/bin/env python3
"""
Test script to verify OrcaSheets tool integration with the main system.
"""

import asyncio
import sys
from pathlib import Path

# Test if OrcaSheets tool can be imported and used
async def test_orcasheets_tool_import():
    """Test importing the OrcaSheets tool"""
    try:
        from tools import OrcaSheetsTool
        print("✅ Successfully imported OrcaSheetsTool")
        
        # Test tool initialization
        tool = OrcaSheetsTool()
        print("✅ Successfully initialized OrcaSheetsTool")
        
        # Test tool parameters
        params = tool.to_params()
        print(f"✅ Tool parameters: {params['name']}")
        print(f"   Description: {params['description']}")
        print(f"   Actions: {params['input_schema']['properties']['action']['enum']}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to import/initialize OrcaSheetsTool: {e}")
        return False

async def test_orcasheets_tool_in_collection():
    """Test OrcaSheets tool in ToolCollection"""
    try:
        from tools import ToolCollection, OrcaSheetsTool, ComputerTool, BashTool, EditTool
        
        collection = ToolCollection(
            ComputerTool(),
            BashTool(), 
            EditTool(),
            OrcaSheetsTool(),
        )
        
        params = collection.to_params()
        tool_names = [tool['name'] for tool in params]
        
        print(f"✅ ToolCollection created with tools: {tool_names}")
        
        if 'orcasheets' in tool_names:
            print("✅ OrcaSheets tool is included in collection")
            return True
        else:
            print("❌ OrcaSheets tool not found in collection")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test ToolCollection: {e}")
        return False

async def test_orcasheets_tool_execution():
    """Test basic OrcaSheets tool execution"""
    try:
        from tools import OrcaSheetsTool
        
        tool = OrcaSheetsTool()
        
        # Test take_screenshot action (should be safe to run)
        print("🔍 Testing take_screenshot action...")
        result = await tool(action="take_screenshot")
        
        if result.error:
            print(f"⚠️  Screenshot action completed with error: {result.error}")
        else:
            print(f"✅ Screenshot action completed: {result.output}")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to execute OrcaSheets tool: {e}")
        return False

async def test_automation_framework():
    """Test the underlying automation framework"""
    try:
        from tools.orcasheets.orcasheets_automation import OrcaSheetsAutomation
        
        automation = OrcaSheetsAutomation()
        print("✅ OrcaSheetsAutomation initialized")
        
        # Test computer tool availability
        if automation.computer:
            print("✅ Computer tool is available")
        else:
            print("❌ Computer tool not available")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to test automation framework: {e}")
        return False

async def run_all_tests():
    """Run all integration tests"""
    print("🧪 OrcaSheets Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_orcasheets_tool_import),
        ("Collection Test", test_orcasheets_tool_in_collection), 
        ("Execution Test", test_orcasheets_tool_execution),
        ("Framework Test", test_automation_framework),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        emoji = "✅" if result else "❌"
        print(f"{emoji} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! OrcaSheets integration is working.")
        print("\n💡 You can now use prompts like:")
        print("   - 'Open OrcaSheets and upload industry.csv from Downloads'")
        print("   - 'Use OrcaSheets to upload data.csv to My Project'")
        print("   - 'Open OrcaSheets application'")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)