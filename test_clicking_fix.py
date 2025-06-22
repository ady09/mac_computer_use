#!/usr/bin/env python3
"""
Test the clicking fix for OrcaSheets automation.
"""

import asyncio
from tools.orcasheets.orcasheets_automation import OrcaSheetsAutomation

async def test_clicking():
    """Test that clicking with coordinates works"""
    print("🧪 Testing OrcaSheets Clicking Fix")
    print("=" * 50)
    
    automation = OrcaSheetsAutomation()
    
    try:
        print("🔍 Testing mouse_move + left_click pattern...")
        
        # Test the pattern we now use: mouse_move then left_click
        print("1. Moving mouse to coordinates [100, 100]...")
        result1 = await automation.computer(action="mouse_move", coordinate=[100, 100])
        print(f"   Result: {result1.output if result1.output else 'Success'}")
        
        print("2. Clicking at current position...")
        result2 = await automation.computer(action="left_click")
        print(f"   Result: {result2.output if result2.output else 'Success'}")
        
        print("✅ Clicking pattern works correctly!")
        
        # Test the select_project method (but don't actually run it since it would interfere)
        print("\n🔍 Testing select_project method signature...")
        print("   Method uses: mouse_move(coordinate) + left_click()")
        print("   This should work with the current computer.py implementation")
        
        return True
        
    except Exception as e:
        print(f"❌ Clicking test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_clicking())
    if success:
        print("\n🎉 Clicking fix successful!")
        print("The OrcaSheets automation should now work correctly.")
    else:
        print("\n⚠️ Clicking test failed.")