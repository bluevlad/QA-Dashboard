from fastapi import APIRouter

from app.core.config import get_settings
from app.core.database import get_pool
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    settings = get_settings()
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = str(e)
    return HealthResponse(status="ok", version=settings.APP_VERSION, database=db_status)
