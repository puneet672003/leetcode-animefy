from fastapi import APIRouter, Request, Response

from managers.session_data import SessionManager

auth_router = APIRouter()


@auth_router.post("/signout")
async def signout(request: Request, response: Response):
    session_id = getattr(request.state, "session_id", None)
    if session_id:
        await SessionManager.delete_session(session_id)
    response.delete_cookie(key="session_id", httponly=True, secure=True, samesite="lax")
    return {"detail": "Signed out"}
