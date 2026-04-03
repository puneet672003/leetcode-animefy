from typing import Literal

from pydantic import BaseModel


class DifficultyCount(BaseModel):
    count: int
    difficulty: Literal["EASY", "MEDIUM", "HARD"]


class UserProgress(BaseModel):
    username: str
    progress: list[DifficultyCount]
