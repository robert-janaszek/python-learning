import time
from fastapi import FastAPI, Depends, Request, status
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from fastapi.responses import JSONResponse
from python_week2.exception import DomainException
from python_week2.project.service import ProjectService
from python_week2.task.service import TaskService

from python_week2.dependencies import get_project_service, get_task_service
from python_week2.schemas import ProjectCreate, ProjectResponse, ProjectsResponse, TaskCreate, TaskResponse

app = FastAPI()

@app.exception_handler(DomainException)
async def domain_exception_handler(_request: Request, exc: DomainException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message, "code": exc.code })


@app.middleware("http")
async def add_timing_header(request: Request, call_next: RequestResponseEndpoint) -> Response:
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Process-Time"] = f"{elapsed_ms:.1f}"
    return response


@app.post("/projects/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
async def create_project(payload: ProjectCreate, project_service: ProjectService = Depends(get_project_service)):
    return await project_service.create_project(payload)


@app.get("/projects/", status_code=status.HTTP_200_OK, response_model=list[ProjectsResponse])
async def get_projects(project_service: ProjectService = Depends(get_project_service)):
    return await project_service.get_projects()

@app.post("/projects/{project_id}/tasks/", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(project_id: int, payload: TaskCreate, task_service: TaskService = Depends(get_task_service)):
    return await task_service.create_task(project_id, payload)

@app.patch("/tasks/{task_id}/complete", status_code=status.HTTP_200_OK, response_model=TaskResponse)
async def mark_task_complete(task_id: int, task_service: TaskService = Depends(get_task_service)):
    return await task_service.mark_complete(task_id)
