import httpx
from core.logger import logger


class DiscordUser:
    BASE_URL = "https://discord.com/api"
    CDN_URL = "https://cdn.discordapp.com"
    MANAGE_GUILD = 0x20

    def __init__(self, token: str):
        self.token = token
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL, headers={"Authorization": f"Bearer {self.token}"}
        )

    async def fetch_user(self) -> dict | None:
        try:
            response = await self.client.get("/users/@me")
            if response.status_code == 200:
                data = response.json()
                user_id = data["id"]
                avatar_hash = data.get("avatar")
                return {
                    "username": data.get("username"),
                    "avatar": (
                        f"{self.CDN_URL}/avatars/{user_id}/{avatar_hash}.png"
                        if avatar_hash
                        else None
                    ),
                }
            logger.warning(
                f"[DISCORD] Failed to fetch user: {response.status_code} - {response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"[DISCORD] Request error (user): {e}")
        return None

    async def fetch_manageable_guilds(self) -> list[dict]:
        try:
            response = await self.client.get("/users/@me/guilds")
            if response.status_code == 200:
                guilds = response.json()
                return [
                    {"id": guild["id"], "name": guild["name"]}
                    for guild in guilds
                    if int(guild.get("permissions", 0)) & self.MANAGE_GUILD
                ]
            logger.warning(
                f"[DISCORD] Failed to fetch guilds: {response.status_code} - {response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"[DISCORD] Request error (guilds): {e}")
        return []

    async def close(self):
        await self.client.aclose()
