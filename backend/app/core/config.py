from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "QA-Dashboard"
    APP_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql://postgres@localhost:5432/qa_dashboard"

    # API Key for ingest authentication
    API_KEY: str = "qa-agent-secret-key"

    # 프로젝트 스코프 — 값이 있으면 그 프로젝트만 허용, 빈 문자열이면 전체 허용(멀티프로젝트).
    # SkillRadar 중심 다중 서비스 fix 중앙 수집을 위해 기본 멀티프로젝트. hopenvision 은 레거시.
    # (단일 프로젝트 대시보드로 쓰려면 env QA_DASHBOARD_TARGET_PROJECT 로 지정)
    TARGET_PROJECT: str = ""

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
