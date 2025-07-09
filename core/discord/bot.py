import discord
from typing import List

from core.config import Config
from core.logger import logger
from models.discord import WebhookInfo, ChannelInfo, DiscordClientException


class DiscordBot:
    bot = discord.Bot()

    @classmethod
    async def run_bot(cls):
        await cls.bot.login(Config.BOT_TOKEN)
        logger.info(f"Logged in as: {cls.bot.user}")

    @classmethod
    async def close_conn(cls):
        await cls.bot.close()

    @classmethod
    async def _fetch_guild(cls, guild_id: int) -> discord.Guild:
        try:
            return await cls.bot.fetch_guild(guild_id)
        except discord.NotFound:
            raise DiscordClientException("Guild not found", status_code=404)
        except Exception as e:
            logger.exception("[DISCORD] Unexpected error fetching guild")
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
            logger.exception("[DISCORD] Unexpected error fetching channel")
            raise DiscordClientException("Failed to fetch channel", status_code=500)

    @classmethod
    async def _fetch_member(cls, guild: discord.Guild) -> discord.Member:
        try:
            return await guild.fetch_member(cls.bot.user.id)
        except discord.NotFound:
            raise DiscordClientException(
                "Bot is not a member of this guild", status_code=404
            )
        except Exception as e:
            logger.exception("[DISCORD] Unexpected error fetching bot member")
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
            logger.exception("[DISCORD] HTTP error while creating webhook")
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
