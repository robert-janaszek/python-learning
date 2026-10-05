from fastapi import APIRouter, Depends, status

from mini_jira.dependencies import get_task_service
from mini_jira.task.schemas import TaskCreate, TaskResponse
from mini_jira.task.service import TaskService


router = APIRouter()

@router.post("/projects/{project_id}/tasks/", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(project_id: int, payload: TaskCreate, task_service: TaskService = Depends(get_task_service)):
    return await task_service.create_task(project_id, payload)

@router.patch("/tasks/{task_id}/complete", status_code=status.HTTP_200_OK, response_model=TaskResponse)
async def mark_task_complete(task_id: int, task_service: TaskService = Depends(get_task_service)):
    return await task_service.mark_complete(task_id)
