from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from core.config import Config


class DBClient:
    _client: AsyncIOMotorClient = AsyncIOMotorClient(Config.DATABASE_URL)
    _db: AsyncIOMotorDatabase = _client[Config.DATABASE_NAME]

    @classmethod
    def guilds(cls) -> AsyncIOMotorCollection:
        guild_collection: AsyncIOMotorCollection = cls._db["guilds"]
        return guild_collection
