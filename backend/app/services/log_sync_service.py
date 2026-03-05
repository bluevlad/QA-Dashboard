import json
import logging
import os
from glob import glob

from app.core.config import get_settings
from app.core.database import get_pool
from app.models.schemas import IngestRequest
from app.services.import_log_service import (
    log_import_failed,
    log_import_received,
    log_import_success,
)
from app.services.import_service import ingest_run

logger = logging.getLogger(__name__)


async def sync_logs() -> int:
    """Scan log directory for new run-*.json files and import them into the database."""
    settings = get_settings()
    pool = await get_pool()

    log_files = sorted(glob(os.path.join(settings.LOG_DIR, "run-*.json")))
    if not log_files:
        return 0

    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT run_id FROM qa_runs")
        imported = {r["run_id"] for r in rows}

    new_count = 0
    for filepath in log_files:
        filename = os.path.basename(filepath)
        run_id = filename.replace("run-", "").replace(".json", "")
        if run_id in imported:
            continue

        try:
            await _import_log_file(filepath)
            new_count += 1
            logger.info("Imported log: %s", filename)
        except Exception as e:
            logger.error("Failed to import %s: %s", filename, e)

    return new_count


async def _import_log_file(filepath: str) -> None:
    file_size = os.path.getsize(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    request = IngestRequest(**data)

    log_id = await log_import_received(
        run_id=request.runId,
        source="file_sync",
        client_ip="localhost",
        request_size=file_size,
    )

    try:
        await ingest_run(request)
        await log_import_success(log_id)
    except Exception as e:
        await log_import_failed(log_id, str(e))
        raise
