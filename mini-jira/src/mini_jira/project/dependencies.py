from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mini_jira.database import get_db
from mini_jira.project.repository import ProjectRepository
from mini_jira.project.service import ProjectService

def get_project_repository(
    session: AsyncSession = Depends(get_db)
) -> ProjectRepository:
    return ProjectRepository(session)

def get_project_service(
    repo: ProjectRepository = Depends(get_project_repository),
    session: AsyncSession = Depends(get_db)
) -> ProjectService:
    return ProjectService(repo, session)
