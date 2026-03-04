from fastapi import APIRouter

from app.models.schemas import DashboardSummary
from app.services.project_service import get_projects
from app.services.run_service import get_runs
from app.services.trend_service import get_pass_rate_trend

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary():
    paginated = await get_runs(page=1, size=10)
    projects = await get_projects()
    trend = await get_pass_rate_trend(days=14)

    return DashboardSummary(
        total_runs=paginated.total,
        latest_run=paginated.items[0] if paginated.items else None,
        projects=projects,
        pass_rate_trend=trend,
        recent_runs=paginated.items,
    )
