from app.ai.retrieval.abc import AIRetrieval


class MockAIRetrieval(AIRetrieval):
    async def search(self, query: str) -> list[str]:
        return ["test document text 1", "test document text 2", "test document text 3"]
