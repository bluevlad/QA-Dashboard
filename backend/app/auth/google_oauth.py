import logging
from urllib.parse import urlencode

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.auth.config import get_auth_settings
from app.auth.jwt_handler import create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth = OAuth()


def _register_google():
    settings = get_auth_settings()
    if not settings.GOOGLE_CLIENT_ID:
        logger.warning("GOOGLE_CLIENT_ID not set - OAuth will not work")
        return
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


_register_google()


def _is_admin(email: str) -> bool:
    settings = get_auth_settings()
    if not settings.ADMIN_EMAILS:
        # If no admin emails configured, allow all authenticated users
        return True
    allowed = [e.strip().lower() for e in settings.ADMIN_EMAILS.split(",") if e.strip()]
    return email.lower() in allowed


@router.get("/google/login")
async def google_login(request: Request):
    settings = get_auth_settings()
    redirect_uri = f"{settings.BACKEND_URL}/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request):
    settings = get_auth_settings()
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        logger.error(f"OAuth error: {e}")
        params = urlencode({"error": "oauth_failed"})
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?{params}")

    user_info = token.get("userinfo")
    if not user_info:
        params = urlencode({"error": "no_user_info"})
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?{params}")

    email = user_info.get("email", "")
    name = user_info.get("name", "")

    if not _is_admin(email):
        logger.warning(f"Unauthorized login attempt: {email}")
        params = urlencode({"error": "unauthorized"})
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?{params}")

    access_token = create_access_token({"sub": email, "name": name, "email": email})

    params = urlencode({"token": access_token})
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/callback?{params}")


@router.get("/me")
async def get_me(request: Request):
    from app.auth.dependencies import require_admin

    user = await require_admin(request)
    return {"email": user["email"], "name": user.get("name", "")}
