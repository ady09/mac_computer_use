#!/usr/bin/env python3
"""
Create a mock OrcaSheets app for testing automation.
"""

import os
import subprocess
import sys

def create_mock_orcasheets():
    """Create a mock OrcaSheets app for testing."""
    print("🔧 Creating Mock OrcaSheets App for Testing")
    print("=" * 50)
    
    # Create a simple AppleScript app that acts like OrcaSheets
    app_name = "MockOrcaSheets"
    app_path = f"/Applications/{app_name}.app"
    
    # Check if app already exists
    if os.path.exists(app_path):
        print(f"✅ {app_name} already exists at {app_path}")
        return True
    
    # Create the app bundle structure
    contents_path = f"{app_path}/Contents"
    macos_path = f"{contents_path}/MacOS"
    resources_path = f"{contents_path}/Resources"
    
    try:
        # Create directories
        os.makedirs(macos_path, exist_ok=True)
        os.makedirs(resources_path, exist_ok=True)
        
        # Create Info.plist
        info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.test.{app_name.lower()}</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.9</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
</dict>
</plist>"""
        
        with open(f"{contents_path}/Info.plist", "w") as f:
            f.write(info_plist)
        
        # Create executable script
        executable_script = f"""#!/bin/bash
osascript -e 'tell application "System Events"
    display dialog "Mock OrcaSheets is running!\\n\\nThis is a test app for automation.\\n\\nFeatures:\\n• Project selection\\n• File upload simulation\\n• Window management" with title "Mock OrcaSheets" buttons {{"Close", "Minimize", "Projects"}} default button "Projects"
    
    set buttonPressed to button returned of result
    
    if buttonPressed is "Projects" then
        display dialog "Available Projects:\\n\\n• Default Project\\n• Test Project\\n• Demo Project\\n\\nSelect a project to continue." with title "Project Selection" buttons {{"Cancel", "Default Project"}} default button "Default Project"
        
        set projectSelected to button returned of result
        
        if projectSelected is "Default Project" then
            display dialog "Project: Default Project\\n\\nActions available:\\n• Add new sheet\\n• Upload file\\n• View data" with title "Default Project" buttons {{"Cancel", "Add Sheet", "Upload File"}} default button "Upload File"
            
            set actionSelected to button returned of result
            
            if actionSelected is "Upload File" then
                display dialog "File upload simulation\\n\\nThis would normally open a file picker.\\n\\nSupported formats:\\n• CSV\\n• XLSX\\n• JSON\\n• TXT" with title "Upload File" buttons {{"OK"}} default button "OK"
            else if actionSelected is "Add Sheet" then
                display dialog "New sheet created!\\n\\nSheet name: New Sheet " & (random number from 1 to 100) with title "Sheet Created" buttons {{"OK"}} default button "OK"
            end if
        end if
    end if
end tell'
"""
        
        with open(f"{macos_path}/{app_name}", "w") as f:
            f.write(executable_script)
        
        # Make executable
        os.chmod(f"{macos_path}/{app_name}", 0o755)
        
        print(f"✅ Created {app_name} at {app_path}")
        print(f"✅ App is now searchable in Spotlight as 'orcasheets' or '{app_name}'")
        
        # Test that it can be found
        print("\n🧪 Testing Spotlight search...")
        result = subprocess.run([
            "mdfind", 
            f"kMDItemDisplayName == '{app_name}'"
        ], capture_output=True, text=True)
        
        if app_path in result.stdout:
            print("✅ App is indexed by Spotlight")
        else:
            print("⚠️ App may not be indexed yet (this is normal)")
            print("   Wait a few minutes for Spotlight to index the new app")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create mock app: {e}")
        return False

def test_mock_app():
    """Test the mock app."""
    print("\n🧪 Testing Mock App")
    print("=" * 30)
    
    try:
        # Try to open the app
        subprocess.run([
            "open", "/Applications/MockOrcaSheets.app"
        ], check=True)
        
        print("✅ Mock app launched successfully!")
        print("   You should see a dialog box with mock OrcaSheets interface")
        
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Failed to launch mock app")
        return False
    except FileNotFoundError:
        print("❌ Mock app not found. Create it first.")
        return False

def create_alias():
    """Create aliases for easier Spotlight finding."""
    print("\n🔗 Creating Spotlight Aliases")
    print("=" * 30)
    
    aliases = ["OrcaSheets", "Orca Sheets", "Orca", "Sheets"]
    
    for alias in aliases:
        alias_path = f"/Applications/{alias}.app"
        original_path = "/Applications/MockOrcaSheets.app"
        
        if not os.path.exists(alias_path) and os.path.exists(original_path):
            try:
                # Create symbolic link
                os.symlink(original_path, alias_path)
                print(f"✅ Created alias: {alias}")
            except Exception as e:
                print(f"⚠️ Could not create alias {alias}: {e}")

def main():
    """Main function."""
    print("🚀 Mock OrcaSheets Setup")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        return test_mock_app()
    
    success = True
    success &= create_mock_orcasheets()
    create_alias()  # Best effort, don't fail if this doesn't work
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Mock OrcaSheets created successfully!")
        print("\n📋 What you can do now:")
        print("1. Test the app: python3 create_mock_orcasheets.py test")
        print("2. Search in Spotlight: Cmd+Space, type 'orcasheets'")
        print("3. Run automation: 'open orcasheets and upload industry.csv from downloads'")
        print("\n💡 This mock app simulates OrcaSheets functionality for testing automation.")
    else:
        print("❌ Failed to create mock app.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)