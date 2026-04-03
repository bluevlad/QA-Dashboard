"""
Engine Stats Service - Dual-Engine 비교 통계

Claude Code CLI와 Local LLM 엔진의 수정 성과를 비교 분석합니다.
"""

import logging
from datetime import datetime, timedelta, timezone

from app.core.database import get_pool

logger = logging.getLogger(__name__)


async def get_engine_comparison_stats(days: int = 30) -> dict:
    """엔진별 수정 성과 비교 통계를 반환합니다."""
    pool = await get_pool()
    since = datetime.now(timezone.utc) - timedelta(days=days)

    async with pool.acquire() as conn:
        # 엔진별 집계
        engine_rows = await conn.fetch(
            """
            SELECT
                COALESCE(engine_type, strategy) AS engine,
                COALESCE(engine_model, strategy) AS model,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status IN ('pr_created', 'merged', 'deployed', 'verification_passed', 'build_verified', 'test_verified')) AS succeeded,
                COUNT(*) FILTER (WHERE status = 'failed') AS failed,
                COUNT(*) FILTER (WHERE status = 'skipped') AS skipped,
                ROUND(AVG(duration_ms)) AS avg_duration_ms,
                ROUND(AVG(engine_inference_ms)) AS avg_inference_ms,
                COUNT(*) FILTER (WHERE engine_metadata->>'fallbackUsed' = 'true') AS fallback_count
            FROM qa_fix_results
            WHERE created_at >= $1
            GROUP BY COALESCE(engine_type, strategy), COALESCE(engine_model, strategy)
            ORDER BY total DESC
            """,
            since,
        )

        engines = []
        for row in engine_rows:
            total = row["total"]
            succeeded = row["succeeded"]
            engines.append({
                "engine_type": row["engine"],
                "model_name": row["model"],
                "total_fixes": total,
                "success_count": succeeded,
                "failure_count": row["failed"],
                "skipped_count": row["skipped"],
                "success_rate": round(succeeded / total * 100, 1) if total > 0 else 0,
                "avg_duration_ms": row["avg_duration_ms"],
                "avg_inference_ms": row["avg_inference_ms"],
                "fallback_count": row["fallback_count"],
            })

        # 엔진별 프로젝트 분포
        project_rows = await conn.fetch(
            """
            SELECT
                COALESCE(engine_type, strategy) AS engine,
                project_name,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status IN ('pr_created', 'merged', 'deployed', 'verification_passed', 'build_verified', 'test_verified')) AS succeeded,
                COUNT(*) FILTER (WHERE status = 'failed') AS failed,
                ROUND(AVG(duration_ms)) AS avg_duration_ms
            FROM qa_fix_results
            WHERE created_at >= $1
            GROUP BY COALESCE(engine_type, strategy), project_name
            ORDER BY engine, project_name
            """,
            since,
        )

        by_project: dict[str, list[dict]] = {}
        for row in project_rows:
            engine = row["engine"]
            if engine not in by_project:
                by_project[engine] = []
            total = row["total"]
            succeeded = row["succeeded"]
            by_project[engine].append({
                "project_name": row["project_name"],
                "total": total,
                "succeeded": succeeded,
                "failed": row["failed"],
                "success_rate": round(succeeded / total * 100, 1) if total > 0 else 0,
                "avg_duration_ms": row["avg_duration_ms"],
            })

    return {
        "period_days": days,
        "engines": engines,
        "by_project": by_project,
    }


async def get_engine_daily_trend(days: int = 30) -> list[dict]:
    """엔진별 일별 트렌드 데이터를 반환합니다."""
    pool = await get_pool()
    since = datetime.now(timezone.utc) - timedelta(days=days)

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                DATE(created_at AT TIME ZONE 'UTC') AS date,
                COALESCE(engine_type, strategy) AS engine,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status IN ('pr_created', 'merged', 'deployed', 'verification_passed', 'build_verified', 'test_verified')) AS succeeded,
                COUNT(*) FILTER (WHERE status = 'failed') AS failed,
                ROUND(AVG(duration_ms)) AS avg_duration_ms,
                ROUND(AVG(engine_inference_ms)) AS avg_inference_ms
            FROM qa_fix_results
            WHERE created_at >= $1
            GROUP BY DATE(created_at AT TIME ZONE 'UTC'), COALESCE(engine_type, strategy)
            ORDER BY date, engine
            """,
            since,
        )

    return [
        {
            "date": str(row["date"]),
            "engine_type": row["engine"],
            "total": row["total"],
            "succeeded": row["succeeded"],
            "failed": row["failed"],
            "avg_duration_ms": row["avg_duration_ms"],
            "avg_inference_ms": row["avg_inference_ms"],
        }
        for row in rows
    ]
