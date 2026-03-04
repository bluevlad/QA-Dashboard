from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import PaginatedRuns, RunDetail
from app.services.run_service import get_run_detail, get_runs

router = APIRouter()


@router.get("/runs", response_model=PaginatedRuns)
async def list_runs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    return await get_runs(page=page, size=size)


@router.get("/runs/{run_id}", response_model=RunDetail)
async def get_run(run_id: str):
    detail = await get_run_detail(run_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Run not found")
    return detail
