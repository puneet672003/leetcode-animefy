from datetime import datetime

from fastapi import Body, HTTPException, Request

from models.guild import ScheduleInput


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
        rounded_minute = (now.minute // 15) * 15
        slot_str = f"{now.hour:02d}:{rounded_minute:02d}"
    else:
        slot_str = body["slot"]

    return ScheduleInput(slot=slot_str)
