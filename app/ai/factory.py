from functools import lru_cache

from app.ai.chat.abc import AIChat
from app.ai.chat.mock import MockAIChat
from app.ai.retrieval.abc import AIRetrieval
from app.ai.retrieval.mock import MockAIRetrieval
from app.core.config import get_settings


@lru_cache
def get_ai_chat() -> AIChat:
    settings = get_settings()

    if settings.ai_provider == "groq":
        if not settings.groq_api_key or not settings.groq_model:
            raise ValueError("AI_PROVIDER is set to 'groq', but GROQ_API_KEY or GROQ_MODEL is missing.")

        from app.ai.chat.groq import GroqAIChat

        return GroqAIChat(api_key=settings.groq_api_key, model=settings.groq_model)

    return MockAIChat()


@lru_cache
def get_ai_retrieval() -> AIRetrieval:
    settings = get_settings()

    if settings.ai_retrieval == "qdrant":
        from app.ai.retrieval.qdrant import QdrantAIRetrieval

        return QdrantAIRetrieval()

    return MockAIRetrieval()
