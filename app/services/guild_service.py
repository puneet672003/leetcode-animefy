import discord
from fastapi import HTTPException

from core.discord.bot import DiscordBot
from core.logger import Logger
from managers.guild_data import GuildManager
from managers.leetcode_manager import LeetCodeManager
from models.discord import DiscordClientException
from models.guild import ParsedSlot
from models.leetcode import UserProgress
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
                Logger.warning(
                    f"No webhook configured for guild {guild.guild_id}, skipping."
                )
                continue

            improvement_map = {}
            veterans: list[UserProgress] = []
            recruits: list[UserProgress] = []

            for username in guild.leetcode_users:
                try:
                    progress = await leetcode_service.get_user_progress(username)
                    current_total = sum(d.count for d in progress.progress)

                    try:
                        stats = await LeetCodeManager.get_user_stats(
                            guild.guild_id, username
                        )
                    except Exception as e:
                        Logger.warning(
                            f"Failed to get user stats for {username} in guild {guild.guild_id}: {e}"
                        )
                        stats = None

                    if stats:
                        last_count = int(stats.get("last_count", 0))
                        delta = current_total - last_count
                        improvement_map[username] = delta if delta > 0 else 0
                        veterans.append(progress)
                    else:
                        recruits.append(progress)

                    await LeetCodeManager.update_user_stats(
                        guild.guild_id, username, current_total
                    )

                except Exception as e:
                    Logger.error(
                        f"Failed to fetch/update progress for {username} in guild {guild.guild_id}: {e}"
                    )

            if not veterans and not recruits:
                Logger.info(f"No valid user data for guild {guild.guild_id}, skipping.")
                continue

            try:
                if len(veterans) > 1:
                    result = await plot_service.generate_scene(
                        veterans, improvement_map, prompt_name="battle"
                    )
                    embed = discord.Embed(
                        title="⚔️ LeetCode Battle Results ⚔️",
                        description=result["plot"],
                        color=discord.Color.brand_red(),
                    )
                    embed.add_field(
                        name="🏆 Winner", value=f"**{result['winner']}**", inline=True
                    )
                    embed.add_field(
                        name="📊 Leaderboard", value=result["leaderboard"], inline=True
                    )

                    if recruits:
                        recruit_names = ", ".join([f"`{u.username}`" for u in recruits])
                        embed.add_field(
                            name="New Challengers Appears for Next Battle",
                            value=recruit_names,
                            inline=False,
                        )

                    embed.set_footer(text="Generated by Animefy Bot")
                    await DiscordBot.send_webhook_message(guild.webhook_id, embed=embed)

                elif len(veterans) == 1:
                    result = await plot_service.generate_scene(
                        veterans, improvement_map, prompt_name="solo"
                    )
                    embed = discord.Embed(
                        title="⚔️ LeetCode Solo Battle Results ⚔️",
                        description=result["plot"],
                        color=discord.Color.brand_red(),
                    )
                    embed.add_field(
                        name="🏆 Improvement",
                        value=f"**{result['winner']}**",
                        inline=False,
                    )
                    embed.set_footer(text="Generated by Animefy Bot")
                    await DiscordBot.send_webhook_message(guild.webhook_id, embed=embed)

                elif len(recruits) > 0:
                    result = await plot_service.generate_scene(
                        recruits, prompt_name="intro"
                    )
                    embed = discord.Embed(
                        title="🔥 A New Era Begins... 🔥",
                        description=result["plot"],
                        color=discord.Color.gold(),
                    )
                    recruit_names = ", ".join([f"**{u.username}**" for u in recruits])
                    embed.add_field(
                        name="🌟 The Founding Warriors",
                        value=recruit_names,
                        inline=False,
                    )
                    embed.set_footer(
                        text="Stats are being recorded. The first battle begins tomorrow!"
                    )

                    await DiscordBot.send_webhook_message(guild.webhook_id, embed=embed)

                Logger.info(f"Sent output to guild {guild.guild_id}")

            except Exception as e:
                Logger.error(
                    f"Failed to generate/send content for guild {guild.guild_id}: {e}"
                )
