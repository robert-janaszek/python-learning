import json
from typing import Literal
from openai.types.chat import ChatCompletionToolParam
from pydantic import ValidationError

from mini_jira.project.service import ProjectService
from mini_jira.task.schemas import TaskCreate
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

def make_list_tasks(task_service: TaskService, project_service: ProjectService):
    async def list_tasks(
        project_id: int,
        status: Literal["open", "completed", "all"] = "all"
    ) -> str:
        projects = await project_service.get_projects()
        project = next((p for p in projects if p.id == project_id), None)

        if project is None:
            return f"Error: Project with id={project_id} was not found"

        tasks = await task_service.list_tasks(project_id, status)

        return json.dumps([{
            "id": task.id,
            "title": task.title,
            "is_completed": task.is_completed,
            "project_id": project_id,
            "priority": task.priority,
        } for task in tasks])
    
    tool: ChatCompletionToolParam = {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": (
                "Lists tasks in the project with the given id. "
                "Each task includes title, priority, and is_completed. "
                "status selects open tasks, completed tasks, or all of them."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer"},
                    "status": {
                        "type": "string",
                        "enum": ["open", "completed", "all"],
                        "description": "Which tasks to return. Defaults to all.",
                    },
                },
                "required": ["project_id"],
            },
        },
    }
    
    return list_tasks, tool

def make_count_by_priority(task_service: TaskService, project_service: ProjectService):
    async def count_by_priority(
        project_id: int,
        status: Literal["open", "completed", "all"] = "all"
    ) -> str:
        projects = await project_service.get_projects()
        project = next((p for p in projects if p.id == project_id), None)

        if project is None:
            return f"Error: Project with id={project_id} was not found"
        
        tasks = await task_service.list_tasks(project_id, status)

        counts: dict[str, int] = {"low": 0, "medium": 0, "high": 0}

        for task in tasks:
            counts[task.priority] += 1
        
        return f"There are {json.dumps(counts)} {status} tasks in project id={project_id}"

    tool: ChatCompletionToolParam = {
        "type": "function",
        "function": {
            "name": "count_by_priority",
            "description": (
                "Counts tasks in the project with the given id, grouped by priority. "
                "Returns counts for low, medium, and high. "
                "status selects open tasks, completed tasks, or all of them."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer"},
                    "status": {
                        "type": "string",
                        "enum": ["open", "completed", "all"],
                        "description": "Which tasks to count. Defaults to all.",
                    },
                },
                "required": ["project_id"],
            },
        },
    }
    
    return count_by_priority, tool