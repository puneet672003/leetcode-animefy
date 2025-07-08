from typing import Optional
import redis.asyncio as redis

from core.config import Config
from core.logger import logger


class CacheStore:
    _client = redis.Redis(
        username="default",
        decode_responses=True,
        host=Config.CACHE_DB_HOST,
        port=Config.CACHE_DB_PORT,
        password=Config.CACHE_DB_PASSWORD,
    )

    # Log initialization
    logger.info("[CACHE] Async Redis client initialized")

    @classmethod
    async def set_cache(cls, key: str, value: str, ex: int = None) -> bool:
        return await cls._client.set(key, value, ex=ex)

    @classmethod
    async def get_cache(cls, key: str) -> Optional[str]:
        return await cls._client.get(key)

    @classmethod
    async def delete_cache(cls, key: str) -> bool:
        return bool(await cls._client.delete(key))

    @classmethod
    async def exists(cls, key: str) -> bool:
        return bool(await cls._client.exists(key))
