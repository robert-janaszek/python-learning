
from typing import Literal
from openai.types.chat import ChatCompletionToolParam
from pydantic import ValidationError

from mini_jira.project.service import ProjectService
from mini_jira.schemas import TaskCreate
from mini_jira.task.service import TaskService


def make_create_task(task_service: TaskService, project_service: ProjectService):
    async def create_task(
        project_id: int,
        title: str,
        priority: Literal["low", "medium", "high"]
    ) -> str:
        projects = await project_service.get_projects()
        project = next((p for p in projects if p.id == project_id), None)

        if project is None:
            return f"Error: Project with id={project_id} was not found"
        
        try:
            task_create_payload = TaskCreate(
                title=title,
                priority=priority,
            )
        except ValidationError as err:
            details = "; ".join(
                f"{err['loc'][0]}: {err['msg']}" for err in err.errors()
            )
            return f"Error: {details}"

        result = await task_service.create_task(
            project_id=project.id,
            payload=task_create_payload
        )

        return f"SUCCESS: Task was created with id={result.id}"

    tool: ChatCompletionToolParam = {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Creates a task in the project with the given id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": ["project_id", "title", "priority"],
            },
        },
    }

    return create_task, tool