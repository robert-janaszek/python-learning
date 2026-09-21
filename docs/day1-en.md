## Day 1: Tooling and clean syntax (`uv`, `Ruff`, `for`, comprehensions)

**Goal:** Set up the environment in 2 minutes, then learn `for`, dictionaries, and the collection-operations idiom.

1. **Environment setup:**
   * Install `uv` (if you do not have it yet): `curl -LsSf https://astral.sh/uv/install.sh | sh`
   * Initialize the project: `uv init python-week1 && cd python-week1`
   * Add Ruff: `uv add --dev ruff`
   * Run the linter and formatter: `uv run ruff check .` and `uv run ruff format .`
   * Run the code: `uv run python-week1` (from the `python-week1` directory). This calls `python_week1:main` from `pyproject.toml`. `uv run` uses the local `.venv`; you do not need to activate it by hand.
   * `uv run python -m python_week1` will do nothing until the package has a `__main__.py`, or `main()` is invoked on import.

2. **Primer: dictionaries and the `for` loop**

An event is a **dictionary** (`dict`): key → value pairs.

```python
log = {"user_id": 1, "action": "login", "duration": 120}
```

You look up a value with **square brackets and the key**: `log["action"]` is `"login"`, `log["duration"]` is `120`. The key is a string, the same one you wrote on the left of the literal.

Several events are a **list** of dicts. A Python `for` loop walks the collection’s elements (here: each dict in turn), not indexes. The loop body is indented.

```python
logs = [
    {"user_id": 1, "action": "login", "duration": 120},
    {"user_id": 2, "action": "login", "duration": 110},
    {"user_id": 1, "action": "logout", "duration": 90},
    {"user_id": 1, "action": "login", "duration": 30},
]

for log in logs:
    print(log["action"], log["duration"])
```

An `if` inside the loop skips selected rows. You build a new list with `.append`:

```python
durations = []
for log in logs:
    if log["action"] == "login":
        durations.append(log["duration"])
```

That is the expanded form of the list comprehension in exercise 3a. Run the `print` loop first so you can see what each `log` contains.

3. **Coding exercise — event logs:**

Keep one `logs` list in `main()` (as above) and call three functions on it (`print` each). Do not use `.map()` / `.filter()`.

A comprehension is the same loop written as an expression. The `for` inside `[...]` or `{...}` belongs to that syntax. In exercise 3c you stay with a `for` *statement*, because you are accumulating a sum in a variable.

**3a. List comprehension — filter + map**

Syntax: `[expression for item in collection if condition]`.

Mini example: `[n * 2 for n in [1, 2, 3, 4] if n % 2 == 0]` → `[4, 8]`.

Write `login_durations(logs: list[dict]) -> list[int]`: the `duration` values for `"login"` events only.

Expected: `[120, 110, 30]`.

**3b. Dict comprehension — last value wins**

Syntax: `{key: value for item in collection if condition}`.

Mini example: `{n: n * n for n in [1, 2, 3]}` → `{1: 1, 2: 4, 3: 9}`.

Write `last_login_duration(logs: list[dict]) -> dict[int, int]`: `user_id → duration` of the **last** login. A repeated key **overwrites** the previous value — that is the lesson. A comprehension does **not** sum.

Expected: `{1: 30, 2: 110}`.

**3c. `defaultdict` — sum by key**

Summing is not a comprehension job. Write `total_login_duration(logs: list[dict]) -> dict[int, int]` with `collections.defaultdict(int)` and a `for` loop (same shape as the primer, plus `+=`):

* `totals = defaultdict(int)` — a missing key is `0`
* for each login: `totals[user_id] += duration`

You can reuse 3a or filter in the loop. Return `dict(totals)` or the `defaultdict` itself.

Expected: `{1: 150, 2: 110}`.

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
