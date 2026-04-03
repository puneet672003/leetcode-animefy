from fastapi import APIRouter, Depends

from middlewares.scheduler_dependency import resolve_slot, verify_scheduler_access
from models.guild import ScheduleInput
from services.guild_service import run_slot_jobs

schedule_router = APIRouter(dependencies=[Depends(verify_scheduler_access)])


@schedule_router.post("/")
async def schedule_job(data: ScheduleInput = Depends(resolve_slot)):
    await run_slot_jobs(data.slot)
    return data.model_dump()
