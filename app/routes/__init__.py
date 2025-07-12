from fastapi import APIRouter
from routes.guild_router import guild_router
from routes.schedule_router import schedule_router

from core.config import Config


global_router = APIRouter(prefix="/api")

if Config.APP_TYPE == "scheduler":
    global_router.include_router(schedule_router, prefix="/schedule")
else:
    global_router.include_router(guild_router, prefix="/guild")
