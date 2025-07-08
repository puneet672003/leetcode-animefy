import os


def _get_env(key, required: bool = False):
    val = os.environ.get(key)
    if val is None and required:
        raise ValueError(f"{key} is missing.")

    return val


class Config:
    BOT_TOKEN = _get_env("BOT_TOKEN", required=True)
    DATABASE_URL = _get_env("DATABASE_URL", required=True)
    DATABASE_NAME = _get_env("DATABASE_NAME", required=True)
    SERVER_HOST = _get_env("UVICORN_HOST", required=True)
    SERVER_PORT = int(_get_env("UVICORN_PORT", required=True))
    CACHE_DB_HOST = _get_env("CACHE_DB_HOST", required=True)
    CACHE_DB_PORT = int(_get_env("CACHE_DB_PORT", required=True))
    CACHE_DB_PASSWORD = _get_env("CACHE_DB_PASSWORD", required=True)
