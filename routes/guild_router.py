from fastapi import APIRouter, HTTPException

from services import guild_service
from models.guild import CreateGuildImput, UpdateGuildInput, UpdateGuildUserInput

guild_router = APIRouter()


@guild_router.post("/")
async def create_guild(data: CreateGuildImput):
    return await guild_service.add_guild(data.guild_id)


@guild_router.get("/{guild_id}")
async def read_guild(guild_id: str):
    if not guild_id.isdigit():
        raise HTTPException(status_code=400, detail="guild_id must be a number string")

    return await guild_service.get_guild_data(guild_id)


@guild_router.post("/{guild_id}/channel")
async def update_channel(guild_id: str, data: UpdateGuildInput):
    if not guild_id.isdigit():
        raise HTTPException(status_code=400, detail="guild_id must be a number string")

    return await guild_service.set_channel(guild_id, data.channel_id)


@guild_router.post("/{guild_id}/user")
async def update_guild_user(guild_id: str, data: UpdateGuildUserInput):
    if not guild_id.isdigit():
        raise HTTPException(status_code=400, detail="guild_id must be a number string")

    if data.action == "add":
        return await guild_service.add_user(guild_id, data.user_id)
    elif data.action == "remove":
        return await guild_service.remove_user(guild_id, data.user_id)
