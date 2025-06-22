#!/usr/bin/env python3
"""
Example demonstrating how to use OrcaSheets tool directly.
This shows how the tool would be called from the Claude assistant.
"""

import asyncio
from tools import OrcaSheetsTool

async def example_usage():
    """Example of how Claude would use the OrcaSheets tool"""
    
    tool = OrcaSheetsTool()
    
    print("🔧 OrcaSheets Tool Usage Examples")
    print("=" * 50)
    
    # Example 1: Full workflow (what happens when user says "Open OrcaSheets and upload industry.csv")
    print("\n📋 Example 1: Full Workflow")
    print("User prompt: 'Open OrcaSheets and upload industry.csv from Downloads'")
    print("Tool call: orcasheets(action='full_workflow', file_path='~/Downloads/industry.csv')")
    
    # Note: This would actually try to open OrcaSheets, so we'll just show the call
    # result = await tool(action="full_workflow", file_path="~/Downloads/industry.csv")
    print("(Would execute full workflow: open app → select default project → upload file)")
    
    # Example 2: Step by step
    print("\n📋 Example 2: Step-by-step workflow")
    print("User prompt: 'Open OrcaSheets, select My Project, then upload data.csv'")
    
    print("Tool call 1: orcasheets(action='open_app')")
    # result1 = await tool(action="open_app")
    
    print("Tool call 2: orcasheets(action='select_project', project_name='My Project')")
    # result2 = await tool(action="select_project", project_name="My Project")
    
    print("Tool call 3: orcasheets(action='upload_file', file_path='~/Downloads/data.csv')")
    # result3 = await tool(action="upload_file", file_path="~/Downloads/data.csv")
    
    # Example 3: Just open the app
    print("\n📋 Example 3: Just open OrcaSheets")
    print("User prompt: 'Open OrcaSheets application'")
    print("Tool call: orcasheets(action='open_app')")
    
    # Example 4: Take screenshot for debugging
    print("\n📋 Example 4: Debug screenshot")
    print("Claude can take screenshots to see current state:")
    result = await tool(action="take_screenshot")
    print(f"Result: {result.output}")
    
    print("\n✨ Integration Complete!")
    print("The OrcaSheets tool is now available in your Claude Computer Use dashboard.")
    print("Try prompts like:")
    print("  • 'Open OrcaSheets and upload industry.csv from Downloads'")
    print("  • 'Use OrcaSheets to upload data.csv to My Project'") 
    print("  • 'Open OrcaSheets application'")

if __name__ == "__main__":
    asyncio.run(example_usage())