from typing import Protocol

from mini_jira.models import TaskModel
from mini_jira.schemas import TaskCreate
from sqlalchemy import Row, insert, update
from sqlalchemy.ext.asyncio import AsyncSession


class TaskRepositoryProtocol(Protocol):
    async def create_task(self, project_id: int, payload: TaskCreate) -> Row[tuple[int, str, bool, int]]: ...
    async def mark_complete(self, id: int) -> (Row[tuple[int, str, bool, int]] | None): ...


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def mark_complete(self, id: int) -> (Row[tuple[int, str, bool, int]] | None):
        update_task_stmt = (
            update(TaskModel)
            .where(TaskModel.id == id)
            .values(is_completed=True)
            .returning(
                TaskModel.id,
                TaskModel.title,
                TaskModel.is_completed,
                TaskModel.project_id
            )
        )
        task_result = await self.session.execute(update_task_stmt)

        return task_result.one_or_none()
    
    async def create_task(self, project_id: int, payload: TaskCreate) -> Row[tuple[int, str, bool, int]]:
        insert_stmt = (
            insert(TaskModel)
            .values(
                title=payload.title,
                priority=payload.priority,
                project_id=project_id
            )
            .returning(
                TaskModel.id,
                TaskModel.title,
                TaskModel.is_completed,
                TaskModel.project_id
            )
        )

        result = await self.session.execute(insert_stmt)
        return result.one()