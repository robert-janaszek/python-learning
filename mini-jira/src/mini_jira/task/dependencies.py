from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mini_jira.database import get_db
from mini_jira.project.dependencies import get_project_repository
from mini_jira.project.repository import ProjectRepository
from mini_jira.task.repository import TaskRepository
from mini_jira.task.service import TaskService

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
