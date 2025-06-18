#!/usr/bin/env python3
"""
Test mouse and keyboard control directly.
"""

import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mouse_movement():
    """Test if mouse can be controlled."""
    print("🖱️ Testing Mouse Control")
    print("=" * 30)
    
    try:
        from orcasheets.config import OrcaSheetsConfig
        from orcasheets.tools.ui_automation import UIAutomation
        
        config = OrcaSheetsConfig()
        ui = UIAutomation(config)
        
        print("📍 Current mouse position test...")
        
        # Test clicking at different positions
        test_positions = [
            (100, 100),  # Top left
            (400, 300),  # Center
            (600, 200),  # Right side
        ]
        
        print("⚠️ **WATCH YOUR SCREEN** - Mouse will click in 3 seconds!")
        time.sleep(3)
        
        for i, (x, y) in enumerate(test_positions, 1):
            print(f"   {i}. Clicking at ({x}, {y})...")
            
            success = ui.click_at_coordinates(x, y)
            print(f"      Result: {'✅ Success' if success else '❌ Failed'}")
            
            time.sleep(1)  # Pause between clicks
        
        return True
        
    except Exception as e:
        print(f"❌ Mouse test failed: {e}")
        return False

def test_keyboard_control():
    """Test keyboard control."""
    print("\n⌨️ Testing Keyboard Control")
    print("=" * 30)
    
    try:
        from orcasheets.config import OrcaSheetsConfig
        from orcasheets.tools.ui_automation import UIAutomation
        
        config = OrcaSheetsConfig()
        ui = UIAutomation(config)
        
        print("📝 Testing key combinations...")
        
        # Test key combinations
        test_keys = [
            ("cmd+space", "Open Spotlight"),
            ("escape", "Close Spotlight"),
            ("cmd+a", "Select All"),
        ]
        
        print("⚠️ **WATCH YOUR SCREEN** - Keys will be pressed in 3 seconds!")
        time.sleep(3)
        
        for keys, description in test_keys:
            print(f"   Testing: {keys} ({description})")
            
            success = ui.press_key_combination(keys)
            print(f"      Result: {'✅ Success' if success else '❌ Failed'}")
            
            time.sleep(2)  # Pause between key presses
        
        return True
        
    except Exception as e:
        print(f"❌ Keyboard test failed: {e}")
        return False

def test_typing():
    """Test typing text."""
    print("\n📝 Testing Text Typing")
    print("=" * 30)
    
    try:
        from orcasheets.config import OrcaSheetsConfig
        from orcasheets.tools.ui_automation import UIAutomation
        
        config = OrcaSheetsConfig()
        ui = UIAutomation(config)
        
        print("📝 Testing text input...")
        print("⚠️ **WATCH YOUR SCREEN** - Text will be typed in 3 seconds!")
        print("   (Make sure a text field is active, like opening TextEdit)")
        
        time.sleep(3)
        
        test_text = "Hello from OrcaSheets automation!"
        print(f"   Typing: '{test_text}'")
        
        success = ui.type_text(test_text)
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Typing test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Mouse & Keyboard Control Test")
    print("=" * 50)
    
    print("💡 **Important**: These tests will actually control your mouse and keyboard!")
    print("💡 Make sure you're ready and watching your screen.")
    
    try:
        response = input("\n❓ Continue with control tests? (y/n): ").lower().strip()
        if response != 'y':
            print("⏭️ Skipping control tests")
            return True
    except (EOFError, KeyboardInterrupt):
        print("\n⏭️ Skipping control tests")
        return True
    
    success = True
    
    success &= test_mouse_movement()
    success &= test_keyboard_control()
    success &= test_typing()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Mouse & Keyboard control tests completed!")
        print("\n✅ If you saw the mouse moving and keys being pressed,")
        print("   your automation should work with OrcaSheets!")
        print("\n🚀 Next: Try your OrcaSheets command:")
        print("   streamlit run orcasheets_streamlit.py")
        print("   Command: 'open orcasheets and upload industry.csv from downloads'")
    else:
        print("❌ Some control tests failed.")
        print("💡 Check accessibility permissions and try again.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)