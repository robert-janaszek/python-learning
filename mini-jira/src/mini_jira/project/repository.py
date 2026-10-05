from datetime import datetime
from typing import Protocol
from sqlalchemy import Row, func, insert, select

from mini_jira.models import ProjectModel, TaskModel
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence

from mini_jira.project.schemas import ProjectCreate

class ProjectRepositoryProtocol(Protocol):
    async def create_project(self, payload: ProjectCreate) -> tuple[int, datetime]: ...
    async def get_all_projects(self) -> Sequence[Row[tuple[ProjectModel, int]]]: ...
    async def get_project(self, project_id: int) -> ProjectModel | None: ...


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_project(self, payload: ProjectCreate) -> tuple[int, datetime]:
        insert_stmt = (
            insert(ProjectModel)
            .values(name=payload.name, description=payload.description)
            .returning(ProjectModel.id, ProjectModel.created_at)
        )

        result = await self.session.execute(insert_stmt)
        (project_id, created_at) = result.tuples().one()

        return (project_id, created_at)
    
    async def get_all_projects(self) -> Sequence[Row[tuple[ProjectModel, int]]]:
        select_stmt = (
            select(ProjectModel, func.count(TaskModel.id))
            .outerjoin(ProjectModel.tasks)
            .group_by(ProjectModel.id)
        )
        result = await self.session.execute(select_stmt)
        return result.all()

    async def get_project(self, project_id: int) -> ProjectModel | None:
        select_project_stmt = select(ProjectModel).where(ProjectModel.id == project_id)
        project_result = await self.session.execute(select_project_stmt)
        return project_result.scalar_one_or_none()