from app.core.database import get_pool
from app.models.schemas import ProjectHistoryItem, ProjectStatus


async def get_projects() -> list[ProjectStatus]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT DISTINCT ON (tr.project_name)
                tr.project_name,
                sr.run_id AS last_run_id,
                sr.started_at AS last_run_at,
                COALESCE(hc.healthy, false) AS healthy,
                tr.passed AS last_passed,
                tr.failed AS last_failed,
                tr.total AS last_total,
                tr.duration_ms AS last_duration_ms
            FROM test_run_results tr
            JOIN scheduler_runs sr ON sr.id = tr.run_id
            LEFT JOIN health_check_results hc
                ON hc.run_id = tr.run_id AND hc.project_name = tr.project_name
            ORDER BY tr.project_name, sr.started_at DESC
            """
        )
    return [ProjectStatus(**dict(r)) for r in rows]


async def get_project_history(name: str, limit: int = 30) -> list[ProjectHistoryItem]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                sr.run_id,
                sr.started_at,
                COALESCE(hc.healthy, false) AS healthy,
                tr.passed,
                tr.failed,
                tr.total,
                tr.duration_ms
            FROM test_run_results tr
            JOIN scheduler_runs sr ON sr.id = tr.run_id
            LEFT JOIN health_check_results hc
                ON hc.run_id = tr.run_id AND hc.project_name = tr.project_name
            WHERE tr.project_name = $1
            ORDER BY sr.started_at DESC
            LIMIT $2
            """,
            name,
            limit,
        )
    return [ProjectHistoryItem(**dict(r)) for r in rows]
