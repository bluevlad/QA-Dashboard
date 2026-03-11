import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.auth.config import get_auth_settings
from app.core.config import get_settings
from app.core.database import close_db, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting QA-Dashboard backend...")
    await init_db()
    logger.info("QA-Dashboard backend started")

    yield

    logger.info("Shutting down QA-Dashboard backend...")
    await close_db()
    logger.info("QA-Dashboard backend shut down")


settings = get_settings()
auth_settings = get_auth_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    root_path="/qa",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(SessionMiddleware, secret_key=auth_settings.SESSION_SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.auth.google_oauth import router as auth_router
from app.api.health import router as health_router
from app.api.import_api import router as import_router
from app.api.projects import router as projects_router
from app.api.runs import router as runs_router
from app.api.search import router as search_router
from app.api.summary import router as summary_router
from app.api.trends import router as trends_router

app.include_router(auth_router)
app.include_router(health_router, prefix="/api")
app.include_router(import_router, prefix="/api")
app.include_router(runs_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(summary_router, prefix="/api")
app.include_router(trends_router, prefix="/api")
