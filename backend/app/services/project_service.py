from app.core.database import get_pool
from app.models.schemas import ProjectHistoryItem, ProjectStatus


async def get_projects() -> list[ProjectStatus]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            WITH latest AS (
                SELECT DISTINCT ON (project_name)
                    project_name, healthy, checked_at
                FROM qa_health_results
                ORDER BY project_name, checked_at DESC
            ),
            stats AS (
                SELECT
                    project_name,
                    COUNT(*) as total_runs,
                    AVG(CASE WHEN total > 0 THEN passed::float / total * 100 END) as avg_pass_rate,
                    SUM(CASE WHEN failed > 0 THEN 1 ELSE 0 END) as recent_failures
                FROM qa_test_results
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY project_name
            )
            SELECT
                COALESCE(l.project_name, s.project_name) as project_name,
                l.checked_at as last_checked_at,
                l.healthy as last_healthy,
                COALESCE(s.total_runs, 0) as total_runs,
                s.avg_pass_rate,
                COALESCE(s.recent_failures, 0) as recent_failures
            FROM latest l
            FULL OUTER JOIN stats s ON l.project_name = s.project_name
            ORDER BY project_name
            """
        )
    return [ProjectStatus(**dict(r)) for r in rows]


async def get_project_history(name: str, days: int = 30) -> list[ProjectHistoryItem]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                DATE(r.started_at AT TIME ZONE 'Asia/Seoul') as date,
                h.healthy,
                t.passed, t.failed, t.total,
                AVG((e->>'responseTimeMs')::float) as response_time_ms
            FROM qa_runs r
            JOIN qa_health_results h ON h.run_id = r.id AND h.project_name = $1
            LEFT JOIN qa_test_results t ON t.run_id = r.id AND t.project_name = $1
            LEFT JOIN LATERAL jsonb_array_elements(h.endpoints) e ON TRUE
            WHERE r.started_at >= NOW() - ($2 || ' days')::interval
            GROUP BY DATE(r.started_at AT TIME ZONE 'Asia/Seoul'), h.healthy, t.passed, t.failed, t.total
            ORDER BY date DESC
            """,
            name,
            str(days),
        )
    return [
        ProjectHistoryItem(
            date=str(r["date"]),
            healthy=r["healthy"],
            passed=r["passed"] or 0,
            failed=r["failed"] or 0,
            total=r["total"] or 0,
            responseTimeMs=round(r["response_time_ms"], 1) if r["response_time_ms"] else None,
        )
        for r in rows
    ]
