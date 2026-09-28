from abc import ABC, abstractmethod


class AIRetrieval(ABC):
    @abstractmethod
    async def search(self, query: str) -> list[str]:
        pass
