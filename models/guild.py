from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


class GuildData(BaseModel):
    # id: ObjectId = Field(alias="_id")
    guild_id: str
    channel_id: Optional[str] = None
    webhook_id: Optional[str] = None
    leetcode_users: List[str] = Field(default_factory=list)

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True


class CreateGuildImput(BaseModel):
    guild_id: str

    @field_validator("guild_id")
    def number_string(cls, v: str):
        if not v.isdigit():
            raise ValueError("guild_id must be a number string")
        return v


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
