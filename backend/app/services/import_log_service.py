import logging
from datetime import datetime, timezone

from app.core.database import get_pool

logger = logging.getLogger(__name__)


async def log_import_received(
    run_id: str,
    source: str,
    client_ip: str | None = None,
    request_size: int = 0,
) -> int:
    """Record that an import request was received. Returns the log id."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            """
            INSERT INTO import_request_log
                (run_id, source, client_ip, status, request_size)
            VALUES ($1, $2, $3, 'received', $4)
            RETURNING id
            """,
            run_id,
            source,
            client_ip,
            request_size,
        )


async def log_import_success(log_id: int) -> None:
    """Mark an import request as successfully completed."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE import_request_log
            SET status = 'success', completed_at = $1
            WHERE id = $2
            """,
            datetime.now(timezone.utc),
            log_id,
        )


async def log_import_failed(log_id: int, error_message: str) -> None:
    """Mark an import request as failed."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE import_request_log
            SET status = 'failed', error_message = $1, completed_at = $2
            WHERE id = $3
            """,
            error_message,
            datetime.now(timezone.utc),
            log_id,
        )


async def get_import_logs(
    page: int = 1,
    size: int = 50,
    status: str | None = None,
    source: str | None = None,
) -> tuple[list[dict], int]:
    """Retrieve import request logs with pagination and optional filters."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        conditions = []
        params = []
        idx = 1

        if status:
            conditions.append(f"status = ${idx}")
            params.append(status)
            idx += 1

        if source:
            conditions.append(f"source = ${idx}")
            params.append(source)
            idx += 1

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        total = await conn.fetchval(
            f"SELECT count(*) FROM import_request_log {where}",
            *params,
        )

        offset = (page - 1) * size
        params_with_paging = [*params, size, offset]
        rows = await conn.fetch(
            f"""
            SELECT id, run_id, source, client_ip, received_at, status,
                   error_message, request_size, completed_at
            FROM import_request_log
            {where}
            ORDER BY received_at DESC
            LIMIT ${idx} OFFSET ${idx + 1}
            """,
            *params_with_paging,
        )

        return [dict(r) for r in rows], total
