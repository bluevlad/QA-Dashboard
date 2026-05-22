from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "QA-Dashboard"
    APP_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql://postgres@localhost:5432/qa_dashboard"

    # API Key for ingest authentication
    API_KEY: str = "qa-agent-secret-key"

    # 단일 프로젝트 연동 제한 — QA/To-be Agent 연동을 이 프로젝트로만 한정.
    # 빈 문자열이면 제한 없음(기존 다중 프로젝트 동작).
    TARGET_PROJECT: str = "hopenvision"

    # Log directory (mounted volume)
    LOG_DIR: str = "/app/logs"

    # Sync interval in seconds
    SYNC_INTERVAL: int = 60

    # CORS
    CORS_ORIGINS: str = "*"

    model_config = {
        "env_prefix": "QA_DASHBOARD_",
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
