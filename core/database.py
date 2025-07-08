from motor.motor_asyncio import AsyncIOMotorClient

from core.config import Config


class DBClient:
    _client = AsyncIOMotorClient(Config.DATABASE_URL)
    _db = _client[Config.DATABASE_NAME]

    @classmethod
    def get_collection(cls, name):
        return cls._db[name]
