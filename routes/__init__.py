from fastapi import APIRouter
from routes.guild_router import guild_router

global_router = APIRouter(prefix="/api")

# Include other routers
global_router.include_router(guild_router, prefix="/guild")
