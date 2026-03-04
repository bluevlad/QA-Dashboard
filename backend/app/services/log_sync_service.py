import json
import logging
import os
from glob import glob

from app.core.config import get_settings
from app.core.database import get_pool
from app.models.schemas import RunImportRequest
from app.services.import_service import import_run

logger = logging.getLogger(__name__)


async def sync_logs() -> int:
    """Scan log directory for new run-*.json files and import them into the database."""
    settings = get_settings()
    pool = await get_pool()

    log_files = sorted(glob(os.path.join(settings.LOG_DIR, "run-*.json")))
    if not log_files:
        return 0

    # Get already-imported filenames
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT log_filename FROM scheduler_runs")
        imported = {r["log_filename"] for r in rows}

    new_count = 0
    for filepath in log_files:
        filename = os.path.basename(filepath)
        if filename in imported:
            continue

        try:
            await _import_log_file(filepath, filename)
            new_count += 1
            logger.info("Imported log: %s", filename)
        except Exception as e:
            logger.error("Failed to import %s: %s", filename, e)

    return new_count


async def _import_log_file(filepath: str, filename: str) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    request = RunImportRequest(**data)
    await import_run(request, log_filename=filename)
