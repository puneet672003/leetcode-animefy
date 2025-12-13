from typing import List, Dict

from core.llm import LLMClient
from models.leetcode import UserProgress
from managers.prompt_data import PromptManager


def _generate_score_string(users: List[UserProgress]) -> str:
    scores = []
    for user in users:
        total_solved = sum(d.count for d in user.progress)
        scores.append({"user": user.username, "total": total_solved})
    
    sorted_scores = sorted(scores, key=lambda x: x["total"], reverse=True)

    score_string = ""
    for user_score in sorted_scores:
        user = user_score["user"]
        score = user_score["total"]
        score_string += f"Warrior: {user} Power Level: {score}. \n"

    return score_string


async def generate_battle_scene(users: List[UserProgress]) -> str:
    score_string = _generate_score_string(users)
    system_prompt = PromptManager.get_prompt("battle")
    
    return await LLMClient.a_generate(system_prompt, score_string)
