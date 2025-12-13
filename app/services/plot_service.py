from typing import List, Dict

from core.llm import LLMClient
from models.leetcode import UserProgress
from managers.prompt_data import PromptManager


def _calculate_battle_stats(users: List[UserProgress], improvement_map: Dict[str, int] = None) -> Dict:
    scores = []
    for user in users:
        total_solved = sum(d.count for d in user.progress)
        improvement = 0
        if improvement_map and user.username in improvement_map:
            improvement = improvement_map[user.username]
            
        scores.append({"user": user.username, "total": total_solved, "improvement": improvement})
    
    sorted_scores = sorted(scores, key=lambda x: (x["improvement"], x["total"]), reverse=True)
    winner = sorted_scores[0]["user"] if sorted_scores else "None"
    
    score_context = ""
    leaderboard_lines = []
    
    for i, user_score in enumerate(sorted_scores):
        user = user_score["user"]
        total = user_score["total"]
        imp = user_score["improvement"]
        
        improvement_str = f" (+{imp})" if imp > 0 else " (+0)"
        
        rank_icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
        
        leaderboard_lines.append(f"{rank_icon} **{user}**: {improvement_str}")
        score_context += f"Warrior: {user} Power Level: {imp}. \n"

    return {
        "winner": winner,
        "leaderboard": "\n".join(leaderboard_lines),
        "context": score_context,
        "sorted_scores": sorted_scores,
    }


async def generate_scene(users: List[UserProgress], improvement_map: Dict[str, int] = None, prompt_name: str = "intro") -> Dict:
    stats = _calculate_battle_stats(users, improvement_map)
    
    system_prompt = PromptManager.get_prompt(prompt_name)
    if prompt_name == "intro":
        names = [u.username for u in users]
        context = ", ".join(names)
    else:
        context = stats["context"]

    plot = await LLMClient.a_generate(system_prompt, context)
    return {
        "plot": plot,
        "winner": stats["winner"] if prompt_name == "battle" else "None",
        "leaderboard": stats["leaderboard"] if prompt_name == "battle" else "None"
    }
