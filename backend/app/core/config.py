from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "QA-Dashboard"
    APP_VERSION: str = "1.0.0"

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "qa_dashboard"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""

    # Log directory (mounted volume)
    LOG_DIR: str = "/app/logs"

    # Sync interval in seconds
    SYNC_INTERVAL: int = 60

    # CORS
    CORS_ORIGINS: str = "*"

    model_config = {
        "env_file": ".env",
        "env_prefix": "QD_",
        "extra": "ignore",
    }

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
