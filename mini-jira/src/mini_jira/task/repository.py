from typing import Protocol, Sequence

from mini_jira.models import TaskModel
from mini_jira.schemas import TaskCreate
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class TaskRepositoryProtocol(Protocol):
    async def create_task(self, project_id: int, payload: TaskCreate) -> TaskModel: ...
    async def mark_complete(self, id: int) -> TaskModel | None: ...
    async def list_all_tasks(self, project_id: int) -> Sequence[TaskModel]: ...
    async def list_tasks_by_is_completed(self, project_id: int, is_completed: bool) -> Sequence[TaskModel]: ...


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, project_id: int, payload: TaskCreate) -> TaskModel:
        insert_stmt = (
            insert(TaskModel)
            .values(
                title=payload.title,
                priority=payload.priority,
                project_id=project_id
            )
            .returning(TaskModel)
        )

        result = await self.session.execute(insert_stmt)
        return result.scalar_one()

    async def mark_complete(self, id: int) -> TaskModel | None:
        update_task_stmt = (
            update(TaskModel)
            .where(TaskModel.id == id)
            .values(is_completed=True)
            .returning(TaskModel)
        )
        task_result = await self.session.execute(update_task_stmt)

        return task_result.scalar_one_or_none()

    async def list_all_tasks(self, project_id: int) -> Sequence[TaskModel]:
        select_stmt = select(TaskModel).where(TaskModel.project_id == project_id)
        result = await self.session.execute(select_stmt)
        return result.scalars().all()
    
    async def list_tasks_by_is_completed(self, project_id: int, is_completed: bool) -> Sequence[TaskModel]:
        select_stmt = select(TaskModel).where(
            TaskModel.project_id == project_id,
            TaskModel.is_completed == is_completed
        )
        result = await self.session.execute(select_stmt)
        return result.scalars().all()