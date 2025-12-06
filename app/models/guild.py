from fastapi import HTTPException
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from utils.validators import validate_slot_str


class GuildData(BaseModel):
    guild_id: str
    slot: Optional[str] = None
    channel_id: Optional[str] = None
    webhook_id: Optional[str] = None
    leetcode_users: List[str] = Field(default_factory=list)

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True


class ParsedSlot(BaseModel):
    hh: int
    mm: int


class UpdateGuildInput(BaseModel):
    channel_id: str

    @field_validator("channel_id")
    def number_string(cls, v: str):
        if not v.isdigit():
            raise ValueError("channel_id must be a number string")
        return v


class UpdateGuildUserInput(BaseModel):
    user_id: str
    action: Literal["add", "remove"]


class ScheduleInput(BaseModel):
    slot: ParsedSlot

    @field_validator("slot", mode="before")
    def enforce_and_convert_slot(cls, v: str):
        if not isinstance(v, str):
            raise HTTPException(status_code=422, detail="slot must be a string")

        try:
            hh, mm = validate_slot_str(v)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        return {"hh": hh, "mm": mm}
