from pydantic import BaseModel, Field

from models.discord import GuildInfo, UserInfo


class TokenData(BaseModel):
    access_token: str
    ex: int


class SessionData(BaseModel):
    user: UserInfo
    token: TokenData
    guilds: list[GuildInfo] = Field(default_factory=list)
