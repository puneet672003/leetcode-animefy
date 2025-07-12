from fastapi import APIRouter

schedule_router = APIRouter()


@schedule_router.post("/")
async def schedule_job():
    return {"detail": "under development"}
