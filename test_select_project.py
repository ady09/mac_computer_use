#!/usr/bin/env python3
"""
Test selecting an existing project workflow
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.orcasheets.tool import OrcaSheetsTool

async def test_select_project():
    """Test selecting existing project workflow"""
    print("Testing 'select default project' workflow...")
    
    tool = OrcaSheetsTool()
    result = await tool.run_workflow(
        "Open orcasheets and select default project and upload industry.csv from downloads", 
        "~/Downloads/industry.csv",
        "default"
    )
    
    print(f"Result: {result}")
    return result

if __name__ == "__main__":
    asyncio.run(test_select_project())