import logging

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.auth.config import get_auth_settings
from app.auth.jwt_handler import create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class GoogleTokenRequest(BaseModel):
    credential: str


def _is_admin(email: str) -> bool:
    settings = get_auth_settings()
    if not settings.ADMIN_EMAILS:
        return True
    allowed = [e.strip().lower() for e in settings.ADMIN_EMAILS.split(",") if e.strip()]
    return email.lower() in allowed


def _verify_google_id_token(credential: str) -> dict:
    """Verify Google ID token and return user info."""
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token

    settings = get_auth_settings()
    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        if idinfo["iss"] not in ("accounts.google.com", "https://accounts.google.com"):
            raise ValueError("Invalid issuer")
        return idinfo
    except ValueError as e:
        logger.error(f"Google ID token verification failed: {e}")
        raise


@router.post("/google/verify")
async def google_verify(body: GoogleTokenRequest):
    """Verify Google ID token from frontend and return JWT."""
    try:
        idinfo = _verify_google_id_token(body.credential)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google credential",
        )

    email = idinfo.get("email", "")
    name = idinfo.get("name", "")

    if not _is_admin(email):
        logger.warning(f"Unauthorized login attempt: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 없는 계정입니다.",
        )

    access_token = create_access_token({"sub": email, "name": name, "email": email})
    return {"token": access_token, "email": email, "name": name}


@router.get("/me")
async def get_me(request: Request):
    from app.auth.dependencies import require_admin

    user = await require_admin(request)
    return {"email": user["email"], "name": user.get("name", "")}
