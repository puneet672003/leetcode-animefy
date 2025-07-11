import httpx
from typing import List, Optional

from core.logger import Logger
from models.discord import UserInfo, GuildInfo


class DiscordUser:
    BASE_URL = "https://discord.com/api"
    CDN_URL = "https://cdn.discordapp.com"
    MANAGE_GUILD = 0x20

    def __init__(self, token: str):
        self.token = token
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL, headers={"Authorization": f"Bearer {self.token}"}
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def fetch_user(self) -> Optional[UserInfo]:
        try:
            response = await self.client.get("/users/@me")
            if response.status_code == 200:
                data = response.json()
                return UserInfo(
                    username=data["username"],
                    avatar=(
                        f"{self.CDN_URL}/avatars/{data['id']}/{data['avatar']}.png"
                        if data.get("avatar")
                        else None
                    ),
                )
            Logger.warning(
                f"[DISCORD] Failed to fetch user: {response.status_code} - {response.text}"
            )
        except httpx.RequestError as e:
            Logger.error(f"[DISCORD] Request error (user): {e}")
        return None

    async def fetch_manageable_guilds(self) -> List[GuildInfo]:
        try:
            response = await self.client.get("/users/@me/guilds")
            if response.status_code == 200:
                guilds = response.json()
                return [
                    GuildInfo(
                        id=guild["id"],
                        name=guild["name"],
                        icon=(
                            f"{self.CDN_URL}/icons/{guild['id']}/{guild['icon']}.png"
                            if guild.get("icon")
                            else None
                        ),
                    )
                    for guild in guilds
                    if int(guild.get("permissions", 0)) & self.MANAGE_GUILD
                ]
            Logger.warning(
                f"[DISCORD] Failed to fetch guilds: {response.status_code} - {response.text}"
            )
        except httpx.RequestError as e:
            Logger.error(f"[DISCORD] Request error (guilds): {e}")
        return []

    async def close(self):
        await self.client.aclose()
