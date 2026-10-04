
from typing import Literal
from openai.types.chat import ChatCompletionToolParam
from mini_jira.project.service import ProjectService
from mini_jira.schemas import TaskCreate
from mini_jira.task.service import TaskService


def make_create_task(task_service: TaskService, project_service: ProjectService):
    async def create_task(
        project_name: str,
        title: str,
        priority: Literal["low", "medium", "high"]
    ) -> str:
        projects = await project_service.get_projects()
        project = next((p for p in projects if p.name == project_name), None)

        if project is None:
            return f"Project with name {project_name} was not found"

        result = await task_service.create_task(
            project_id=project.id,
            payload=TaskCreate(
                title=title,
                priority=priority,
            )
        )

        return f"Task was created with id={result.id}"
    
    tool: ChatCompletionToolParam = {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Creates a task in the project with the given name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string"},
                    "title": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": ["project_name", "title", "priority"],
            },
        },
    }

    return create_task, tool