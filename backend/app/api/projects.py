from fastapi import APIRouter, Query

from app.models.schemas import ProjectHistoryItem, ProjectStatus
from app.services.project_service import get_project_history, get_projects

router = APIRouter()


@router.get("/projects", response_model=list[ProjectStatus])
async def list_projects():
    return await get_projects()


@router.get("/projects/{name}/history", response_model=list[ProjectHistoryItem])
async def project_history(
    name: str,
    limit: int = Query(30, ge=1, le=100),
):
    return await get_project_history(name, limit=limit)
