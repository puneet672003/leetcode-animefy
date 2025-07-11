from fastapi import HTTPException

from core.discord.bot import DiscordBot
from managers.guild_data import GuildManager
from models.discord import DiscordClientException


async def add_guild(guild_id: str):
    res = await GuildManager.init_guild(guild_id)
    if res is None:
        raise HTTPException(status_code=409, detail="Guild ID already exists")
    return res.model_dump()


async def get_guild_data(guild_id: str):
    guild = await GuildManager.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    return guild.model_dump()


async def get_guild_channels(guild_id: str):
    try:
        channels = await DiscordBot.get_manageable_channels(guild_id)
    except DiscordClientException as e:
        raise HTTPException(e.status_code, e.message)

    return [channel.model_dump() for channel in channels]


async def set_channel(guild_id: str, channel_id: str):
    try:
        webhook = await DiscordBot.create_webhook(guild_id, channel_id)
    except DiscordClientException as e:
        raise HTTPException(e.status_code, e.message)

    if not await GuildManager.set_channel_id(guild_id, channel_id):
        raise HTTPException(status_code=404, detail="Guild not found")

    updated_data = await GuildManager.set_webhook_id(guild_id, webhook.id)
    if not updated_data:
        raise HTTPException(status_code=404, detail="Guild not found")

    return updated_data.model_dump()


async def add_user(guild_id: str, username: str):
    updated_data = await GuildManager.add_leetcode_user(guild_id, username)
    if not updated_data:
        raise HTTPException(status_code=404, detail="Guild not found")

    return updated_data.model_dump()


async def remove_user(guild_id: str, username: str):
    updated_data = await GuildManager.remove_leetcode_user(guild_id, username)
    if not updated_data:
        raise HTTPException(status_code=404, detail="Guild not found")

    return updated_data.model_dump()
