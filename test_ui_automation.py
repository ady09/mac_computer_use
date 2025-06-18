#!/usr/bin/env python3
"""
Test UI automation capabilities and permissions.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ui_automation():
    """Test UI automation setup and permissions."""
    print("🧪 Testing UI Automation Setup")
    print("=" * 50)
    
    try:
        from orcasheets.config import OrcaSheetsConfig
        from orcasheets.tools.ui_automation import UIAutomation
        
        # Create UI automation instance
        config = OrcaSheetsConfig()
        ui = UIAutomation(config)
        
        print("✅ UI automation instance created")
        
        # Get diagnostics
        print("\n🔍 System Diagnostics:")
        diagnostics = ui.get_diagnostics()
        print(diagnostics)
        
        # Test permissions
        print("\n🔐 Permission Tests:")
        permissions = ui.test_permissions()
        
        for perm_type, status in permissions.items():
            if perm_type != 'recommendations':
                print(f"  {perm_type.title()}: {'✅' if status else '❌'}")
        
        if permissions['recommendations']:
            print("\n💡 Recommendations:")
            for rec in permissions['recommendations']:
                print(f"  • {rec}")
        
        # Test screenshot
        print("\n📸 Testing Screenshot:")
        try:
            screenshot = ui.take_screenshot()
            if len(screenshot) > 100:
                print("✅ Screenshot capability works")
            else:
                print("❌ Screenshot returned empty data")
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
        
        # Test basic AppleScript
        print("\n🍎 Testing AppleScript:")
        try:
            import subprocess
            result = subprocess.run([
                "osascript", "-e", 
                'tell application "System Events" to return "Hello from AppleScript"'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ AppleScript execution works")
                print(f"   Response: {result.stdout.strip()}")
            else:
                print(f"❌ AppleScript failed: {result.stderr}")
        except Exception as e:
            print(f"❌ AppleScript test error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI automation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_spotlight_methods():
    """Test different methods of opening Spotlight."""
    print("\n🔍 Testing Spotlight Methods")
    print("=" * 30)
    
    try:
        from orcasheets.config import OrcaSheetsConfig
        from orcasheets.tools.ui_automation import UIAutomation
        
        config = OrcaSheetsConfig()
        ui = UIAutomation(config)
        
        # Test AppleScript method
        print("Method 1: AppleScript keystroke")
        import subprocess
        try:
            result = subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to keystroke space using command down'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ AppleScript keystroke command succeeded")
                print("   Note: This actually triggered Spotlight! Press Esc to close it.")
            else:
                print(f"❌ AppleScript keystroke failed: {result.stderr}")
        except Exception as e:
            print(f"❌ AppleScript test error: {e}")
        
        # Test cliclick method
        print("\nMethod 2: cliclick")
        try:
            result = subprocess.run([
                "cliclick", "kd:cmd space"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ cliclick command succeeded")
                print("   Note: This may have triggered Spotlight! Press Esc to close it.")
            else:
                print(f"❌ cliclick failed: {result.stderr}")
        except FileNotFoundError:
            print("❌ cliclick not found. Install with: brew install cliclick")
        except Exception as e:
            print(f"❌ cliclick test error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Spotlight test failed: {e}")
        return False

def main():
    """Run all UI automation tests."""
    print("🚀 OrcaSheets UI Automation Test Suite")
    print("=" * 60)
    
    success = True
    
    success &= test_ui_automation()
    success &= test_spotlight_methods()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 UI automation tests completed!")
        print("\nIf you see permission errors:")
        print("1. Go to System Preferences > Security & Privacy > Privacy")
        print("2. Add Terminal to 'Accessibility' list")
        print("3. Add Terminal to 'Screen Recording' list (if using screenshots)")
        print("4. Restart Terminal and try again")
    else:
        print("❌ Some UI automation tests failed.")
        print("Check the errors above and follow the recommendations.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)