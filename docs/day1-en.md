## Day 1: Tooling and clean syntax (`uv`, `Ruff`, comprehensions)

**Goal:** Set up the environment in 2 minutes and master the collection-operations idiom.

1. **Environment setup:**
   * Install `uv` (if you do not have it yet): `curl -LsSf https://astral.sh/uv/install.sh | sh`
   * Initialize the project: `uv init python-week1 && cd python-week1`
   * Add Ruff: `uv add --dev ruff`
   * Run the linter and formatter: `uv run ruff check .` and `uv run ruff format .`

2. **Coding exercise:**
   * You have a list of dictionaries representing event logs: `[{"user_id": 1, "action": "login", "duration": 120}, ...]`.
   * Write a function that, using a **list/dict comprehension** (no `for` loops and no `.map()` / `.filter()`):
     * Filters only events of type `"login"`.
     * Returns a dictionary `{user_id: total_duration}` (including the case where a user has multiple logs — try using `collections.defaultdict`).

---

## Day 2: Dunder methods, OOP, and context managers

**Goal:** Understand how objects in Python interact with language syntax.

1. **Coding exercise — magic methods:**
   * Create a `RateLimiter` class that takes `max_requests: int` and `window_seconds: int`.
   * Implement `__call__(self, user_id: str) -> bool` so the class instance is callable like a function (`limiter("user_123")`).
   * Implement `__repr__` so `print(limiter)` yields a readable debug string: `RateLimiter(max_requests=10, window=60)`.

2. **Coding exercise — custom context manager:**
   * Write a `Timer` class using the context manager protocol (`__enter__` and `__exit__`).
   * Usage: `with Timer("DB Query"): ...` should automatically measure the block’s runtime and print it on exit.

---

## Day 3: Typing and Pydantic v2 (Python’s “Zod”)

**Goal:** Data models at the I/O boundary with full validation and static typing.

1. **Setup:**
   * Add Pydantic and Pyright/Mypy: `uv add pydantic` and `uv add --dev pyright`

2. **Coding exercise:**
   * Create a Pydantic model `UserPayload`:
     * `id`: `UUID`
     * `email`: `EmailStr`
     * `roles`: `list[Literal["admin", "user", "guest"]]`
     * `created_at`: `datetime` (with an automatic default in the UTC timezone)
   * Add a `@field_validator` for `roles` that raises an error if the list is empty.
   * Add a `@model_validator(mode="after")` that requires role `"admin"` when `email` ends with `@company.com`.
   * Test deserializing invalid JSON and handle `ValidationError`.

---

## Day 4: Asynchronicity in `asyncio`

**Goal:** Understand the explicit event loop and avoid blocking it.

1. **Coding exercise — async fetcher & rate limiting:**
   * Write an async function `fetch_metrics(service_id: int) -> dict` that simulates an HTTP request (`await asyncio.sleep(0.5)`).
   * Fetch data concurrently for 20 services (`service_id` from 1 to 20) using `asyncio.gather`.
   * Cap concurrency at 3 in-flight requests with `asyncio.Semaphore`.
   * **Trap to test:** Add a synchronous `time.sleep(2)` in one of the functions and watch it block the whole event loop. Fix it by moving the blocking call to another thread with `asyncio.to_thread`.

---

## Day 5: TDD with `pytest` and fixtures

**Goal:** Write idiomatic tests using fixtures and parametrization.

1. **Setup:**
   * Add pytest: `uv add --dev pytest pytest-asyncio`

2. **Coding exercise:**
   * Build a simple class-based `UserService` with an in-memory cache (dictionary).
   * Write a `pytest` suite:
     * Use `@pytest.fixture` to provide a fresh `UserService` instance before each test.
     * Use `@pytest.mark.parametrize` to test email validation on 5 different valid and invalid strings in a single test.
     * Use `pytest.raises(ValueError)` to assert thrown exceptions.

---

## Day 6: Mini-CLI from everything you wired together

**Goal:** Combine the tools into one coherent script.

1. **Exercise:**
   * Create a CLI that takes a path to a JSON file with a list of users, validates each entry with Pydantic, “processes” them asynchronously (simulated I/O), and writes aggregated stats to a new file.
   * Everything should be fully typed, formatted by `ruff`, and covered by passing `pytest` tests.

---

## Day 7: Code review and Pyright strict mode

**Goal:** Verify code quality against production standards.

1. Enable strict type checking in `pyproject.toml` for Pyright (`typeCheckingMode = "strict"`) or Mypy (`strict = true`).
2. Review the Day 6 code and eliminate all typing warnings (missing `None`, `Any` types, `Optional` mismatches).
3. Run the full check pipeline:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```
