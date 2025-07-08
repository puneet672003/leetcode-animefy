from typing import Optional
from pydantic import BaseModel


class WebhookInfo(BaseModel):
    id: str
    name: str
    url: str


class ChannelInfo(BaseModel):
    id: str
    name: str


class GuildInfo(BaseModel):
    id: str
    name: str
    icon: str


class DiscordClientException(Exception):
    def __init__(self, message: str, status_code: Optional[int] = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
