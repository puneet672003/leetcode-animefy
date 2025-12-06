from fastapi import HTTPException, Request
from models.guild import ParsedSlot
from utils.validators import validate_slot_str


async def verify_scheduler_access(request: Request) -> None:
    is_scheduler_authenticated = getattr(
        request.state, "is_scheduler_authenticated", False
    )

    if not is_scheduler_authenticated:
        raise HTTPException(status_code=401, detail="Authentication required")
