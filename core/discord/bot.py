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
    async def create_webhook(
        cls, guild_id: str, channel_id: str, name: str = "webhook"
    ) -> WebhookInfo:
        guild = await cls.bot.fetch_guild(int(guild_id))
        if not guild:
            raise DiscordClientException("Guild not found", status_code=404)

        channel = await guild.fetch_channel(int(channel_id))
        if not isinstance(channel, discord.TextChannel):
            raise DiscordClientException(
                "Channel not found or not a text channel", status_code=400
            )

        try:
            webhook = await channel.create_webhook(name=name)
        except discord.Forbidden:
            raise DiscordClientException(
                "Bot is lacks permission to manage webhooks in this channel",
                status_code=403,
            )
        except discord.HTTPException as e:
            raise DiscordClientException(
                f"Failed to create webhook: {e}", status_code=500
            )

        return WebhookInfo(id=str(webhook.id), name=webhook.name, url=webhook.url)

    @classmethod
    async def get_manageable_channels(cls, guild_id: str) -> List[ChannelInfo]:
        guild = await cls.bot.fetch_guild(int(guild_id))
        if not guild:
            raise DiscordClientException("Guild not found", status_code=404)

        manageable = []
        channels = await guild.fetch_channels()
        for channel in channels:
            perms = channel.permissions_for(await guild.fetch_member(cls.bot.user.id))
            if perms.manage_webhooks and isinstance(channel, discord.TextChannel):
                manageable.append(ChannelInfo(id=str(channel.id), name=channel.name))

        return manageable
