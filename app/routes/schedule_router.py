from fastapi import APIRouter, Depends

from models.guild import ScheduleInput
from services.guild_service import run_slot_jobs
from middlewares.scheduler_dependency import verify_scheduler_access

schedule_router = APIRouter(dependencies=[Depends(verify_scheduler_access)])


@schedule_router.post("/")
async def schedule_job(data: ScheduleInput):
    await run_slot_jobs(data.slot)
