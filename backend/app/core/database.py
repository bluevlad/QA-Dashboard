import logging

import asyncpg

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool not initialized")
    return _pool


async def init_db() -> None:
    global _pool
    settings = get_settings()

    _pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=10,
    )
    logger.info("Database pool initialized: %s", settings.DATABASE_URL.split("@")[-1])

    from app.models.database_models import TABLES_DDL

    async with _pool.acquire() as conn:
        for ddl in TABLES_DDL:
            try:
                await conn.execute(ddl)
            except asyncpg.exceptions.InsufficientPrivilegeError:
                pass
    logger.info("Database tables ensured")


async def close_db() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed")
