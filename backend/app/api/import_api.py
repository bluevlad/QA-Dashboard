import logging

import asyncpg
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    BulkImportRequest,
    BulkImportResult,
    DeleteResult,
    ImportResult,
    RunImportRequest,
)
from app.services.import_service import delete_run, import_run

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Import"])


@router.post("/import/run", response_model=ImportResult, status_code=201)
async def import_single_run(body: RunImportRequest):
    """Import a single run into the database."""
    try:
        await import_run(body)
        return ImportResult(
            success=True,
            runId=body.runId,
            message="Run imported successfully",
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(
            status_code=409,
            detail=f"Run '{body.runId}' already exists",
        )


@router.post("/import/bulk", response_model=BulkImportResult)
async def import_bulk_runs(body: BulkImportRequest):
    """Import multiple runs. Partial success is allowed."""
    results: list[ImportResult] = []
    succeeded = 0
    failed = 0

    for run in body.runs:
        try:
            await import_run(run)
            results.append(
                ImportResult(
                    success=True,
                    runId=run.runId,
                    message="Imported successfully",
                )
            )
            succeeded += 1
        except asyncpg.UniqueViolationError:
            results.append(
                ImportResult(
                    success=False,
                    runId=run.runId,
                    message=f"Duplicate run_id '{run.runId}'",
                )
            )
            failed += 1
        except Exception as e:
            logger.error("Bulk import failed for run %s: %s", run.runId, e)
            results.append(
                ImportResult(
                    success=False,
                    runId=run.runId,
                    message=str(e),
                )
            )
            failed += 1

    return BulkImportResult(
        total=len(body.runs),
        succeeded=succeeded,
        failed=failed,
        results=results,
    )


@router.delete("/runs/{run_id}", response_model=DeleteResult)
async def delete_run_endpoint(run_id: str):
    """Delete a run and all related data (cascade)."""
    deleted = await delete_run(run_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return DeleteResult(
        success=True,
        runId=run_id,
        message="Run and related data deleted successfully",
    )
