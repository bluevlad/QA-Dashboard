from functools import lru_cache

from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480  # 8 hours

    # Session
    SESSION_SECRET_KEY: str = "change-me-session-secret"

    # URLs
    FRONTEND_URL: str = "http://localhost:4095"
    BACKEND_URL: str = "http://localhost:9095"

    # Allowed admin emails (comma-separated)
    ADMIN_EMAILS: str = ""

    model_config = {
        "env_prefix": "QA_AUTH_",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_auth_settings() -> AuthSettings:
    return AuthSettings()
