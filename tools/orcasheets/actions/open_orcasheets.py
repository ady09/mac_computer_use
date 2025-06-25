from .base import BaseAction
from tools.computer import ComputerTool
import asyncio

class OpenOrcaSheetsAction(BaseAction):
    def __init__(self, computer: ComputerTool):
        super().__init__(computer)

    async def run(self):
        # Open Spotlight (Cmd+Space)
        await self.computer(action="key", text="command+space")
        await asyncio.sleep(1)
        # Type 'OrcaSheets'
        await self.type_text("OrcaSheets")
        await asyncio.sleep(0.5)
        # Press Enter
        await self.press_key("Return")
        await asyncio.sleep(3)  # Wait for app to launch
        return {"status": "orcasheets_opened"} 