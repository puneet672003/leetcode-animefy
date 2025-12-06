from datetime import datetime
from fastapi import HTTPException, Request, Body
from models.guild import ParsedSlot, ScheduleInput


async def verify_scheduler_access(request: Request) -> None:
    is_scheduler_authenticated = getattr(
        request.state, "is_scheduler_authenticated", False
    )

    if not is_scheduler_authenticated:
        raise HTTPException(status_code=401, detail="Authentication required")


async def resolve_slot(body: dict | None = Body(default=None)):
    slot_str = None
    if not body or "slot" not in body:
        now = datetime.now()
        slot_str = (
            f"{now.hour if now.hour > 0 else '00'}:{'00' if now.minute < 30 else '30'}"
        )
    else:
        slot_str = body["slot"]

    return ScheduleInput(slot=slot_str)
