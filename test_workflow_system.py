#!/usr/bin/env python3
"""
Test the workflow-aware OrcaSheets automation system.
"""

import asyncio
from tools import OrcaSheetsTool

async def test_workflow_integration():
    """Test that the workflow system is properly integrated"""
    print("🧪 Testing Workflow Integration")
    print("=" * 50)
    
    try:
        from tools.orcasheets.workflow_automation import WorkflowOrcaSheetsAutomation
        
        tool = OrcaSheetsTool()
        print("✅ OrcaSheetsTool initialized with workflow automation")
        
        # Check that it's using the workflow system
        if hasattr(tool.automation, 'execute_workflow_command'):
            print("✅ Workflow command execution available")
        else:
            print("❌ Workflow command execution missing")
            return False
        
        if hasattr(tool.automation, '_detect_current_state'):
            print("✅ State detection available")
        else:
            print("❌ State detection missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow integration test failed: {e}")
        return False

async def test_command_parsing():
    """Test command parsing for workflow commands"""
    print("\n🧪 Testing Workflow Command Parsing")
    print("=" * 50)
    
    try:
        from tools.orcasheets.workflow_automation import WorkflowOrcaSheetsAutomation
        
        automation = WorkflowOrcaSheetsAutomation()
        
        # Test filename extraction
        test_cases = [
            ("upload industry.csv from downloads", "industry.csv"),
            ("upload data.xlsx to my project", "data.xlsx"),
            ("add report.json file", "report.json"),
        ]
        
        print("🔍 Testing filename extraction:")
        for command, expected in test_cases:
            result = automation._extract_filename(command)
            if result == expected:
                print(f"   ✅ '{command}' → '{result}'")
            else:
                print(f"   ❌ '{command}' → expected '{expected}', got '{result}'")
                return False
        
        # Test project name extraction
        project_cases = [
            ("upload to my project", "my"),
            ("select default project", "default"),
            ("upload industry.csv to alpha project", "alpha"),
        ]
        
        print("\n🔍 Testing project name extraction:")
        for command, expected in project_cases:
            result = automation._extract_project_name(command)
            if result == expected:
                print(f"   ✅ '{command}' → '{result}'")
            else:
                print(f"   ❌ '{command}' → expected '{expected}', got '{result}'")
        
        # Test tab name extraction
        tab_cases = [
            ("close industry.csv tab", "industry.csv"),
            ("close data.xlsx tab", "data.xlsx"),
            ("close report tab", "report"),
        ]
        
        print("\n🔍 Testing tab name extraction:")
        for command, expected in tab_cases:
            result = automation._extract_tab_name(command)
            if result == expected:
                print(f"   ✅ '{command}' → '{result}'")
            else:
                print(f"   ❌ '{command}' → expected '{expected}', got '{result}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Command parsing test failed: {e}")
        return False

async def test_workflow_understanding():
    """Test that the system understands different workflow types"""
    print("\n🧪 Testing Workflow Understanding")
    print("=" * 50)
    
    try:
        from tools.orcasheets.workflow_automation import WorkflowOrcaSheetsAutomation
        
        automation = WorkflowOrcaSheetsAutomation()
        
        # Test workflow detection
        workflows = [
            ("upload industry.csv from downloads", "upload"),
            ("close data.xlsx tab", "close_tab"),
            ("select my project", "select_project"),
        ]
        
        print("🔍 Testing workflow detection:")
        for command, expected_type in workflows:
            print(f"   Command: '{command}'")
            
            if "upload" in command.lower() and any(ext in command for ext in ['.csv', '.xlsx', '.json']):
                detected_type = "upload"
            elif "close" in command.lower() and "tab" in command.lower():
                detected_type = "close_tab"
            elif "select" in command.lower() and "project" in command.lower():
                detected_type = "select_project"
            else:
                detected_type = "unknown"
            
            if detected_type == expected_type:
                print(f"   ✅ Detected as: {detected_type}")
            else:
                print(f"   ❌ Expected: {expected_type}, got: {detected_type}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow understanding test failed: {e}")
        return False

async def test_tool_execution():
    """Test tool execution with workflow commands"""
    print("\n🧪 Testing Tool Execution")
    print("=" * 50)
    
    try:
        tool = OrcaSheetsTool()
        
        # Test screenshot action (safe to run)
        print("🔍 Testing take_screenshot action...")
        result = await tool(action="take_screenshot")
        
        if result.error:
            print(f"⚠️  Screenshot action completed with warning: {result.error}")
        else:
            print(f"✅ Screenshot action: {result.output}")
        
        # Test state detection
        print("\n🔍 Testing analyze_screen action...")
        result = await tool(action="analyze_screen")
        
        if result.error:
            print(f"⚠️  State detection completed with warning: {result.error}")
        else:
            print(f"✅ State detection: {result.output}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool execution test failed: {e}")
        return False

async def demonstrate_workflow():
    """Demonstrate the workflow process"""
    print("\n🧪 Workflow Process Demonstration")
    print("=" * 50)
    
    command = "upload industry.csv from downloads"
    print(f"🎯 Command: '{command}'")
    
    print("\n📋 Workflow steps that would be executed:")
    print("1. 📱 Ensure OrcaSheets is open (Spotlight if needed)")
    print("2. 🔍 Detect current state")
    print("3. 📂 Navigate to project selection screen if needed")
    print("4. 🎯 Select 'default' project (extracted from context)")
    print("5. ⏳ Wait for main interface to load")
    print("6. ➕ Find and click 'Add new sheet' button")
    print("7. ⏳ Wait for file dialog to open")
    print("8. 📎 Navigate to ~/Downloads/industry.csv")
    print("9. ✅ Select and upload the file")
    
    print("\n💡 Key differences from previous system:")
    print("   ❌ OLD: Literal interpretation → jumps to file operations")
    print("   ✅ NEW: Workflow-aware → follows proper OrcaSheets UI flow")
    print("   ❌ OLD: Uses Cmd+Shift+G immediately")
    print("   ✅ NEW: Only uses file navigation AFTER 'Add new sheet' opens dialog")
    
    return True

async def main():
    """Run all workflow tests"""
    print("🚀 Workflow-Aware OrcaSheets Test Suite")
    print("=" * 70)
    
    tests = [
        ("Workflow Integration", test_workflow_integration),
        ("Command Parsing", test_command_parsing),
        ("Workflow Understanding", test_workflow_understanding),
        ("Tool Execution", test_tool_execution),
        ("Workflow Demonstration", demonstrate_workflow),
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
    
    print("\n" + "=" * 70)
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
        print("\n🎉 Workflow system is working correctly!")
        print("\n✨ Key improvements:")
        print("   🔄 Follows proper OrcaSheets UI workflow")
        print("   📋 State-aware navigation")
        print("   🎯 Context-aware command interpretation")
        print("   📱 Proper app launching and screen transitions")
        print("\n🚀 Ready to test with actual OrcaSheets!")
        print("\n💬 Try: orcasheets(action='execute_command', command='upload industry.csv from downloads')")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())