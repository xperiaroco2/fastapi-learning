from functools import lru_cache

from app.ai.mock import MockAIProvider
from app.ai.provider import AIProvider
from app.core.config import get_settings


@lru_cache
def get_ai_provider() -> AIProvider:
    settings = get_settings()

    if settings.ai_provider == "groq":
        if not settings.groq_api_key or not settings.groq_model:
            raise ValueError("AI_PROVIDER is set to 'groq', but GROQ_API_KEY or GROQ_MODEL is missing.")

        from app.ai.groq import GroqAIProvider

        return GroqAIProvider(api_key=settings.groq_api_key, model=settings.groq_model)

    return MockAIProvider()
