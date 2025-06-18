#!/usr/bin/env python3
"""
Debug tool execution to see exactly what parameters are being passed.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def debug_tool_execution():
    """Debug tool execution step by step."""
    print("🔍 Debugging Tool Execution")
    print("=" * 40)
    
    try:
        # Step 1: Parse the command
        from orcasheets.tasks import TaskValidator
        
        command = "open orcasheets and upload industry.csv from downloads"
        print(f"1️⃣ Original command: {command}")
        
        task = TaskValidator.parse_user_request(command)
        if task:
            print(f"✅ Parsed successfully")
            print(f"   Task type: {task.task_type.value}")
            print(f"   File path: '{task.parameters.get('file_path')}'")
            print(f"   Project name: '{task.parameters.get('project_name')}'")
        else:
            print("❌ Failed to parse")
            return False
        
        # Step 2: Test the async wrapper
        from orcasheets.tools.async_wrapper import AsyncOrcaSheetsTool
        
        tool = AsyncOrcaSheetsTool()
        
        print(f"\n2️⃣ Calling async tool with exact parameters:")
        print(f"   task_type: {task.task_type.value}")
        print(f"   parameters: {task.parameters}")
        
        # Call the tool exactly as the framework would
        result = await tool(
            task_type=task.task_type.value,
            parameters=task.parameters
        )
        
        print(f"\n3️⃣ Tool execution result:")
        print(f"   Success: {not result.error}")
        if result.error:
            print(f"   Error: {result.error}")
        if result.output:
            print(f"   Output: {result.output}")
        
        # Step 3: Debug the underlying tool directly
        print(f"\n4️⃣ Testing underlying tool directly:")
        from orcasheets.tools.orcasheets_tool import OrcaSheetsTool
        
        direct_tool = OrcaSheetsTool()
        
        # Test file path handling
        file_path = task.parameters.get('file_path')
        print(f"   Original file_path: '{file_path}'")
        
        expanded = direct_tool.ui.expand_path(file_path)
        print(f"   Expanded path: '{expanded}'")
        
        exists = direct_tool.ui.file_exists(file_path)
        print(f"   File exists: {exists}")
        
        # Test direct os.path.isfile
        import os
        direct_exists = os.path.isfile(expanded)
        print(f"   Direct os.path.isfile: {direct_exists}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run debugging."""
    print("🚀 Tool Execution Debug")
    print("=" * 60)
    
    success = await debug_tool_execution()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Debug completed!")
    else:
        print("❌ Debug failed.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)