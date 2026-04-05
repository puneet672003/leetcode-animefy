import secrets

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import HTTPConnection

from core.config import Config
from core.discord.user import DiscordUser
from core.logger import Logger
from managers.session_data import SessionManager
from models.auth import SessionData


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name="Authorization", cookie_name="session_id"):
        super().__init__(app)
        self.header_name = header_name
        self.cookie_name = cookie_name

    async def dispatch(self, request: Request, call_next):
        header = request.headers.get(self.header_name)
        session_id = request.cookies.get(self.cookie_name)
        session_data = (
            await SessionManager.get_session(session_id) if session_id else None
        )

        should_clear_cookie = False

        if session_data:
            self._set_auth(request, session_id, session_data)
            Logger.info(f"[AUTH] Found existing session: {session_id}")

        elif header and header.startswith("Bearer "):
            token = header.split(" ", 1)[1]
            try:
                async with DiscordUser(token) as discord_gateway:
                    user = await discord_gateway.fetch_user()
                    guilds = await discord_gateway.fetch_manageable_guilds()
            except Exception as e:
                Logger.error(f"[AUTH] Discord error: {e}")
                user = None
                guilds = []

            if user:
                session_data = SessionData(
                    user=user,
                    guilds=guilds,
                    token={"access_token": token, "ex": 3600},
                )
                session_id = await SessionManager.create_session(session_data, ex=3600)
                self._set_auth(request, session_id, session_data)
                Logger.info(f"[AUTH] Created new session: {session_id}")
            else:
                if session_id:
                    await SessionManager.delete_session(session_id)
                    should_clear_cookie = True
                self._set_unauth(request)
                Logger.warning(f"[AUTH] Invalid token: {token[:10]}...")
        else:
            self._set_unauth(request)

        response = await call_next(request)

        if should_clear_cookie:
            response.delete_cookie(
                key=self.cookie_name, httponly=True, secure=True, samesite="lax"
            )
        elif (
            session_id
            and not request.cookies.get(self.cookie_name)
            and getattr(request.state, "is_authenticated", False)
        ):
            response.set_cookie(
                key=self.cookie_name,
                value=session_id,
                max_age=3600,
                httponly=True,
                secure=True,
                samesite="lax",
            )
        return response

    def _set_auth(self, request: HTTPConnection, session_id: str, data: SessionData):
        request.state.session_id = session_id
        request.state.session_data = data

        request.state.is_authenticated = True

    def _set_unauth(self, request: HTTPConnection):
        request.state.session_id = None
        request.state.session_data = None

        request.state.is_authenticated = False


class SchedulerAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name="Authorization"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next):
        header = request.headers.get(self.header_name)
        request.state.is_scheduler_authenticated = False

        if header and header.startswith("Bearer "):
            token = header.split(" ", 1)[1]
            if secrets.compare_digest(token, Config.SCHEDULER_SECRET):
                request.state.is_scheduler_authenticated = True
                Logger.info("[SCHEDULER AUTH] Authentication successfull")
            else:
                Logger.warning("[SCHEDULER AUTH] Incorrect token")
        else:
            Logger.warning("[SCHEDULER AUTH] Invalid token")

        return await call_next(request)
