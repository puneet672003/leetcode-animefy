from typing import List
from pydantic import BaseModel, Field

from models.discord import UserInfo, GuildInfo


class TokenData(BaseModel):
    access_token: str
    ex: int


class SessionData(BaseModel):
    user: UserInfo
    token: TokenData
    guilds: List[GuildInfo] = Field(default_factory=list)
