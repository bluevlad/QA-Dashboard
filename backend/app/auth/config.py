from functools import lru_cache

from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    # Google OAuth (Client ID for ID token verification)
    GOOGLE_CLIENT_ID: str = ""

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480  # 8 hours

    # Allowed admin emails (comma-separated)
    ADMIN_EMAILS: str = ""

    model_config = {
        "env_prefix": "QA_AUTH_",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_auth_settings() -> AuthSettings:
    return AuthSettings()
