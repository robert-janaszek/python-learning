import asyncio
from mini_jira.database import AsyncSessionLocal
from mini_jira.project.dependencies import get_project_repository, get_project_service
from mini_jira.project.schemas import ProjectCreate
from mini_jira.task.dependencies import get_task_repository, get_task_service
from mini_jira.task.schemas import TaskCreate


async def setup_env():
    async with AsyncSessionLocal() as session:
        project_repository = get_project_repository(session)
        task_repository = get_task_repository(session)
        project_service = get_project_service(project_repository, session)
        task_service = get_task_service(task_repository, project_repository, session)

        projects = await project_service.get_projects()
        project = next((p for p in projects if p.name == "Backend"), None)

        if project is not None:
            print("Project Backend already exists. Quitting...")
            return
        
        backend_project = await project_service.create_project(
            ProjectCreate(name="Backend", description=None)
        )

        await task_service.create_task(backend_project.id, TaskCreate(
            title="Fix login",
            priority="high"
        ))

        await task_service.create_task(backend_project.id, TaskCreate(
            title="Deploy failed",
            priority="high"
        ))

        readme_task = await task_service.create_task(backend_project.id, TaskCreate(
            title="Create README",
            priority="low"
        ))

        await task_service.mark_complete(readme_task.id)

if __name__ == "__main__":
    asyncio.run(setup_env())