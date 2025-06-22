#!/usr/bin/env python3
"""
Example usage of OrcaSheets Automation Framework

This script demonstrates how to use the OrcaSheets automation tools
to perform various tasks like opening the app, selecting projects, and uploading files.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to Python path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from tools.orcasheets.orcasheets_automation import OrcaSheetsAutomation, automate_orcasheets
from tools.orcasheets.core.tasks import TaskRegistry, WORKFLOWS
from tools.orcasheets.core.applescript_helper import AppleScriptHelper


async def example_basic_usage():
    """Example of basic usage - upload a file"""
    print("=== Basic Usage Example ===")
    
    # Simple one-liner to upload a file
    file_path = "~/Downloads/industry.csv"  # Adjust path as needed
    project_name = "default"
    
    success = await automate_orcasheets(file_path, project_name)
    print(f"Upload result: {'Success' if success else 'Failed'}")


async def example_step_by_step():
    """Example of step-by-step automation"""
    print("\n=== Step-by-Step Example ===")
    
    automation = OrcaSheetsAutomation()
    
    try:
        # Step 1: Open the app
        print("1. Opening OrcaSheets...")
        await automation.search_and_open_app("OrcaSheets")
        await automation.wait_for_app_launch()
        
        # Step 2: Take a debug screenshot
        print("2. Taking debug screenshot...")
        await automation.take_debug_screenshot("after_launch.png")
        
        # Step 3: Select project
        print("3. Selecting project...")
        await automation.select_project("default")
        
        # Step 4: Add new sheet and upload
        print("4. Uploading file...")
        await automation.add_new_sheet()
        await automation.upload_file("~/Downloads/industry.csv")
        
        print("Step-by-step automation completed!")
        
    except Exception as e:
        print(f"Error during automation: {e}")


async def example_using_task_registry():
    """Example using the task registry system"""
    print("\n=== Task Registry Example ===")
    
    automation = OrcaSheetsAutomation()
    registry = TaskRegistry()
    
    # List available tasks
    print("Available tasks:", registry.list_tasks())
    
    # Execute individual tasks
    print("Executing tasks...")
    
    # Open app
    success = await registry.execute_task("open_app", automation)
    print(f"Open app: {'Success' if success else 'Failed'}")
    
    # Select project
    success = await registry.execute_task("select_project", automation, project_name="default")
    print(f"Select project: {'Success' if success else 'Failed'}")
    
    # Upload file
    success = await registry.execute_task("upload_file", automation, file_path="~/Downloads/industry.csv")
    print(f"Upload file: {'Success' if success else 'Failed'}")


async def example_using_workflow():
    """Example using predefined workflows"""
    print("\n=== Workflow Example ===")
    
    automation = OrcaSheetsAutomation()
    registry = TaskRegistry()
    
    # Execute the complete upload workflow
    workflow_tasks = WORKFLOWS["upload_file"]
    print(f"Executing workflow: {workflow_tasks}")
    
    success = await registry.execute_workflow(
        workflow_tasks, 
        automation,
        project_name="default",
        file_path="~/Downloads/industry.csv"
    )
    
    print(f"Workflow result: {'Success' if success else 'Failed'}")


async def example_applescript_integration():
    """Example using AppleScript for more reliable automation"""
    print("\n=== AppleScript Integration Example ===")
    
    # Check if OrcaSheets is running
    is_running = await AppleScriptHelper.is_application_running("OrcaSheets")
    print(f"OrcaSheets running: {is_running}")
    
    # Open OrcaSheets using AppleScript
    if not is_running:
        print("Opening OrcaSheets with AppleScript...")
        success = await AppleScriptHelper.open_application("OrcaSheets")
        print(f"Open result: {'Success' if success else 'Failed'}")
        
        # Wait a bit for the app to launch
        await asyncio.sleep(3)
    
    # Get window information
    windows = await AppleScriptHelper.get_application_windows("OrcaSheets")
    print(f"OrcaSheets windows: {windows}")
    
    # Try to get UI elements (this might be useful for debugging)
    ui_elements = await AppleScriptHelper.get_ui_elements("OrcaSheets")
    if ui_elements:
        print(f"UI elements found: {len(ui_elements)} characters of data")


async def example_with_different_project():
    """Example uploading to a different project"""
    print("\n=== Different Project Example ===")
    
    # Upload to a specific project (not default)
    file_path = "~/Downloads/industry.csv"
    project_name = "My Project"  # Change this to an actual project name
    
    automation = OrcaSheetsAutomation()
    success = await automation.full_workflow(file_path, project_name)
    print(f"Upload to '{project_name}': {'Success' if success else 'Failed'}")


async def debug_current_screen():
    """Helper function to debug current screen state"""
    print("\n=== Debug Current Screen ===")
    
    automation = OrcaSheetsAutomation()
    
    # Take screenshot and save it
    screenshot = await automation.take_debug_screenshot("current_screen.png")
    print("Screenshot saved as current_screen.png")
    
    # You can examine the screenshot to adjust coordinates if needed


def main():
    """Main function to run examples"""
    print("OrcaSheets Automation Framework Examples")
    print("=" * 50)
    
    # You can uncomment the examples you want to run:
    
    # Basic usage
    # asyncio.run(example_basic_usage())
    
    # Step by step
    # asyncio.run(example_step_by_step())
    
    # Task registry
    # asyncio.run(example_using_task_registry())
    
    # Workflow
    # asyncio.run(example_using_workflow())
    
    # AppleScript integration
    # asyncio.run(example_applescript_integration())
    
    # Different project
    # asyncio.run(example_with_different_project())
    
    # Debug screen
    asyncio.run(debug_current_screen())
    
    print("\nDone! Check the output above for results.")
    print("\nTo run specific examples, uncomment them in the main() function.")


if __name__ == "__main__":
    main()