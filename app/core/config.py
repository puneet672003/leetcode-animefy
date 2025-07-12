import os


def _get_env(key, required: bool = False, default=None):
    val = os.environ.get(key, default)
    if val is None and required:
        raise ValueError(f"{key} is missing.")

    return val


class Config:
    # app
    APP_TYPE = _get_env("APP_TYPE", default="default")
    # bot
    BOT_TOKEN = _get_env("BOT_TOKEN", required=True)
    # aws
    AWS_DEFAULT_REGION = _get_env("AWS_DEFAULT_REGION", required=True)
    AWS_ACCESS_KEY_ID = _get_env("AWS_ACCESS_KEY_ID", required=True)
    AWS_SECRET_ACCESS_KEY = _get_env("AWS_SECRET_ACCESS_KEY", required=True)
    # cache
    CACHE_TOKEN = _get_env("CACHE_TOKEN", required=True)
    CACHE_ENDPOINT = _get_env("CACHE_ENDPOINT", required=True)
    # development
    SERVER_HOST = _get_env("UVICORN_HOST", default="localhost")
    SERVER_PORT = int(_get_env("UVICORN_PORT", default="8000"))
    DEVELOPMENT = _get_env("DEVELOPMENT", default="false").lower() == "true"
