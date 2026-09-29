import time
from fastapi import FastAPI, Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from fastapi.responses import JSONResponse
from python_week2.exception import DomainException
from python_week2.project.router import router as project_router
from python_week2.task.router import router as task_router

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


app.include_router(project_router)
app.include_router(task_router)
