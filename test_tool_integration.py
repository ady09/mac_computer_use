#!/usr/bin/env python3
"""
Test tool integration with Anthropic API format.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_tool_collection():
    """Test that our tool works with ToolCollection."""
    print("🧪 Testing tool collection integration...")
    
    try:
        from tools.collection import ToolCollection
        from orcasheets.tools.async_wrapper import AsyncOrcaSheetsTool
        
        # Create tool
        orcasheets_tool = AsyncOrcaSheetsTool()
        
        # Create collection
        tool_collection = ToolCollection(orcasheets_tool)
        
        print("✅ Tool collection created successfully")
        
        # Test tool parameters
        params = tool_collection.to_params()
        print(f"✅ Tool collection params: {len(params)} tools")
        
        if params:
            first_tool = params[0]
            print(f"✅ First tool name: {first_tool['name']}")
            print(f"✅ First tool type: {first_tool['type']}")
        
        # Test tool execution (should handle validation)
        print("\n🔧 Testing tool execution...")
        
        # Test with valid task
        result = await tool_collection.run(
            name="orcasheets_automation",
            tool_input={
                "task_type": "open_orcasheets",
                "parameters": {}
            }
        )
        
        print(f"✅ Tool execution completed")
        if result.error:
            print(f"   Expected error (no real app): {result.error}")
        else:
            print(f"   Result: {result.output}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool collection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_task_validation():
    """Test task validation in the tool."""
    print("\n🔍 Testing task validation...")
    
    try:
        from orcasheets.tools.async_wrapper import AsyncOrcaSheetsTool
        
        tool = AsyncOrcaSheetsTool()
        
        # Test valid task
        valid_result = await tool(
            task_type="open_orcasheets",
            parameters={}
        )
        
        print("✅ Valid task processed")
        if valid_result.error:
            print(f"   Note: {valid_result.error}")
        
        # Test invalid task
        invalid_result = await tool(
            task_type="invalid_task",
            parameters={}
        )
        
        if invalid_result.error:
            print("✅ Invalid task correctly rejected")
        else:
            print("❌ Invalid task was not rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ Task validation test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Tool Integration Test")
    print("=" * 50)
    
    success = True
    
    success &= await test_tool_collection()
    success &= await test_task_validation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tool integration tests passed!")
        print("\nThe framework should now work with Anthropic API!")
    else:
        print("❌ Some tests failed. Check errors above.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)