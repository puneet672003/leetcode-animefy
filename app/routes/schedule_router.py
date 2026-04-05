from fastapi import APIRouter, BackgroundTasks, Depends

from middlewares.scheduler_dependency import resolve_slot, verify_scheduler_access
from models.guild import ScheduleInput
from services.guild_service import run_slot_jobs

schedule_router = APIRouter(dependencies=[Depends(verify_scheduler_access)])


@schedule_router.post("/")
async def schedule_job(
    background_tasks: BackgroundTasks, data: ScheduleInput = Depends(resolve_slot)
):
    background_tasks.add_task(run_slot_jobs, data.slot)
    return data.model_dump()
