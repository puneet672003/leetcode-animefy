import discord
from fastapi import HTTPException

from core.discord.bot import DiscordBot
from core.logger import Logger
from managers.guild_data import GuildManager
from managers.leetcode_manager import LeetCodeManager
from models.auth import SessionData
from models.discord import DiscordClientException
from models.guild import ParsedSlot
from models.leetcode import UserProgress
from services import leetcode_service, plot_service


async def _classify_users(
    guild_id: str, usernames: list[str]
) -> tuple[list[str], list[str], dict[str, dict]]:
    veterans, recruits, stats_map = [], [], {}
    for username in usernames:
        stats = await LeetCodeManager.get_user_stats(guild_id, username)
        if stats:
            veterans.append(username)
            stats_map[username] = stats
        else:
            recruits.append(username)
    return veterans, recruits, stats_map


def _get_mode(veteran_count: int, recruit_count: int) -> str:
    if veteran_count > 1:
        return "battle"
    elif veteran_count == 1:
        return "solo"
    elif recruit_count > 0:
        return "intro"
    return "not_configured"


async def get_user_guilds(session_data: SessionData):
    bot_guild_ids = await DiscordBot.fetch_guild_ids()
    with_bot = []
    without_bot = []
    for guild in session_data.guilds:
        if guild.id in bot_guild_ids:
            with_bot.append(guild.model_dump())
        else:
            without_bot.append(guild.model_dump())
    return {"with_bot": with_bot, "without_bot": without_bot}


async def add_guild(guild_id: str):
    res = await GuildManager.init_guild(guild_id)
    if res is None:
        raise HTTPException(status_code=409, detail="Guild ID already exists")
    return res.model_dump()


async def get_guild_data(guild_id: str):
    guild = await GuildManager.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    veterans, recruits, _ = await _classify_users(guild_id, guild.leetcode_users)

    return {
        **guild.model_dump(),
        "veterans": veterans,
        "recruits": recruits,
        "mode": _get_mode(len(veterans), len(recruits)),
        "is_configured": bool(guild.webhook_id and guild.slot and guild.leetcode_users),
    }


async def get_guild_channels(guild_id: str):
    try:
        channels = await DiscordBot.get_manageable_channels(guild_id)
    except DiscordClientException as e:
        raise HTTPException(e.status_code, e.message)

    return [channel.model_dump() for channel in channels]


async def set_channel(guild_id: str, channel_id: str):
    guild = await GuildManager.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    try:
        webhook = await DiscordBot.create_webhook(guild_id, channel_id)
    except DiscordClientException as e:
        raise HTTPException(e.status_code, e.message)

    if guild.webhook_id:
        await DiscordBot.delete_webhook(guild.webhook_id)

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

    veterans, recruits, _ = await _classify_users(guild_id, updated_data.leetcode_users)
    return {
        **updated_data.model_dump(),
        "veterans": veterans,
        "recruits": recruits,
        "mode": _get_mode(len(veterans), len(recruits)),
    }


async def remove_user(guild_id: str, username: str):
    updated_data = await GuildManager.remove_leetcode_user(guild_id, username)
    if not updated_data:
        raise HTTPException(status_code=404, detail="Guild not found")

    veterans, recruits, _ = await _classify_users(guild_id, updated_data.leetcode_users)
    return {
        **updated_data.model_dump(),
        "veterans": veterans,
        "recruits": recruits,
        "mode": _get_mode(len(veterans), len(recruits)),
    }


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

            veteran_names, recruit_names, stats_map = await _classify_users(
                guild.guild_id, guild.leetcode_users
            )

            improvement_map = {}
            veterans: list[UserProgress] = []
            recruits: list[UserProgress] = []

            for username in guild.leetcode_users:
                try:
                    progress = await leetcode_service.get_user_progress(username)
                    current_total = sum(d.count for d in progress.progress)

                    if username in stats_map:
                        last_count = int(stats_map[username].get("last_count", 0))
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
                mode = _get_mode(len(veterans), len(recruits))

                if mode == "battle":
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

                    embed.set_footer(text="Generated by LeetJutsu")

                elif mode == "solo":
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
                        value=result["leaderboard"],
                        inline=False,
                    )

                    if recruits:
                        recruit_names = ", ".join([f"`{u.username}`" for u in recruits])
                        embed.add_field(
                            name="New Challengers Appears for Next Battle",
                            value=recruit_names,
                            inline=False,
                        )

                    embed.set_footer(text="Generated by LeetJutsu")

                elif mode == "intro":
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

                try:
                    await DiscordBot.send_webhook_message(guild.webhook_id, embed=embed)
                    Logger.info(f"Sent output to guild {guild.guild_id}")
                except DiscordClientException as e:
                    if e.status_code == 404:
                        Logger.warning(
                            f"Webhook not found for guild {guild.guild_id}, clearing webhook_id."
                        )
                        await GuildManager.clear_webhook_id(guild.guild_id)
                    else:
                        Logger.error(
                            f"Failed to send message for guild {guild.guild_id}: {e}"
                        )

            except Exception as e:
                Logger.error(
                    f"Failed to generate/send content for guild {guild.guild_id}: {e}"
                )
