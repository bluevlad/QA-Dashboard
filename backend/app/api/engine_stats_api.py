"""
Engine Stats API - Dual-Engine 비교 통계 엔드포인트

Claude Code CLI와 Local LLM 엔진의 수정 성과를 비교하는 API를 제공합니다.
"""

import logging

from fastapi import APIRouter, Query

from app.services.engine_stats_service import (
    get_engine_comparison_stats,
    get_engine_daily_trend,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Engine Stats"])


@router.get("/engine-stats")
async def engine_stats(days: int = Query(30, ge=1, le=365)):
    """엔진별 수정 성과 비교 통계를 반환합니다."""
    return await get_engine_comparison_stats(days)


@router.get("/engine-stats/trend")
async def engine_trend(days: int = Query(30, ge=1, le=365)):
    """엔진별 일별 트렌드 데이터를 반환합니다."""
    return await get_engine_daily_trend(days)
