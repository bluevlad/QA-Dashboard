import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings
from app.services.log_sync_service import sync_logs

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def log_sync_job():
    try:
        count = await sync_logs()
        if count > 0:
            logger.info("Synced %d new log file(s)", count)
    except Exception as e:
        logger.error("Log sync failed: %s", e)


def start_scheduler():
    settings = get_settings()

    scheduler.add_job(
        log_sync_job,
        "interval",
        seconds=settings.SYNC_INTERVAL,
        id="log_sync",
        max_instances=1,
    )
    scheduler.start()
    logger.info("Scheduler started: log sync every %ds", settings.SYNC_INTERVAL)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
