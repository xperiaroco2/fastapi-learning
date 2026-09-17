from redis.asyncio import Redis, from_url

from app.core.config import get_settings

redis_client: Redis | None = None


async def connect_redis() -> None:
    global redis_client
    redis_client = from_url(get_settings().redis_url, encoding="utf-8", decode_responses=True)
    await redis_client.ping()


async def close_redis() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None


async def get_redis() -> Redis:
    if not redis_client:
        raise RuntimeError("Redis is not initialized")
    return redis_client
