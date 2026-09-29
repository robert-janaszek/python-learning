# python-learning

[Polski](README.pl.md)

A private Python course for people who already program in TypeScript. The repo walks you through week by week: each day you read short notes on an idiomatic pattern, then you do the tasks yourself. Notes are in Polish and in English.

## How to start

The repository contains finished solution code. Before you start the tasks, hide it by renaming the file or changing the extension, for example:

```text
rate_limiter.py  →  rate_limiter.py.solution
```

Python no longer imports that file, so you write your own version from scratch. The old file stays beside it as a crib: open it only when you get stuck.

This applies to the modules in `introduction/src/introduction/` (implementation and tests). Leave `pyproject.toml`, `uv.lock`, and the data files (`users.json`).

Then go day by day. Theory is at the start of the day, tasks at the end.

## Requirements

- Python 3.14 (`introduction/.python-version`)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

From the `introduction` directory:

```bash
uv sync
uv run introduction
```

`uv run` uses the local `.venv`. You do not need to activate the environment yourself.

## How to work

1. Read the notes for one day.
2. Do that day's tasks in your own files.
3. Run the code and the checks given in the notes.
4. Open the `*.solution` files only when you get stuck.

Where a comparison with TypeScript helps, the notes include it. The goal is the pattern used in Python, not a one-to-one syntax translation.

## Week 1 — language and tooling

Project: `introduction/`.

| Day | Topic |
| --- | --- |
| 1 | Tooling and semantics: `uv`, Ruff, `dict`, `for`, comprehensions |
| 2 | Dunder methods, OOP, context managers |
| 3 | Typing and Pydantic v2 |
| 4 | Asynchronicity with `asyncio` |
| 5 | TDD with `pytest` and fixtures |
| 6 | Mini-CLI wiring the previous days together |
| 7 | Code review and Pyright strict mode |

Full check from the `introduction` directory (day 7):

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

## Week 2 — API, database, tests

Project: `mini-jira/`. Weeks 3–6 continue in this directory.

You build a REST API (mini-Jira): FastAPI, SQLAlchemy 2.0, Alembic, integration tests, and Docker. You set up the project on day 8, following the notes.

| Day | Topic |
| --- | --- |
| 8 | Project setup and DTOs with Pydantic v2 |
| 9 | ORM models and the database layer (SQLAlchemy 2.0) |
| 10 | Migrations (Alembic) |
| 11 | FastAPI endpoints |
| 12 | Integration tests (`pytest` + `AsyncClient`) |
| 13 | Errors, middleware, logs |
| 14 | Docker and an architecture review |
