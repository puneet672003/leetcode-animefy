from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    username: str
    avatar: Optional[str] = None


class TokenData(BaseModel):
    access_token: str
    ex: int


class SessionData(BaseModel):
    user: User
    token: TokenData
