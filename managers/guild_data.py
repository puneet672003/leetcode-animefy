from typing import Optional

from core.database import DBClient
from models.guild import GuildData


class GuildManager:
    @staticmethod
    async def init_guild(guild_id: str) -> GuildData:
        doc = {
            "guild_id": guild_id,
            "channel_id": None,
            "webhook_id": None,
            "leetcode_users": [],
        }

        await DBClient.guilds().insert_one(doc)
        return GuildData(**doc)

    @staticmethod
    async def get_guild(guild_id: str) -> Optional[GuildData]:
        doc = await DBClient.guilds().find_one({"guild_id": guild_id})
        return GuildData(**doc) if doc else None

    @staticmethod
    async def set_channel_id(guild_id: str, channel_id: str) -> Optional[GuildData]:
        doc = await DBClient.guilds().find_one_and_update(
            {"guild_id": guild_id},
            {"$set": {"channel_id": channel_id}},
            return_document=True,
        )
        return GuildData(**doc) if doc else None

    @staticmethod
    async def set_webhook_id(guild_id: str, webhook_id: str) -> GuildData:
        doc = await DBClient.guilds().find_one_and_update(
            {"guild_id": guild_id},
            {"$set": {"webhook_id": webhook_id}},
            return_document=True,
        )
        return GuildData(**doc)

    @staticmethod
    async def add_leetcode_user(guild_id: str, username: str) -> GuildData:
        doc = await DBClient.guilds().find_one_and_update(
            {"guild_id": guild_id},
            {"$addToSet": {"leetcode_users": username}},
            return_document=True,
        )
        return GuildData(**doc) if doc else None

    @staticmethod
    async def remove_leetcode_user(guild_id: str, username: str):
        doc = await DBClient.guilds().find_one_and_update(
            {"guild_id": guild_id},
            {"$pull": {"leetcode_users": username}},
            return_document=True,
        )
        return GuildData(**doc) if doc else None
