import discord
from typing import List

from core.config import Config
from core.logger import logger
from models.discord import WebhookInfo, ChannelInfo, DiscordClientException


class DiscordBot:
    bot = discord.Bot()

    @classmethod
    async def run_bot(cls):
        @cls.bot.event
        async def on_ready():
            logger.info(f"[BOT] Logged in as {cls.bot.user}")

        await cls.bot.start(Config.BOT_TOKEN)

    @classmethod
    async def create_webhook(
        cls, guild_id: str, channel_id: str, name: str = "webhook"
    ) -> WebhookInfo:
        guild = cls.bot.get_guild(int(guild_id))
        if not guild:
            raise DiscordClientException("Guild not found", status_code=404)

        channel = guild.get_channel(int(channel_id))
        if not isinstance(channel, discord.TextChannel):
            raise DiscordClientException(
                "Channel not found or not a text channel", status_code=400
            )

        perms = channel.permissions_for(guild.me)
        if not perms.manage_webhooks:
            raise DiscordClientException(
                "Bot lacks permission to manage webhooks in this channel",
                status_code=403,
            )

        try:
            webhook = await channel.create_webhook(name=name)
        except discord.Forbidden:
            raise DiscordClientException(
                "Bot is forbidden from creating a webhook", status_code=403
            )
        except discord.HTTPException as e:
            raise DiscordClientException(
                f"Failed to create webhook: {e}", status_code=500
            )

        return WebhookInfo(id=str(webhook.id), name=webhook.name, url=webhook.url)

    @classmethod
    async def get_manageable_channels(guild_id: str) -> List[ChannelInfo]:
        guild = DiscordBot.bot.get_guild(int(guild_id))
        if not guild:
            raise DiscordClientException("Guild not found", status_code=404)

        manageable = []
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.manage_webhooks:
                manageable.append(ChannelInfo(id=str(channel.id), name=channel.name))

        return manageable
