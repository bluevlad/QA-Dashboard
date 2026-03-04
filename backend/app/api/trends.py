from fastapi import APIRouter, Query

from app.models.schemas import DurationTrendPoint, TrendPoint
from app.services.trend_service import get_duration_trend, get_pass_rate_trend

router = APIRouter()


@router.get("/trends/pass-rate", response_model=list[TrendPoint])
async def pass_rate_trend(
    days: int = Query(30, ge=1, le=365),
):
    return await get_pass_rate_trend(days=days)


@router.get("/trends/duration", response_model=list[DurationTrendPoint])
async def duration_trend(
    days: int = Query(30, ge=1, le=365),
):
    return await get_duration_trend(days=days)
