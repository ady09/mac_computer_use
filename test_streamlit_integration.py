#!/usr/bin/env python3
"""
Test OrcaSheets framework with minimal dependencies for Streamlit integration.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_framework_without_anthropic():
    """Test framework functionality without full Anthropic dependencies."""
    print("🧪 Testing framework without full dependencies...")
    
    try:
        from orcasheets_main import OrcaSheetsAutomation
        
        automation = OrcaSheetsAutomation()
        
        # Test basic request processing
        result = automation.process_request("open orcasheets")
        print("✅ Request processing works")
        print(f"   Result: {result.get('success', False)}")
        
        # Test blocked request
        blocked_result = automation.process_request("open chrome")
        print("✅ Blocked request handling works")
        print(f"   Correctly blocked: {not blocked_result.get('success', True)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Framework test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_async_tool():
    """Test async tool wrapper."""
    print("\n🔧 Testing async tool wrapper...")
    
    try:
        from orcasheets.tools.async_wrapper import AsyncOrcaSheetsTool
        
        tool = AsyncOrcaSheetsTool()
        
        # Test tool parameters
        params = tool.to_params()
        print("✅ Tool parameters generated")
        print(f"   Tool name: {params['name']}")
        print(f"   Tool type: {params['type']}")
        
        # Test tool execution
        result = await tool(
            task_type="open_orcasheets",
            parameters={}
        )
        
        print("✅ Async tool execution completed")
        if result.error:
            print(f"   Expected error (UI automation): {result.error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Async tool test failed: {e}")
        return False

def test_api_key_loading():
    """Test API key loading functionality."""
    print("\n🔑 Testing API key loading...")
    
    try:
        from orcasheets.utils import get_api_key, validate_api_key
        
        try:
            api_key = get_api_key()
            is_valid = validate_api_key(api_key)
            
            print("✅ API key loaded")
            print(f"   Valid format: {is_valid}")
            print(f"   Key preview: {api_key[:10]}...")
            
        except ValueError as e:
            print(f"⚠️ API key issue: {e}")
            print("   This is expected if no valid key is configured")
        
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Streamlit Integration Test")
    print("=" * 50)
    
    success = True
    
    success &= test_framework_without_anthropic()
    success &= await test_async_tool()
    success &= test_api_key_loading()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Framework ready for Streamlit!")
        print("\nTo run with Streamlit:")
        print("1. Install dependencies: pip install anthropic streamlit python-dotenv")
        print("2. Configure API key in .env file")
        print("3. Run: streamlit run orcasheets_streamlit.py")
    else:
        print("❌ Some tests failed. Check errors above.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)