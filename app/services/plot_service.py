from typing import List, Dict

from core.llm import LLMClient
from models.leetcode import UserProgress
from managers.prompt_data import PromptManager


def _calculate_battle_stats(users: List[UserProgress]) -> Dict:
    scores = []
    for user in users:
        total_solved = sum(d.count for d in user.progress)
        scores.append({"user": user.username, "total": total_solved})
    
    sorted_scores = sorted(scores, key=lambda x: x["total"], reverse=True)
    winner = sorted_scores[0]["user"] if sorted_scores else "None"
    
    score_context = ""
    leaderboard_lines = []
    for i, user_score in enumerate(sorted_scores):
        user = user_score["user"]
        score = user_score["total"]
        rank_icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
        
        leaderboard_lines.append(f"{rank_icon} **{user}**: {score}")
        score_context += f"Warrior: {user} Power Level: {score}. \n"

    return {
        "winner": winner,
        "leaderboard": "\n".join(leaderboard_lines),
        "context": score_context,
        "sorted_scores": sorted_scores
    }


async def generate_battle_scene(users: List[UserProgress]) -> Dict:
    stats = _calculate_battle_stats(users)
    system_prompt = PromptManager.get_prompt("battle")
    
    plot = await LLMClient.a_generate(system_prompt, stats["context"])
    return {
        "plot": plot,
        "winner": stats["winner"],
        "leaderboard": stats["leaderboard"]
    }
