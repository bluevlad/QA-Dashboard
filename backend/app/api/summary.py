from fastapi import APIRouter

from app.services.project_service import get_projects
from app.services.run_service import get_runs
from app.services.trend_service import get_pass_rate_trend
from app.services.fix_service import get_lifecycle_summary

router = APIRouter()


@router.get("/summary")
async def dashboard_summary():
    paginated = await get_runs(page=1, size=10)
    projects = await get_projects()
    trend = await get_pass_rate_trend(days=14)
    lifecycle = await get_lifecycle_summary()

    return {
        "total_runs": paginated.total,
        "latest_run": paginated.items[0].model_dump() if paginated.items else None,
        "projects": [p.model_dump() for p in projects],
        "pass_rate_trend": [t.model_dump() for t in trend],
        "recent_runs": [r.model_dump() for r in paginated.items],
        "lifecycle_summary": lifecycle,
    }
