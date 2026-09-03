from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str

    ai_provider: str = "mock"
    groq_api_key: str | None

    jwt_secret: str
    jwt_refresh_secret: str

    jwt_lifetime_minutes: int
    jwt_refresh_lifetime_seconds: int

    sql_echo: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()  # type: ignore
