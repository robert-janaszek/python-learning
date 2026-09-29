# Week 2: Async Architecture, Web API (FastAPI), and Database Access (SQLAlchemy 2.0)

This week we move from the language itself to building production backend services. Each day starts with an example, and the task follows immediately below it.

The goal of this week is to build a fully tested REST API for managing projects and tasks (Mini-Jira) with an asynchronous database. The project directory is `mini-jira`. Weeks 3–6 keep using that same directory.

---

### Day 8: Project setup and DTOs with Pydantic v2

In the JS/TS world, the counterpart of FastAPI is NestJS or Express, but FastAPI is built on the **ASGI** standard (Asynchronous Server Gateway Interface) — the counterpart of WSGI for asynchronous code.

* **Pydantic as the I/O layer:** FastAPI automatically validates requests and responses using Pydantic models. It also generates ready-made OpenAPI documentation (`/docs`).

```python
from pydantic import BaseModel, EmailStr

# I/O model (DTO)
class UserCreate(BaseModel):
    email: EmailStr
    age: int
```

* **Task:**
1. Initialize the project: `uv init mini-jira && cd mini-jira`
2. Add Pyright: `uv add --dev pyright` and enable strict mode in `pyproject.toml`:

```toml
[tool.pyright]
typeCheckingMode = "strict"
```

3. Install the required packages in the project with `uv`:
`uv add fastapi uvicorn sqlalchemy aiosqlite alembic httpx pytest-asyncio greenlet`
4. Define the project file structure:
```text
src/
  mini_jira/
    ├── database.py
    ├── models.py
    ├── schemas.py
    ├── main.py
tests/
  └── test_api.py
```
5. In `schemas.py` create Pydantic models for the `Project` and `Task` entities:
* `ProjectCreate` (`name: str`, `description: str | None`)
* `ProjectResponse` (`id: int`, `name: str`, `created_at: datetime`)
* `TaskCreate` (`title: str`, `priority: Literal["low", "medium", "high"]`)
* `TaskResponse` (`id: int`, `title: str`, `is_completed: bool`, `project_id: int`)

---

### Day 9: ORM models and the database layer (SQLAlchemy 2.0)

In Python, SQLAlchemy is the market standard (like Prisma or TypeORM in TS). Version 2.0 introduced a fully asynchronous interface and explicit typing.

* **`DeclarativeBase`:** Base class for entities (counterpart of `@Entity()` in TypeORM).
* **`Mapped` and `mapped_column`:** Modern field-type syntax supported by static type checkers.
* **`AsyncSession`:** Asynchronous session for running queries with an explicit `select()`.

```python
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# 1. Base class
class Base(AsyncAttrs, DeclarativeBase):
    pass

# 2. Entity model
class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)

# 3. Connection setup (in-memory SQLite for the example)
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# 4. Example query (2.0 syntax)
async def get_user_by_email(session: AsyncSession, email: str) -> UserModel | None:
    stmt = select(UserModel).where(UserModel.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

* **Dependency Injection (DI):** FastAPI has a built-in dependency injection container (`Depends`) for managing database sessions, authorization, and configuration. A dependency is a generator: `yield` hands out the session for the request, and the code after `yield` closes it once the request is handled.

```python
def get_db_session():
    db = {"connected": True}
    try:
        yield db
    finally:
        # Cleanup (counterpart of closing a database connection)
        db["connected"] = False
```

* **Task:**
1. In `models.py` create SQLAlchemy models for the `projects` and `tasks` tables. Take the columns from the Pydantic schemas in `schemas.py`.
2. Implement a one-to-many relationship between `ProjectModel` and `TaskModel` using `relationship()` and `ForeignKey`.
3. In `database.py` prepare an async `engine`, `async_sessionmaker`, and a dependency function `get_db()` that uses an async generator (`yield`) to hand out a session and close it after the request is handled.

---

### Day 10: Initializing migrations (Alembic)

Alembic is the companion tool for SQLAlchemy (counterpart of `prisma migrate` or `typeorm migration`).

* It stores the database state in the `alembic_version` table.
* It can automatically detect changes in the structure of `DeclarativeBase` classes and generate migration scripts (`autogenerate`).

* **Task:**
1. Initialize Alembic in the project: `uv run alembic init -t async alembic`
2. Configure `alembic/env.py`, wiring `target_metadata = Base.metadata` from your models.
3. Generate the first automatic migration:
`uv run alembic revision --autogenerate -m "Initial tables"`
4. Run the migration: `uv run alembic upgrade head`.

---

### Day 11: API endpoints in FastAPI

An endpoint receives a Pydantic payload and dependencies through `Depends`. `HTTPException` stops handling and returns an error status.

```python
from fastapi import Depends, HTTPException, status

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: dict = Depends(get_db_session)):
    if payload.age < 18:
        raise HTTPException(status_code=400, detail="User must be adult")
    return {"status": "created", "email": payload.email}
```

* **Task:**
In `main.py` create the following endpoints:
* `POST /projects/` — Create a new project.
* `GET /projects/` — Fetch the list of projects together with the count of assigned tasks.
* `POST /projects/{project_id}/tasks/` — Create a task assigned to a given project (return `HTTP 404` if the project does not exist).
* `PATCH /tasks/{task_id}/complete` — Mark a task as completed.

---

### Day 12: Integration tests (pytest + AsyncClient)

To test asynchronous FastAPI endpoints we use `AsyncClient` from the `httpx` library, wired to `pytest` fixtures.

```python
import pytest
from httpx import AsyncClient, ASGITransport
from my_app import app  # Example import of the FastAPI app

@pytest.fixture
async def async_client():
    # ASGITransport lets you test the app in memory without standing up an HTTP server
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    response = await async_client.post("/users", json={"email": "dev@test.com", "age": 25})
    assert response.status_code == 201
    assert response.json()["email"] == "dev@test.com"
```

* **Task:**
1. Configure `conftest.py` in the `tests/` directory. Create a fixture for an async database session running on an in-memory SQLite database (`sqlite+aiosqlite:///:memory:`).
2. Override the `get_db` dependency in FastAPI during tests using `app.dependency_overrides`.
3. Write full integration tests for:
* Creating a project and verifying status 201.
* Trying to add a task to a project that does not exist (check status 404).
* Reading the project list.

---

### Day 13: Error handling, middleware, and log structure

A request in FastAPI passes through the middleware stack, then reaches the endpoint. The response travels back the same way. These are two places for code that applies to many endpoints at once, rather than to a single route.

* **Exception handler:** a function registered with `@app.exception_handler(ExceptionType)`. FastAPI calls it when that exception, or a subclass, is raised while handling a request, and it expects a `Response` (usually a `JSONResponse`). A custom error class then becomes one JSON shape. This is the equivalent of an exception filter in NestJS.
* **HTTP middleware:** a function registered with `@app.middleware("http")`. It receives `request` and `call_next`. `response = await call_next(request)` sends the request onward (the remaining middleware and the endpoint) and returns the response. After that call you can change it, for example by adding a header, and you must return it. This is the equivalent of `app.use` in Express.

```python
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class QuotaExceeded(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

@app.exception_handler(QuotaExceeded)
async def quota_exceeded_handler(request: Request, exc: QuotaExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": exc.message})

@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.1f}"
    return response
```

* **Task:**
1. Create your own Python exception `DomainException` and register an `exception_handler` for it in FastAPI so that it returns a unified JSON error shape (`{"error": "message", "code": "CUSTOM_CODE"}`).
2. Add simple middleware that measures the execution time of every HTTP request and adds an `X-Process-Time` header to the response.

---

### Day 14: Dockerization and architecture review

* **Task:**
1. Prepare an optimal multi-stage `Dockerfile` for the application using `uv`:
* Stage 1 (Builder): Prepare the environment and install dependencies.
* Stage 2 (Runner): Copy only the finished venv and the application code, and run as a non-root user.
2. Run the container and manually test the documentation at `http://localhost:8000/docs`.
