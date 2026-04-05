from fastapi import APIRouter

from core.config import Config
from routes.auth_router import auth_router
from routes.guild_router import guild_router
from routes.schedule_router import schedule_router

global_router = APIRouter(prefix="/api")

if Config.APP_TYPE == "scheduler":
    global_router.include_router(schedule_router, prefix="/schedule")
else:
    global_router.include_router(auth_router, prefix="/auth")
    global_router.include_router(guild_router, prefix="/guild")
