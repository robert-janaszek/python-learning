from fastapi import Depends
from python_week2.project.repository import ProjectRepository
from python_week2.project.service import ProjectService
from python_week2.task.repository import TaskRepository
from python_week2.task.service import TaskService
from sqlalchemy.ext.asyncio import AsyncSession

from python_week2.database import get_db

def get_project_repository(
    session: AsyncSession = Depends(get_db)
) -> ProjectRepository:
    return ProjectRepository(session)

def get_project_service(
    repo: ProjectRepository = Depends(get_project_repository),
    session: AsyncSession = Depends(get_db)
) -> ProjectService:
    return ProjectService(repo, session)

def get_task_repository(
    session: AsyncSession = Depends(get_db)
) -> TaskRepository:
    return TaskRepository(session)

def get_task_service(
    task_repository: TaskRepository = Depends(get_task_repository),
    project_repository: ProjectRepository = Depends(get_project_repository),
    session: AsyncSession = Depends(get_db)
) -> TaskService:
    return TaskService(task_repository, project_repository, session)
