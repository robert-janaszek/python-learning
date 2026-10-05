from typing import Literal
from fastapi import status as http_status
from mini_jira.exception import DomainException
from mini_jira.project.repository import ProjectRepositoryProtocol
from mini_jira.schemas import TaskCreate, TaskResponse
from mini_jira.task.repository import TaskRepositoryProtocol
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
                status_code=http_status.HTTP_404_NOT_FOUND,
            )

        await self.session.commit()

        return TaskResponse(
            id=task_found.id,
            title=task_found.title,
            is_completed=task_found.is_completed,
            project_id=task_found.project_id,
            priority=task_found.priority,
        )
    
    async def create_task(self, project_id: int, payload: TaskCreate) -> TaskResponse:
        project = await self.project_repository.get_project(project_id)

        if project is None:
            raise DomainException(
                message="Project was not found",
                code="PROJECT_NOT_FOUND",
                status_code=http_status.HTTP_404_NOT_FOUND,
            )
        
        task = await self.task_repository.create_task(project_id, payload)
        await self.session.commit()

        return TaskResponse(
            id=task.id,
            title=task.title,
            is_completed=task.is_completed,
            project_id=task.project_id,
            priority=task.priority,
        )
    
    async def list_tasks(self, project_id: int, status: Literal["open", "completed", "all"] = "all") -> list[TaskResponse]:
        project = await self.project_repository.get_project(project_id)

        if project is None:
            raise DomainException(
                message="Project was not found",
                code="PROJECT_NOT_FOUND",
                status_code=http_status.HTTP_404_NOT_FOUND,
            )

        if status == "all":
            tasks = await self.task_repository.list_all_tasks(project_id)
        else:
            is_completed = True if status == "completed" else False
            tasks = await self.task_repository.list_tasks_by_is_completed(project_id, is_completed)

        return [TaskResponse(
            id=task.id,
            title=task.title,
            is_completed=task.is_completed,
            project_id = project_id,
            priority=task.priority,
        ) for task in tasks]
