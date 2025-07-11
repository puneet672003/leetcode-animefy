from typing import Optional
from upstash_redis.asyncio import Redis

from core.config import Config
from core.logger import Logger


class CacheStore:
    _client: Redis = None

    @classmethod
    def _get_client(cls) -> Redis:
        if cls._client is None:
            Logger.info("[CACHE] Initializing redis client")
            cls._client = Redis(Config.CACHE_ENDPOINT, token=Config.CACHE_TOKEN)
        return cls._client

    @classmethod
    async def set_cache(cls, key: str, value: str, ex: int = None) -> bool:
        return await cls._get_client().set(key, value, ex=ex)

    @classmethod
    async def get_cache(cls, key: str) -> Optional[str]:
        return await cls._get_client().get(key)

    @classmethod
    async def delete_cache(cls, key: str) -> bool:
        return bool(await cls._get_client().delete(key))

    @classmethod
    async def exists(cls, key: str) -> bool:
        return bool(await cls._get_client().exists(key))
