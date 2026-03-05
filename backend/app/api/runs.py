from fastapi import APIRouter, HTTPException, Query

from app.services.run_service import get_run_detail, get_runs

router = APIRouter()


@router.get("/runs")
async def list_runs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    date_from: str | None = None,
    date_to: str | None = None,
):
    paginated = await get_runs(page=page, size=limit, date_from=date_from, date_to=date_to)
    return {
        "total": paginated.total,
        "page": paginated.page,
        "limit": limit,
        "runs": [item.model_dump() for item in paginated.items],
    }


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    detail = await get_run_detail(run_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Run not found")
    return detail
