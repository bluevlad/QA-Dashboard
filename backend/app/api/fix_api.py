import logging
import math

from fastapi import APIRouter, Depends, Query

from app.api.import_api import verify_api_key
from app.models.schemas import FixResultIn
from app.services.fix_service import (
    get_fix_results,
    get_lifecycle_items,
    get_lifecycle_summary,
    update_lifecycle_verification,
    upsert_fix_result,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Fix Results & Lifecycle"])


@router.post("/fix-results")
async def post_fix_result(req: FixResultIn, _=Depends(verify_api_key)):
    """Auto-Tobe-Agent가 수정 결과를 전송합니다."""
    data = req.model_dump()
    fix_id = await upsert_fix_result(data)
    return {
        "status": "ok",
        "fixId": fix_id,
        "issueNumber": req.issueNumber,
        "projectName": req.projectName,
        "lifecycleStatus": _resolve_lifecycle_status(req.status),
    }


@router.get("/fix-results")
async def list_fix_results(
    project: str | None = Query(None),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """수정 결과 목록을 조회합니다."""
    rows, total = await get_fix_results(
        project_name=project, status=status, priority=priority,
        page=page, size=size,
    )
    return {
        "items": rows,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 0,
    }


@router.get("/lifecycle/summary")
async def lifecycle_summary_endpoint():
    """전체 생명주기 요약 (점검→수정→확인 현황)을 반환합니다."""
    return await get_lifecycle_summary()


@router.get("/lifecycle")
async def list_lifecycle(
    project: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """생명주기 추적 항목을 조회합니다."""
    rows, total = await get_lifecycle_items(
        project_name=project, lifecycle_status=status,
        page=page, size=size,
    )
    return {
        "items": rows,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 0,
    }


@router.put("/lifecycle/{project}/{issue_number}/verify")
async def verify_lifecycle(
    project: str,
    issue_number: int,
    verification_run_id: str = Query(...),
    passed: bool = Query(...),
    _=Depends(verify_api_key),
):
    """QA Agent 재점검 결과로 lifecycle 상태를 업데이트합니다."""
    updated = await update_lifecycle_verification(
        project_name=project,
        issue_number=issue_number,
        verification_run_id=verification_run_id,
        passed=passed,
    )
    if not updated:
        return {"status": "not_found", "message": "No matching lifecycle entry in 'fixed' or 'verifying' state"}
    return {"status": "ok", "project": project, "issueNumber": issue_number}


def _resolve_lifecycle_status(fix_status: str) -> str:
    """FixStatus → lifecycle_status 매핑."""
    if fix_status in ("failed",):
        return "failed"
    if fix_status in ("pr_created", "test_verified", "build_verified", "fix_applied"):
        return "fixed"
    if fix_status in ("in_progress", "pending"):
        return "fixing"
    if fix_status in ("verification_requested", "verification_passed", "verification_failed"):
        return "verifying"
    if fix_status in ("merged", "deployed"):
        return "resolved"
    return "detected"
