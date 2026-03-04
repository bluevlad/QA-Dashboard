from app.core.database import get_pool
from app.models.schemas import DurationTrendPoint, TrendPoint


async def get_pass_rate_trend(days: int = 30) -> list[TrendPoint]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                DATE_TRUNC('day', sr.started_at)::date::text AS date,
                CASE WHEN SUM(total_tests) > 0
                     THEN ROUND(SUM(total_passed)::numeric / SUM(total_tests) * 100, 1)
                     ELSE 0 END AS pass_rate,
                SUM(total_tests)::int AS total_tests,
                SUM(total_passed)::int AS total_passed,
                SUM(total_failed)::int AS total_failed
            FROM scheduler_runs sr
            WHERE sr.started_at >= NOW() - ($1 || ' days')::interval
            GROUP BY DATE_TRUNC('day', sr.started_at)
            ORDER BY date
            """,
            str(days),
        )
    return [TrendPoint(**dict(r)) for r in rows]


async def get_duration_trend(days: int = 30) -> list[DurationTrendPoint]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                DATE_TRUNC('day', sr.started_at)::date::text AS date,
                ROUND(AVG(sr.duration_ms)::numeric, 0)::float AS avg_duration_ms,
                MIN(sr.duration_ms)::float AS min_duration_ms,
                MAX(sr.duration_ms)::float AS max_duration_ms
            FROM scheduler_runs sr
            WHERE sr.started_at >= NOW() - ($1 || ' days')::interval
            GROUP BY DATE_TRUNC('day', sr.started_at)
            ORDER BY date
            """,
            str(days),
        )
    return [DurationTrendPoint(**dict(r)) for r in rows]
