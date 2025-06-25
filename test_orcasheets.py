#!/usr/bin/env python3
"""
Simple test script to debug OrcaSheets automation
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.computer import ComputerTool

async def test_orcasheets_simple():
    """Test OrcaSheets automation step by step"""
    computer = ComputerTool()
    
    print("Step 1: Taking screenshot to see current state")
    screenshot = await computer(action="screenshot")
    print(f"Screenshot taken: {bool(screenshot.base64_image)}")
    
    print("Step 2: Click NEW PROJECT button at coordinates (745, 202)")
    await computer(action="mouse_move", coordinate=[745, 202])
    await asyncio.sleep(0.5)
    await computer(action="left_click")
    await asyncio.sleep(2)
    
    print("Step 3: Taking screenshot to see if dropdown appeared")
    screenshot2 = await computer(action="screenshot")
    print(f"Screenshot taken: {bool(screenshot2.base64_image)}")
    
    print("Step 4: Click on 'Open files' option (estimated at 745, 240)")
    await computer(action="mouse_move", coordinate=[745, 240])
    await asyncio.sleep(0.5)
    await computer(action="left_click")
    await asyncio.sleep(2)
    
    print("Step 5: Type file path in file dialog")
    await computer(action="type", text="~/Downloads/industry.csv")
    await asyncio.sleep(0.5)
    
    print("Step 6: Press Enter to submit")
    await computer(action="key", text="Return")
    await asyncio.sleep(2)
    
    print("Done!")

if __name__ == "__main__":
    asyncio.run(test_orcasheets_simple())