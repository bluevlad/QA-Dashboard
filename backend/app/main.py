import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import close_db, init_db
from app.core.scheduler import log_sync_job, start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting QA-Dashboard backend...")
    await init_db()

    # Initial sync on startup
    await log_sync_job()

    start_scheduler()
    logger.info("QA-Dashboard backend started")

    yield

    logger.info("Shutting down QA-Dashboard backend...")
    stop_scheduler()
    await close_db()
    logger.info("QA-Dashboard backend shut down")


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from app.api.health import router as health_router
from app.api.import_api import router as import_router
from app.api.projects import router as projects_router
from app.api.runs import router as runs_router
from app.api.summary import router as summary_router
from app.api.trends import router as trends_router

app.include_router(health_router, prefix="/api")
app.include_router(runs_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(trends_router, prefix="/api")
app.include_router(summary_router, prefix="/api")
app.include_router(import_router, prefix="/api")
