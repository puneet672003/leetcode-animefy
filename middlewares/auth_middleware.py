from fastapi import Request
from starlette.requests import HTTPConnection
from starlette.middleware.base import BaseHTTPMiddleware

from models.auth import SessionData
from core.discord.user import DiscordUser
from managers.session_data import SessionManager
from core.logger import logger


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

        if session_data:
            self._set_auth(request, session_id, session_data)
            logger.info(f"[AUTH] Found existing session: {session_id}")

        elif header and header.startswith("Bearer "):
            token = header.split(" ")[1]
            discord_gateway = DiscordUser(token)

            user = await discord_gateway.fetch_user()
            guilds = await discord_gateway.fetch_manageable_guilds()
            if user:
                session_data = SessionData(
                    user=user,
                    guilds=guilds,
                    token={"access_token": token, "ex": 3600},
                )
                session_id = await SessionManager.create_session(session_data, ex=3600)
                self._set_auth(request, session_id, session_data)

                logger.info(f"[AUTH] Created new session: {session_id}")
            else:
                self._set_unauth(request)
                logger.warning(f"[AUTH] Invalid token: {token[:10]}...")
        else:
            self._set_unauth(request)

        response = await call_next(request)

        if (
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
