from abc import ABC, abstractmethod

class CheckSystem(ABC):
    @abstractmethod
    async def check(self, url) -> bool: pass