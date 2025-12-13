from typing import Optional, Dict

from core.config import Config
from core.database import DBClient

class LeetCodeManager:
    table_name = f"{Config.REPO_NAME}-db-user-stats-v2"

    @classmethod
    async def get_user_stats(cls, guild_id: str, username: str) -> Optional[Dict]:
        return await DBClient.get_item(
            table_name=cls.table_name,
            key={
                "guild_id": guild_id,
                "username": username
            }
        )

    @classmethod
    async def update_user_stats(cls, guild_id: str, username: str, total_solved: int) -> None:
        await DBClient.put_item(
            table_name=cls.table_name,
            item={
                "guild_id": guild_id,
                "username": username,
                "last_count": total_solved
            }
        )
