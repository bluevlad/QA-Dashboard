from fastapi import APIRouter, Query

from app.services.project_service import get_project_history, get_projects

router = APIRouter()


@router.get("/projects")
async def list_projects():
    projects = await get_projects()
    return {"projects": [p.model_dump() for p in projects]}


@router.get("/projects/{name}/timeline")
async def project_timeline(
    name: str,
    days: int = Query(30, ge=1, le=90),
):
    timeline = await get_project_history(name, days=days)
    return {
        "projectName": name,
        "days": days,
        "timeline": [t.model_dump() for t in timeline],
    }


@router.get("/timeline")
async def global_timeline(
    days: int = Query(7, ge=1, le=90),
):
    """Global timeline across all projects for migration verification."""
    from app.core.database import get_pool

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                DATE(r.started_at AT TIME ZONE 'Asia/Seoul') as date,
                r.run_id,
                r.total_projects,
                r.healthy_projects,
                r.total_tests,
                r.total_passed,
                r.total_failed
            FROM qa_runs r
            WHERE r.started_at >= NOW() - ($1 || ' days')::interval
            ORDER BY r.started_at DESC
            """,
            str(days),
        )
    return [
        {
            "date": str(r["date"]),
            "run_id": r["run_id"],
            "total_projects": r["total_projects"],
            "healthy_projects": r["healthy_projects"],
            "total_tests": r["total_tests"],
            "total_passed": r["total_passed"],
            "total_failed": r["total_failed"],
        }
        for r in rows
    ]
