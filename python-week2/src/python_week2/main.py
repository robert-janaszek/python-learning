import time
from fastapi import FastAPI, Depends, HTTPException, Request, status

from fastapi.responses import JSONResponse
from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from python_week2.models import ProjectModel, TaskModel
from python_week2.database import get_db
from python_week2.schemas import ProjectCreate, ProjectResponse, ProjectsResponse, TaskCreate, TaskResponse

app = FastAPI()

class DomainException(Exception):
    def __init__(self, message: str, status_code: int, code: str):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message, "code": exc.code })


@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Process-Time"] = f"{elapsed_ms:.1f}"
    return response


@app.post("/projects/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
async def create_project(payload: ProjectCreate, session: AsyncSession = Depends(get_db)):
    insert_stmt = (
        insert(ProjectModel)
        .values(name=payload.name, description=payload.description)
        .returning(ProjectModel.id, ProjectModel.created_at)
    )

    result = await session.execute(insert_stmt)
    (project_id, created_at) = result.tuples().one()
    await session.commit()

    return ProjectResponse(id=project_id, name=payload.name, created_at=created_at)


@app.get("/projects/", status_code=status.HTTP_200_OK, response_model=list[ProjectsResponse])
async def get_projects(session: AsyncSession = Depends(get_db)):
    select_stmt = (
        select(ProjectModel, func.count(TaskModel.id))
        .outerjoin(ProjectModel.tasks)
        .group_by(ProjectModel.id)
    )
    result = await session.execute(select_stmt)
    rows = result.all()

    rows_mapped = [
        ProjectsResponse(
            id=project.id,
            name=project.name,
            created_at=project.created_at,
            task_count=task_count,
        )
        for (project, task_count) in rows
    ]

    return rows_mapped


@app.post("/projects/{project_id}/tasks/", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(project_id: int, payload: TaskCreate, session: AsyncSession = Depends(get_db)):
    select_project_stmt = select(ProjectModel).where(ProjectModel.id == project_id)
    project_result = await session.execute(select_project_stmt)
    project_found = project_result.scalar_one_or_none()

    if project_found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project was not found")

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

    result = await session.execute(insert_stmt)
    result_one = result.one()
    await session.commit()

    return result_one


@app.patch("/tasks/{task_id}/complete", status_code=status.HTTP_200_OK, response_model=TaskResponse)
async def mark_task_complete(task_id: int, session: AsyncSession = Depends(get_db)):
    update_task_stmt = (
        update(TaskModel)
        .where(TaskModel.id == task_id)
        .values(is_completed=True)
        .returning(
            TaskModel.id,
            TaskModel.title,
            TaskModel.is_completed,
            TaskModel.project_id
        )
    )
    task_result = await session.execute(update_task_stmt)
    task_found = task_result.one_or_none()

    if task_found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")

    await session.commit()

    return task_found
