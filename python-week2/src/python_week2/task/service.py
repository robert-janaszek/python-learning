from fastapi import status
from python_week2.exception import DomainException
from python_week2.project.repository import ProjectRepositoryProtocol
from python_week2.schemas import TaskCreate, TaskResponse
from python_week2.task.repository import TaskRepositoryProtocol
from sqlalchemy.ext.asyncio import AsyncSession


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepositoryProtocol,
        project_repository: ProjectRepositoryProtocol,
        session: AsyncSession
    ):
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.session = session
    
    async def mark_complete(self, id: int) -> TaskResponse:
        task_found = await self.task_repository.mark_complete(id)

        if task_found is None:
            raise DomainException(
                message="Task was not found",
                code="TASK_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        await self.session.commit()

        return TaskResponse(
            id=task_found.id,
            title=task_found.title,
            is_completed=task_found.is_completed,
            project_id=task_found.project_id,
        )
    
    async def create_task(self, project_id: int, payload: TaskCreate) -> TaskResponse:
        project = await self.project_repository.get_project(project_id)

        if project is None:
            raise DomainException(
                message="Project was not found",
                code="PROJECT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        task = await self.task_repository.create_task(project_id, payload)
        await self.session.commit()

        return TaskResponse(
            id=task.id,
            title=task.title,
            is_completed=task.is_completed,
            project_id=task.project_id,
        )
