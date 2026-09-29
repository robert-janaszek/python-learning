from sqlalchemy.ext.asyncio import AsyncSession

from mini_jira.project.repository import ProjectRepositoryProtocol
from mini_jira.schemas import ProjectCreate, ProjectResponse, ProjectsResponse


class ProjectService:
    def __init__(self, project_repository: ProjectRepositoryProtocol, session: AsyncSession):
        self.project_repository = project_repository
        self.session = session

    async def get_projects(self) -> list[ProjectsResponse]:
        projects = await self.project_repository.get_all_projects()

        projects_mapped = [
            ProjectsResponse(
                id=project.id,
                name=project.name,
                created_at=project.created_at,
                task_count=task_count,
            )
            for (project, task_count) in projects
        ]

        return projects_mapped

    async def create_project(self, payload: ProjectCreate) -> ProjectResponse:
        (project_id, created_at) = await self.project_repository.create_project(payload)
        await self.session.commit()
        return ProjectResponse(id=project_id, name=payload.name, created_at=created_at)
