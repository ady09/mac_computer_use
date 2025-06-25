from abc import ABC, abstractmethod

class BaseAction(ABC):
    def __init__(self, computer):
        self.computer = computer

    @abstractmethod
    async def run(self, *args, **kwargs):
        """Run the action. To be implemented by subclasses."""
        pass

    async def type_text(self, text: str):
        await self.computer(action="type", text=text)

    async def press_key(self, key: str):
        await self.computer(action="key", text=key) 