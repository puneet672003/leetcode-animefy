from fastapi import APIRouter, Depends, Body

from models.guild import ScheduleInput
from services.guild_service import run_slot_jobs
from middlewares.scheduler_dependency import verify_scheduler_access, resolve_slot

schedule_router = APIRouter(dependencies=[Depends(verify_scheduler_access)])


@schedule_router.post("/")
async def schedule_job(data: ScheduleInput = Depends(resolve_slot)):
    await run_slot_jobs(data.slot)
    return data.model_dump()
