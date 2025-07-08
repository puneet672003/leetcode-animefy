import secrets
from typing import Optional

from core.cache import CacheStore
from models.auth import SessionData


class SessionManager:
    @staticmethod
    def _generate_session_id() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    async def create_session(
        session_data: SessionData, ex: int = 3600
    ) -> Optional[str]:
        session_id = SessionManager._generate_session_id()
        session_json = session_data.model_dump_json()

        res = await CacheStore.set_cache(session_id, session_json, ex)
        return session_id if res else None

    @staticmethod
    async def set_session(
        session_id: str, session_data: SessionData, ex: int = None
    ) -> bool:
        session_json = session_data.model_dump_json()
        return await CacheStore.set_cache(session_id, session_json, ex)

    @staticmethod
    async def get_session(session_id: str) -> Optional[SessionData]:
        session_json = await CacheStore.get_cache(session_id)
        return SessionData.model_validate_json(session_json) if session_json else None

    @staticmethod
    async def delete_session(session_id: str) -> bool:
        return await CacheStore.delete_cache(session_id)

    @staticmethod
    async def session_exists(session_id: str) -> bool:
        return await CacheStore.exists(session_id)
