# Week 3: Observability, Application Architecture, and Background Processes

This week focuses on solutions used at production scale: inter-system communication, asynchronous background task processing (queues), structured logging, and clean layered architecture in Python. Keep working in the `mini-jira` directory from Week 2.

---

## Day 15: Project structure and Clean Architecture (Service Layer & Repository Pattern)

### 1. Introduction and Concepts

Mixing database logic (SQLAlchemy) directly into FastAPI endpoints makes the code harder to test and maintain. Instead, use the **Repository** pattern (isolating data access) and a **Service Layer** (isolating business logic).

* **Repository Pattern:** A class that wraps ORM queries. Instead of writing `select(UserModel)` in an endpoint, you call `user_repo.get_by_id(user_id)`.
* **Service Layer:** Holds business rules, controls database transactions (`commit`/`rollback`), and calls external services.

#### Example:

```python
from typing import Protocol
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import UserModel

# Protocol (an interface, like in TypeScript)
class UserRepositoryProtocol(Protocol):
    async def get_by_email(self, email: str) -> UserModel | None: ...

# Concrete ORM implementation
class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

# Service Layer
class UserService:
    def __init__(self, repo: UserRepositoryProtocol):
        self.repo = repo

    async def register_user(self, email: str) -> UserModel:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError("User already exists")
        # user creation logic...

```

### 2. Tasks for today

1. Refactor the application built in Week 2 (Mini-Jira):
* Create a `ProjectRepository` class and a `TaskRepository` class in separate files.
* Create `ProjectService` and `TaskService` classes, and put all business logic in them.


2. Slim down the `FastAPI` endpoints so they only deserialize the request, pass data to the service, and return the response.

---

## Day 16: Advanced logging and tracing (Structlog)

### 1. Introduction and Concepts

Python's standard `logging` module produces single-line text that is hard to parse in systems such as Datadog, Kibana, or Grafana Loki. The production standard is **Structlog** — a library that generates JSON logs with context (for example `request_id`, `user_id`).

* **Contextvars:** A Python module for storing thread-local or async-context variables (the counterpart of `AsyncLocalStorage` in Node.js). Used to pass a `correlation_id` through an entire request.

#### Example:

```python
import structlog

# Base Structlog configuration
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars, # Merge async context
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()      # JSON format for production
    ]
)

logger = structlog.get_logger()

# Usage
async def process_order(order_id: str):
    # Bind context onto the current execution context
    structlog.contextvars.bind_contextvars(order_id=order_id)
    
    logger.info("order_processing_started", amount=150.00)
    # Resulting log: {"event": "order_processing_started", "amount": 150.0, "order_id": "123", "level": "info", "timestamp": "..."}

```

### 2. Tasks for today

1. Install `structlog`: `uv add structlog`.
2. Configure `structlog` in your project so it logs in JSON format.
3. Create FastAPI middleware that generates a unique `X-Request-ID` (UUID) for every request, binds it to `structlog.contextvars`, and attaches it to the response header.
4. Replace every plain `print` or `logging` call in the services with `logger.info()` / `logger.error()`.

---

## Day 17: Celery & Redis – Background task queues

### 1. Introduction and Concepts

Some operations (sending emails, generating PDF reports, processing images) take too long to run synchronously inside an HTTP request. In the Python ecosystem, the standard tool for delegating background work is **Celery**, with **Redis** or **RabbitMQ** as the broker.

* **Broker:** Stores queued tasks (for example Redis).
* **Worker:** A separate Python process that pulls tasks from the broker and executes them.
* **Celery Task:** An ordinary function decorated with `@app.task`, invoked with `.delay()`.

#### Example:

```python
# tasks.py
from celery import Celery

celery_app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery_app.task
def send_welcome_email(email: str) -> None:
    # Heavy I/O / SMTP operation
    print(f"Sending email to {email}...")

# main.py (FastAPI Endpoint)
@app.post("/register")
def register(email: str):
    # Async invocation — the function RETURNS IMMEDIATELY, the task lands in Redis
    send_welcome_email.delay(email)
    return {"message": "Registration successful, email queued"}

```

### 2. Tasks for today

1. Add Celery and Redis: `uv add celery redis`.
2. Create a `worker.py` file and configure a Celery instance.
3. Write a Celery task `generate_project_report(project_id: int)` that simulates long-running work (for example `time.sleep(5)`) and writes the result to a file or the console.
4. Call this task from the FastAPI endpoint `POST /projects/{id}/report` using `.delay()`. Make sure the HTTP response returns immediately (status 202 Accepted).

---

## Day 18: ARQ – Modern Async Task Queue (an alternative to Celery)

### 1. Introduction and Concepts

Celery dates back to the Python 2 era and is fully synchronous inside its workers (it uses threads/processes). **ARQ** is a modern, fully asynchronous (`asyncio`) task-queue library built on Redis, a natural fit for FastAPI.

* Lightweight, very fast, and it fully supports `async/await`.
* Native integration with Python typing.

#### Example:

```python
# worker.py
from arq import create_pool
from arq.connections import RedisSettings

async def download_file(ctx: dict, url: str) -> int:
    # ctx holds, among other things, a database connection or an HTTP session attached at startup
    print(f"Downloading {url}")
    return 200

class WorkerSettings:
    functions = [download_file]
    redis_settings = RedisSettings(host="localhost", port=6379)

# In FastAPI
async def trigger_download(request: Request, url: str):
    redis = request.app.state.arq_redis
    await redis.enqueue_job("download_file", url)
    return {"status": "queued"}

```

### 2. Tasks for today

1. Install ARQ: `uv add arq`.
2. Create a simple ARQ worker that runs an asynchronous I/O task (for example a request to an external API via `httpx`).
3. Integrate the ARQ connection pool with the FastAPI application (use FastAPI `lifespan` events to open and close the Redis connection).
4. Compare the syntax and simplicity of ARQ with Celery from the previous day.

---

## Day 19: Caching with Redis and Decorators

### 1. Introduction and Concepts

To avoid constantly querying the database for the same, rarely changing data, add a cache layer (Redis). In Python, you often write **your own decorators** to cache function results transparently.

* **Using `@wraps` from `functools`:** Required when writing decorators in Python, so that function names, docstrings, and typing are preserved.

#### Example:

```python
import json
from functools import wraps
from redis.asyncio import Redis

redis_client = Redis(host="localhost", port=6379)

def cache_json(ttl_seconds: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build a key from the arguments
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached_data = await redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            # Call the original function
            result = await func(*args, **kwargs)
            
            await redis_client.setex(cache_key, ttl_seconds, json.dumps(result))
            return result
        return wrapper
    return decorator

```

### 2. Tasks for today

1. Implement the `cache_json` caching decorator above for asynchronous functions.
2. Apply it to the `get_project_by_id` method in your `ProjectService`.
3. Add cache invalidation: when a project is edited or deleted (`UPDATE`/`DELETE`), delete the matching key from Redis.

---

## Day 20: Profiling and performance (cProfile, memory_profiler, Py-Spy)

### 1. Introduction and Concepts

Before a production deployment, you need to be able to identify bottlenecks (CPU bottlenecks, memory leaks, inefficient loops).

* **`cProfile`:** Python's built-in deterministic profiler (measures the execution time of every function).
* **`py-spy`:** A sampling profiler that runs outside the Python process. Safe to run in production, and it generates **flamegraph** charts.

#### Example of running Py-Spy from the CLI:

```bash
# Generate a flamegraph from a running Python process
uv run py-spy record -o profile.svg --pid <PYTHON_PROCESS_PID>

# Profile a script from the CLI
uv run py-spy top -- uv run main.py

```

### 2. Tasks for today

1. Install `py-spy`: `uv add --dev py-spy`.
2. Create a `benchmark.py` script that performs an inefficient operation (for example processing a large list in a `for` loop by repeatedly concatenating strings instead of using `join`).
3. Profile the script with `py-spy` and generate a `flamegraph.svg` file. Open it in a browser and identify the slowest function.
4. Optimize the code and compare the times before and after the change.

---

## Day 21: Production projects and preparing for code review

### 1. Introduction and Concepts

The last step is to tie architecture, logging, background tasks, and tests into one coherent production system that is ready for code review.

### 2. Tasks for today (Synthesis)

Combine every piece built this week into one coherent microservice:

1. Configure a `docker-compose.yml` that starts:
* The FastAPI application
* A Redis instance
* An ARQ / Celery worker

The database stays SQLite (`app.db` from Week 2). It is a file next to the app, not its own container.


2. Make sure application startup automatically runs Alembic migrations (`alembic upgrade head`).
3. Run a full quality check:
```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest --maxfail=1

```
