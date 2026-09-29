from fastapi import APIRouter, Depends, status

from python_week2.dependencies import get_project_service
from python_week2.project.service import ProjectService
from python_week2.schemas import ProjectCreate, ProjectResponse, ProjectsResponse

router = APIRouter(prefix="/projects")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
async def create_project(payload: ProjectCreate, project_service: ProjectService = Depends(get_project_service)):
    return await project_service.create_project(payload)


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ProjectsResponse])
async def get_projects(project_service: ProjectService = Depends(get_project_service)):
    return await project_service.get_projects()
