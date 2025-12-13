from fastapi import HTTPException

from core.logger import Logger
from core.discord.bot import DiscordBot
from models.guild import ParsedSlot
from models.discord import DiscordClientException
from managers.guild_data import GuildManager
from services import leetcode_service, plot_service


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


async def set_slot(guild_id: str, slot: ParsedSlot):
    updated_data = await GuildManager.set_slot(guild_id, f"{slot.hh}:{slot.mm}")
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


async def run_slot_jobs(slot: ParsedSlot):
    guilds = await GuildManager.get_guilds_by_slot(f"{slot.hh}:{slot.mm}")
    
    if guilds and len(guilds) > 0:
        for guild in guilds:
            Logger.info(f"Running for {guild.guild_id}")
            if not guild.webhook_id:
                Logger.warning(f"No webhook configured for guild {guild.guild_id}, skipping.")
                continue

            users_progress = []
            for username in guild.leetcode_users:
                try:
                    progress = await leetcode_service.get_user_progress(username)
                    users_progress.append(progress)
                except Exception as e:
                    Logger.error(f"Failed to fetch progress for {username} in guild {guild.guild_id}: {e}")
            
            if not users_progress:
                Logger.info(f"No valid user data for guild {guild.guild_id}, skipping plot generation.")
                continue

            try:
                scene = await plot_service.generate_battle_scene(users_progress)
                await DiscordBot.send_webhook_message(guild.webhook_id, scene)
                Logger.info(f"Sent battle scene to guild {guild.guild_id}")
            except Exception as e:
                Logger.error(f"Failed to generate/send battle scene for guild {guild.guild_id}: {e}")
