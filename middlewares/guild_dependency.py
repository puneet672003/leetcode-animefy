from fastapi import Request, HTTPException, Path

from core.logger import logger
from models.auth import SessionData


async def verify_guild_access(request: Request, guild_id: str = Path(...)) -> str:
    is_authenticated = getattr(request.state, "is_authenticated", False)
    if not is_authenticated:
        raise HTTPException(status_code=401, detail="Authentication required")

    session_data: SessionData = getattr(request.state, "session_data", None)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    user_guild_ids = [guild.id for guild in session_data.guilds]
    if guild_id not in user_guild_ids:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: You don't have permission to manage guild {guild_id}",
        )

    logger.info(
        f"[GUILD_AUTH] User {session_data.user.username} granted access to guild {guild_id}"
    )
    return guild_id
