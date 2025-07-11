from typing import Optional

from core.database import DBClient
from models.guild import GuildData


class GuildManager:
    table_name = "guilds"

    @staticmethod
    async def get_guild(guild_id: str) -> Optional[GuildData]:
        doc = await DBClient.get_item(GuildManager.table_name, {"guild_id": guild_id})
        return GuildData(**doc) if doc else None

    @staticmethod
    async def init_guild(guild_id: str) -> GuildData:
        guild = await GuildManager.get_guild(guild_id)
        if guild is None:
            doc = GuildData(
                guild_id=guild_id,
                channel_id=None,
                webhook_id=None,
                leetcode_users=[],
            )
            await DBClient.put_item(GuildManager.table_name, doc.model_dump())
            return doc

    @staticmethod
    async def set_channel_id(guild_id: str, channel_id: str) -> Optional[GuildData]:
        updated = await DBClient.update_item(
            GuildManager.table_name,
            {"guild_id": guild_id},
            "SET channel_id = :c",
            {":c": channel_id},
        )
        return GuildData(**updated) if updated else None

    @staticmethod
    async def set_webhook_id(guild_id: str, webhook_id: str) -> Optional[GuildData]:
        updated = await DBClient.update_item(
            GuildManager.table_name,
            {"guild_id": guild_id},
            "SET webhook_id = :w",
            {":w": webhook_id},
        )
        return GuildData(**updated) if updated else None

    @staticmethod
    async def add_leetcode_user(guild_id: str, username: str) -> Optional[GuildData]:
        guild = await GuildManager.get_guild(guild_id)
        if not guild:
            return None
        if username not in guild.leetcode_users:
            guild.leetcode_users.append(username)
            await DBClient.put_item(GuildManager.table_name, guild.model_dump())
        return guild

    @staticmethod
    async def remove_leetcode_user(guild_id: str, username: str) -> Optional[GuildData]:
        guild = await GuildManager.get_guild(guild_id)
        if not guild:
            return None
        if username in guild.leetcode_users:
            guild.leetcode_users.remove(username)
            await DBClient.put_item(GuildManager.table_name, guild.model_dump())
        return guild
