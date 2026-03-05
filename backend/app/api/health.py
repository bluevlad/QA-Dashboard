from fastapi import APIRouter

from app.core.config import get_settings
from app.core.database import get_pool
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    settings = get_settings()
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = str(e)
    return HealthResponse(status="ok", version=settings.APP_VERSION, database=db_status)


@router.get("/migration/status")
async def migration_status():
    """DB 마이그레이션 파이프라인 상태 확인.

    - 최근 ingest 요청 현황 (import_request_log)
    - 최근 run 데이터 수신 여부
    - 프로젝트별 최신 점검 시각
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        # 최근 run
        latest_run = await conn.fetchrow(
            """
            SELECT run_id, started_at, finished_at, total_projects, healthy_projects,
                   total_tests, total_passed, total_failed
            FROM qa_runs ORDER BY started_at DESC LIMIT 1
            """
        )

        # 최근 48시간 내 run 수
        recent_run_count = await conn.fetchval(
            "SELECT COUNT(*) FROM qa_runs WHERE started_at >= NOW() - INTERVAL '48 hours'"
        )

        # import_request_log 최근 통계
        import_stats = await conn.fetchrow(
            """
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'success') as success,
                COUNT(*) FILTER (WHERE status = 'failed') as failed,
                COUNT(*) FILTER (WHERE status = 'received') as pending,
                MAX(received_at) as last_received_at
            FROM import_request_log
            WHERE received_at >= NOW() - INTERVAL '7 days'
            """
        )

        # 최근 실패 로그
        recent_failures = await conn.fetch(
            """
            SELECT run_id, source, client_ip, received_at, error_message
            FROM import_request_log
            WHERE status = 'failed' AND received_at >= NOW() - INTERVAL '7 days'
            ORDER BY received_at DESC LIMIT 5
            """
        )

        # 프로젝트별 최신 점검 시각
        project_last_check = await conn.fetch(
            """
            SELECT project_name,
                   MAX(checked_at) as last_checked_at,
                   bool_or(healthy) FILTER (WHERE checked_at = sub.max_at) as last_healthy
            FROM qa_health_results h
            JOIN (
                SELECT project_name, MAX(checked_at) as max_at
                FROM qa_health_results GROUP BY project_name
            ) sub USING (project_name)
            GROUP BY project_name
            ORDER BY project_name
            """
        )

    # 마이그레이션 건강 상태 판정
    pipeline_healthy = recent_run_count > 0

    return {
        "pipeline_healthy": pipeline_healthy,
        "latest_run": dict(latest_run) if latest_run else None,
        "recent_48h_runs": recent_run_count,
        "import_stats_7d": {
            "total": import_stats["total"] if import_stats else 0,
            "success": import_stats["success"] if import_stats else 0,
            "failed": import_stats["failed"] if import_stats else 0,
            "pending": import_stats["pending"] if import_stats else 0,
            "last_received_at": import_stats["last_received_at"].isoformat() if import_stats and import_stats["last_received_at"] else None,
        },
        "recent_failures": [dict(r) for r in recent_failures],
        "projects": [
            {
                "project_name": r["project_name"],
                "last_checked_at": r["last_checked_at"].isoformat() if r["last_checked_at"] else None,
                "last_healthy": r["last_healthy"],
            }
            for r in project_last_check
        ],
    }
