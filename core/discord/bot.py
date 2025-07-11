import discord
from typing import List

from core.config import Config
from core.logger import Logger
from models.discord import WebhookInfo, ChannelInfo, DiscordClientException


class DiscordBot:
    _bot: discord.Bot = None
    _logged_in: bool = False

    @classmethod
    async def _get_bot(cls) -> discord.Bot:
        if cls._bot is None:
            cls._bot = discord.Bot(intents=discord.Intents.none())

        if not cls._logged_in:
            try:
                await cls._bot.login(Config.BOT_TOKEN)
                Logger.info(f"[DISCORD] Logged in as: {cls._bot.user}")
                cls._logged_in = True
            except discord.HTTPException as e:
                Logger.error("[DISCORD] Failed to login", exc=e)
                raise DiscordClientException("Bot login failed", status_code=401)

        return cls._bot

    @classmethod
    async def close(cls):
        if cls._bot and cls._logged_in:
            await cls._bot.close()
            cls._logged_in = False

    @classmethod
    async def _fetch_guild(cls, guild_id: int) -> discord.Guild:
        bot = await cls._get_bot()
        try:
            return await bot.fetch_guild(guild_id)
        except discord.NotFound:
            raise DiscordClientException("Guild not found", status_code=404)
        except Exception as e:
            Logger.warning(
                f"[DISCORD] Unexpected error fetching guild: {guild_id}: {e}"
            )
            raise DiscordClientException("Failed to fetch guild", status_code=500)

    @classmethod
    async def _fetch_channel(
        cls, guild: discord.Guild, channel_id: int
    ) -> discord.abc.GuildChannel:
        try:
            return await guild.fetch_channel(channel_id)
        except discord.NotFound:
            raise DiscordClientException("Channel not found", status_code=404)
        except Exception as e:
            Logger.warning(
                f"[DISCORD] Unexpected error fetching channel: {channel_id}: {e}"
            )
            raise DiscordClientException("Failed to fetch channel", status_code=500)

    @classmethod
    async def _fetch_member(cls, guild: discord.Guild) -> discord.Member:
        bot = await cls._get_bot()
        try:
            return await guild.fetch_member(bot.user.id)
        except discord.NotFound:
            raise DiscordClientException(
                "Bot is not a member of this guild", status_code=404
            )
        except Exception as e:
            Logger.warning(f"[DISCORD] Unexpected error fetching bot member: {e}")
            raise DiscordClientException("Failed to fetch bot member", status_code=500)

    @classmethod
    async def create_webhook(
        cls, guild_id: str, channel_id: str, name: str = "webhook"
    ) -> WebhookInfo:
        guild = await cls._fetch_guild(int(guild_id))
        channel = await cls._fetch_channel(guild, int(channel_id))

        if not isinstance(channel, discord.TextChannel):
            raise DiscordClientException(
                "Channel is not a text channel", status_code=400
            )

        try:
            webhook = await channel.create_webhook(name=name)
        except discord.Forbidden:
            raise DiscordClientException(
                "Bot lacks permission to manage webhooks in this channel",
                status_code=403,
            )
        except discord.HTTPException as e:
            Logger.warning(f"[DISCORD] HTTP error while creating webhook: {e}")
            raise DiscordClientException(
                f"Failed to create webhook: {e}", status_code=500
            )

        return WebhookInfo(id=str(webhook.id), name=webhook.name, url=webhook.url)

    @classmethod
    async def get_manageable_channels(cls, guild_id: str) -> List[ChannelInfo]:
        guild = await cls._fetch_guild(int(guild_id))
        bot_member = await cls._fetch_member(guild)
        channels = await guild.fetch_channels()

        manageable = []
        for channel in channels:
            if isinstance(channel, discord.TextChannel):
                perms = channel.permissions_for(bot_member)
                if perms.manage_webhooks:
                    manageable.append(
                        ChannelInfo(id=str(channel.id), name=channel.name)
                    )

        return manageable
