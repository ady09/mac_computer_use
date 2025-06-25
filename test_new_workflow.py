#!/usr/bin/env python3
"""
Test the updated OrcaSheets workflow
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.orcasheets.tool import OrcaSheetsTool

async def test_workflow():
    """Test the updated workflow"""
    print("Testing OrcaSheets workflow...")
    
    tool = OrcaSheetsTool()
    result = await tool.run_workflow(
        "Open orcasheets and upload industry.csv from downloads", 
        "~/Downloads/industry.csv"
    )
    
    print(f"Result: {result}")
    return result

if __name__ == "__main__":
    asyncio.run(test_workflow())