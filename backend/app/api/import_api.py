import logging
import math

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request

from app.core.config import get_settings
from app.models.schemas import IngestRequest
from app.services.import_log_service import (
    get_import_logs,
    log_import_failed,
    log_import_received,
    log_import_success,
)
from app.services.import_service import delete_run, ingest_run

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Import"])


def verify_api_key(authorization: str | None = Header(None)) -> None:
    if not authorization:
        raise HTTPException(status_code=401, detail="Invalid API key")
    settings = get_settings()
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/ingest")
async def ingest(
    req: IngestRequest,
    request: Request,
    _=Depends(verify_api_key),
):
    """Ingest a single QA run from the agent."""
    client_ip = _get_client_ip(request)
    request_size = len(req.model_dump_json())

    log_id = await log_import_received(
        run_id=req.runId,
        source="http",
        client_ip=client_ip,
        request_size=request_size,
    )

    try:
        db_id = await ingest_run(req)
        await log_import_success(log_id)
        return {"status": "ok", "runId": req.runId, "dbId": db_id}
    except Exception as e:
        await log_import_failed(log_id, str(e))
        logger.error("Ingest failed for run %s: %s", req.runId, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/runs/{run_id}")
async def delete_run_endpoint(run_id: str, _=Depends(verify_api_key)):
    """Delete a run and all related data (cascade)."""
    deleted = await delete_run(run_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return {"status": "ok", "runId": run_id, "message": "Run and related data deleted"}


@router.get("/import/logs")
async def list_import_logs(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    status: str | None = Query(None, pattern="^(received|success|failed)$"),
    source: str | None = Query(None, pattern="^(http|file_sync)$"),
):
    """Retrieve import request logs for monitoring."""
    rows, total = await get_import_logs(page=page, size=size, status=status, source=source)
    return {
        "items": rows,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 0,
    }
