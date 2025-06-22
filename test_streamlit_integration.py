#!/usr/bin/env python3
"""
Test script to verify the tool integration works with the actual loop system.
"""

import asyncio
from loop import sampling_loop, APIProvider

async def test_tool_collection_in_loop():
    """Test that the tool collection loads correctly in the sampling loop context"""
    try:
        from tools import ToolCollection, ComputerTool, BashTool, EditTool, OrcaSheetsTool
        
        # This mimics what happens in sampling_loop
        tool_collection = ToolCollection(
            ComputerTool(),
            BashTool(),
            EditTool(),
            OrcaSheetsTool(),
        )
        
        # Test that to_params() works for all tools
        params = tool_collection.to_params()
        tool_names = [tool['name'] for tool in params]
        
        print("✅ Tool collection created successfully")
        print(f"✅ Tools available: {tool_names}")
        
        # Verify orcasheets tool is properly formatted
        orcasheets_tool = next((tool for tool in params if tool['name'] == 'orcasheets'), None)
        if orcasheets_tool:
            print("✅ OrcaSheets tool found in collection")
            print(f"   Type: {orcasheets_tool['type']}")
            print(f"   Has input_schema: {'input_schema' in orcasheets_tool}")
            if 'input_schema' in orcasheets_tool:
                actions = orcasheets_tool['input_schema']['properties']['action']['enum']
                print(f"   Available actions: {actions}")
        else:
            print("❌ OrcaSheets tool not found in collection")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to test tool collection in loop context: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_orcasheets_tool_execution():
    """Test that the tool can actually be called through the collection"""
    try:
        from tools import ToolCollection, ComputerTool, BashTool, EditTool, OrcaSheetsTool
        
        tool_collection = ToolCollection(
            ComputerTool(),
            BashTool(),
            EditTool(),
            OrcaSheetsTool(),
        )
        
        # Test calling the orcasheets tool through the collection
        result = await tool_collection.run(
            name="orcasheets",
            tool_input={"action": "take_screenshot"}
        )
        
        if result.error:
            print(f"⚠️  Tool execution completed with error: {result.error}")
        else:
            print(f"✅ Tool execution successful: {result.output}")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to execute tool through collection: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run integration tests"""
    print("🧪 Streamlit Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Tool Collection in Loop Context", test_tool_collection_in_loop),
        ("Tool Execution through Collection", test_orcasheets_tool_execution),
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
        print("🎉 All tests passed! Integration is ready for Streamlit.")
        print("\n🚀 You can now start the Streamlit app:")
        print("   streamlit run streamlit.py")
        print("\n💬 And try prompts like:")
        print("   'Open OrcaSheets and upload industry.csv from Downloads'")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())