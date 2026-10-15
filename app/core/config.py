from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    test_database_url: str

    redis_url: str

    ai_provider: str = "mock"
    ai_retrieval: str = "mock"

    groq_api_key: SecretStr | None = None
    groq_model: str | None = None

    jwt_secret: str
    jwt_refresh_secret: str

    jwt_lifetime_minutes: int
    jwt_refresh_lifetime_minutes: int

    sql_echo: bool = False

    phoenix_collector_endpoint: str

    vector_database_url: str
    qdrant_collection_name: str
    embedding_model: str

    retrieval_score_threshold: float = 0.85

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()  # type: ignore
