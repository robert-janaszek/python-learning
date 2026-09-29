# Week 6: Distributed Systems, Asynchronous AI, and Production Operations

In the last week you plug the AI modules into a production-shaped system: queues, SSE streaming, and full observability. Keep working in the `mini-jira` directory from Week 2.

---

## Day 36: Async AI Processing with ARQ

### 1. Introduction and Concepts

Local LLMs are slow and heavy (a reply can take several seconds to more than a minute). Those calls should not block the HTTP handler — they blow past client timeouts.

* Event-driven shape: HTTP POST enqueues a job in ARQ → a worker runs it on the local LLM → the result is stored in the database. The client gets a `task_id` immediately and reads the result when the worker finishes.

### 2. Tasks for today

1. Connect the agent you built to the ARQ worker from Week 3.
2. Add `POST /agent/tasks`. It accepts a hard task, returns a `task_id` immediately, and the agent does the work in the background on the local LLM.

---

## Day 37: SSE (Server-Sent Events) for AI Interfaces

### 1. Introduction and Concepts

The user should not stare at a blank screen for 20 seconds. They should see the agent's steps and tokens as they arrive.

* **SSE (Server-Sent Events):** The one-way protocol this course uses to stream an LLM reply to the browser.
* **`StreamingResponse`:** Built into FastAPI / Starlette. In the example, the generator yields SSE frames (`data: ...\n\n`) with `media_type="text/event-stream"`.
* **`EventSourceResponse` (`sse-starlette`):** A separate library, not part of FastAPI. Use it when you want named events (`event: tool_called`).

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def llm_token_generator():
    tokens = ["Hello", "!", " I", " am", " your", " AI", " agent."]
    for token in tokens:
        await asyncio.sleep(0.2)
        yield f"data: {token}\n\n"

@app.get("/stream")
async def stream_ai_reply():
    return StreamingResponse(llm_token_generator(), media_type="text/event-stream")

```

### 2. Tasks for today

1. Add SSE support: `uv add sse-starlette`.
2. Build a FastAPI endpoint (`EventSourceResponse` from `sse-starlette`) that streams both local-LLM tokens and tool status (for example an event named `tool_called` with data `{"name": "search_db"}`).

---

## Day 38: Tracing and Observability for AI (OpenTelemetry + Langfuse / Phoenix)

### 1. Introduction and Concepts

On a normal backend you trace SQL. On an AI app you also need the **exact prompt, token usage, LLM latency, tool calls, and the retrieved RAG context**.

* **Langfuse / Arize Phoenix:** Self-hosted or cloud APM for AI apps, built on OpenTelemetry.

### 2. Tasks for today

1. Run Phoenix or Langfuse locally in Docker (`docker run -p 6006:6006 arizephoenix/phoenix`).
2. Attach OpenTelemetry in Python to the OpenAI client, Instructor, and LangGraph.
3. Send a few requests through the agent and inspect the full trace tree in the local UI.

---

## Day 39: Model Call Parameters from Python

### 1. Introduction and Concepts

The server stays the one from Day 22 (Ollama or LM Studio). Today you steer the reply from code, with arguments to `chat.completions.create`.

* **`temperature`:** how far the model may drift from the most likely token. `0` stays on one track; a higher value spreads the replies.
* **`top_p`:** keeps only tokens from the top of the probability distribution.
* **`max_tokens`:** a cap on tokens in the reply.

```python
response = await client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
    top_p=0.9,
    max_tokens=512,
)
```

### 2. Tasks for today

1. Send the same prompt three times, with `temperature` set to `0`, `0.7`, and `1.2`, and compare the replies.
2. Set `max_tokens` so the reply stops mid-sentence, then raise the limit and read the full reply.

---

## Day 40: System Design — an End-to-End Enterprise AI Service

### 1. Introduction and Concepts

Design one system that uses everything from the course, and implement it as a single scalable backend.

### 2. Tasks for today

1. Design and implement the final Python backend:
* **FastAPI** as the API gateway, with Pydantic v2 validation.
* **SSE** to stream replies to the client.
* **ARQ + Redis** for background AI jobs.
* **SQLite (`app.db`) + SQLAlchemy 2.0** for users and conversation history. The same database as in Week 2.
* **LanceDB** as the embedded vector store for RAG.
* A **local LLM** behind an OpenAI-compatible API, driving the agent and RAG.
* **Structlog + OpenTelemetry** for system-wide observability.



---

## Day 41: Multi-stage Docker Build for an AI / Python App

### 1. Introduction and Concepts

AI container images need a small, locked-down production stage (no compiler toolchain left in the final image).

### 2. Tasks for today

1. Write a multi-stage `Dockerfile` that uses `uv` and installs production dependencies only.
2. Write a `docker-compose.yml` that brings up the API, Redis, the worker, and tracing with one command (`docker compose up`). SQLite (`app.db`) and LanceDB are files in the app, not separate containers.

---

## Day 42: Course Review and Code Review

### 1. Task

Run the full quality check on the code from all six weeks. Every command must exit 0: no Ruff findings, no type errors, no failing tests.

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest

```

You have walked the whole path: Python idioms, an async backend (FastAPI / SQLAlchemy), then production-shaped agents and RAG on local models.
