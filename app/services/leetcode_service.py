from fastapi import HTTPException

from core.leetcode import LeetCodeClient, LeetCodeClientException
from models.leetcode import UserProgress, DifficultyCount

async def get_user_progress(username: str) -> UserProgress:
    try:
        data = await LeetCodeClient.get_question_progress(username)
        user = UserProgress(username=username, progress=[DifficultyCount(**item) for item in data])
        return user
    except LeetCodeClientException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
