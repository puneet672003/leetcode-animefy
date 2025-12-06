from core.config import Config


def get_full_table_name(table: str) -> str:
    return f"{Config.REPO_NAME}-db-{table}"
