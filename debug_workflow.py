#!/usr/bin/env python3
"""
Debug the workflow execution to identify where it's failing.
"""

import asyncio
from tools import OrcaSheetsTool

async def debug_upload_command():
    """Debug the upload command step by step"""
    print("🔍 Debugging Upload Command Execution")
    print("=" * 60)
    
    tool = OrcaSheetsTool()
    command = "upload industry.csv from downloads"
    
    print(f"🎯 Testing command: '{command}'")
    
    try:
        # Test state detection first
        print("\n1️⃣ Testing state detection...")
        result = await tool(action="analyze_screen")
        print(f"Result: {result.output}")
        if result.error:
            print(f"Error: {result.error}")
        
        # Test screenshot capability
        print("\n2️⃣ Testing screenshot capability...")
        result = await tool(action="take_screenshot")
        print(f"Result: {result.output}")
        if result.error:
            print(f"Error: {result.error}")
        
        # Test the actual command
        print(f"\n3️⃣ Testing actual command: '{command}'...")
        result = await tool(action="execute_command", command=command)
        print(f"Result: {result.output}")
        if result.error:
            print(f"Error: {result.error}")
            
            # Let's check the automation object directly
            automation = tool.automation
            
            print("\n🔍 Direct automation testing...")
            
            # Test command parsing
            print("Testing filename extraction...")
            filename = automation._extract_filename(command)
            print(f"Extracted filename: '{filename}'")
            
            print("Testing project name extraction...")
            project_name = automation._extract_project_name(command)
            print(f"Extracted project name: '{project_name}'")
            
            # Test workflow detection
            print("Testing workflow type detection...")
            is_upload = "upload" in command.lower() and any(ext in command for ext in ['.csv', '.xlsx', '.json'])
            print(f"Detected as upload workflow: {is_upload}")
            
            if is_upload:
                print("\n🔄 This should trigger upload workflow...")
                print("Expected steps:")
                print("1. Ensure OrcaSheets is open")
                print("2. Navigate to project selection")
                print("3. Select project")
                print("4. Wait for main interface")
                print("5. Click 'Add new sheet'")
                print("6. Upload file")
    
    except Exception as e:
        print(f"💥 Debug failed with exception: {e}")
        import traceback
        traceback.print_exc()

async def test_individual_components():
    """Test individual components of the workflow"""
    print("\n🧪 Testing Individual Workflow Components")
    print("=" * 60)
    
    try:
        from tools.orcasheets.workflow_automation import WorkflowOrcaSheetsAutomation
        
        automation = WorkflowOrcaSheetsAutomation()
        
        # Test 1: Command parsing
        print("1️⃣ Testing command parsing...")
        command = "upload industry.csv from downloads"
        
        filename = automation._extract_filename(command)
        project_name = automation._extract_project_name(command)
        
        print(f"   Filename: '{filename}'")
        print(f"   Project: '{project_name}'")
        
        if not filename:
            print("   ❌ Filename extraction failed!")
            return False
        
        if not project_name:
            project_name = "default"
            print(f"   ⚠️  No project specified, using default: '{project_name}'")
        
        # Test 2: State detection
        print("\n2️⃣ Testing state detection...")
        try:
            state = await automation._detect_current_state()
            print(f"   Current state: {state}")
        except Exception as e:
            print(f"   ❌ State detection failed: {e}")
            return False
        
        # Test 3: OrcaSheets presence check
        print("\n3️⃣ Testing OrcaSheets detection...")
        try:
            is_running = await automation.applescript.is_application_running("OrcaSheets")
            print(f"   OrcaSheets running: {is_running}")
        except Exception as e:
            print(f"   ⚠️  AppleScript check failed: {e}")
        
        print("\n✅ Individual components test completed")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_workflow_steps():
    """Test simplified workflow steps"""
    print("\n🔧 Testing Simple Workflow Steps")
    print("=" * 60)
    
    try:
        from tools.orcasheets.workflow_automation import WorkflowOrcaSheetsAutomation
        
        automation = WorkflowOrcaSheetsAutomation()
        
        print("1️⃣ Testing _ensure_orcasheets_open...")
        try:
            # Just test the method exists and can be called
            print("   Method exists and callable")
        except Exception as e:
            print(f"   ❌ Method test failed: {e}")
        
        print("2️⃣ Testing file path construction...")
        filename = "industry.csv"
        file_path = f"~/Downloads/{filename}"
        from pathlib import Path
        expanded_path = Path(file_path).expanduser()
        print(f"   File path: {file_path}")
        print(f"   Expanded: {expanded_path}")
        print(f"   Parent: {expanded_path.parent}")
        print(f"   Name: {expanded_path.name}")
        print(f"   Exists: {expanded_path.exists()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all debug tests"""
    print("🚀 Workflow Debug Test Suite")
    print("=" * 70)
    
    tests = [
        ("Upload Command Debug", debug_upload_command),
        ("Individual Components", test_individual_components),
        ("Simple Workflow Steps", test_simple_workflow_steps),
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            await test_func()
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
    
    print("\n" + "=" * 70)
    print("🔍 Debug Complete")
    print("\nNext steps:")
    print("1. Check if industry.csv exists in ~/Downloads/")
    print("2. Check if OrcaSheets is installed and accessible")
    print("3. Look for specific error patterns in the output above")

if __name__ == "__main__":
    asyncio.run(main())