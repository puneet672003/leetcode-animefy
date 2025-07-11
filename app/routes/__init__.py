from fastapi import APIRouter
from routes.guild_router import guild_router

print("testing")

global_router = APIRouter(prefix="/api")


# Add a test route
@global_router.get("/ping")
async def ping():
    return {"message": "pong"}


# Include other routers
global_router.include_router(guild_router, prefix="/guild")
