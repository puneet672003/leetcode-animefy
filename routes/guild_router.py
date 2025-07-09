from fastapi import APIRouter, Depends

from services import guild_service
from middlewares.guild_dependency import verify_guild_access
from models.guild import UpdateGuildInput, UpdateGuildUserInput

guild_router = APIRouter()


@guild_router.post("/{guild_id}")
async def create_guild(guild_id: str = Depends(verify_guild_access)):
    return await guild_service.add_guild(guild_id)


@guild_router.get("/{guild_id}")
async def read_guild(guild_id: str = Depends(verify_guild_access)):
    return await guild_service.get_guild_data(guild_id)


@guild_router.get("/{guild_id}/channel")
async def get_channels(guild_id: str = Depends(verify_guild_access)):
    return await guild_service.get_guild_channels(guild_id)


@guild_router.post("/{guild_id}/channel")
async def update_channel(
    data: UpdateGuildInput, guild_id: str = Depends(verify_guild_access)
):
    return await guild_service.set_channel(guild_id, data.channel_id)


@guild_router.post("/{guild_id}/user")
async def update_guild_user(
    data: UpdateGuildUserInput, guild_id: str = Depends(verify_guild_access)
):
    if data.action == "add":
        return await guild_service.add_user(guild_id, data.user_id)
    elif data.action == "remove":
        return await guild_service.remove_user(guild_id, data.user_id)
