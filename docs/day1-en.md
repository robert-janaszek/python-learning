## Day 1: Tooling and Python semantics (`uv`, `Ruff`, `dict`, `for`, comprehensions)

**Goal:** Scaffold the project and be able to write functions, loops, dictionaries, and comprehensions from these notes — without looking up syntax.

Everything below is a language crib for **today**. Exercises are at the end of the day. The notes use numbers and names on purpose, not the log dataset — you compute the logs yourself.

---

### 1. Environment setup

- Install `uv` (if you do not have it yet): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Initialize the project: `uv init python-week1 && cd python-week1`
- Add Ruff: `uv add --dev ruff`
- Linter and formatter: `uv run ruff check .` and `uv run ruff format .`
- Run the code: `uv run python-week1` (from the `python-week1` directory). This calls `python_week1:main` from `pyproject.toml`. `uv run` uses the local `.venv`; you do not need to activate it by hand.
- `uv run python -m python_week1` will do nothing until the package has a `__main__.py`, or `main()` is invoked on import.

---

### 2. How Python reads a file

A `.py` file is a **module**. The interpreter reads it top to bottom and executes every statement.

`def name(...):` **defines** a function: it binds the name to a function object. The body does **not** run at definition time. It runs when you call `name(...)`.

So you can put `main()` at the top of the file and `login_durations` below it. `uv` imports the module (every `def` already exists) and **then** calls `main()`. If you called a function on a line *above* its `def`, startup would raise `NameError`.

A comment runs from `#` to end of line. Python ignores it.

---

### 3. Indentation instead of braces

A block (`def`, `if`, `for`) opens with a colon `:`. The body is **indented** (4 spaces in this project). A dedent ends the block. There are no `{ }`.

```python
if n > 0:
    print("positive")
print("always")  # outside the if, because of less indent
```

Mixing tabs and spaces breaks the parser. Ruff/format will normalize it.

---

### 4. Names and assignment

`x = 1` does not declare a type or a “box”. It binds the name `x` to the object `1`.

A later `x = 2` binds the same name to a different object. The old object goes away if nothing else refers to it.

Two writings, two meanings:

- `x = x + 1` or `x += 1` — rebind the name (for numbers).
- `xs.append(3)` — **mutate** the existing list; the name `xs` still points at the same object.

Naming convention: `snake_case` (`last_login`, not `lastLogin`). Style, not syntax.

---

### 5. Types you use today

| Type | Literal | What it is |
| --- | --- | --- |
| `int` | `120` | integer |
| `str` | `"login"` | text; `"..."` or `'...'` |
| `bool` | `True` / `False` | comparison result |
| `list` | `[1, 2, 3]` | ordered sequence; duplicates allowed |
| `dict` | `{"a": 1}` | key → value mapping |

`==` compares **values** (`"login" == "login"` is `True`). `=` is assignment, not comparison.

Type annotations (`n: int`, `def f(xs: list[int]) -> int`) are for you and for checkers (day 7). **Runtime does not enforce them.** You can annotate `-> dict[int, int]` and return something else — the program still runs until you use the result in a way that raises.

`list[dict]` means: a list whose elements are dictionaries. It does **not** describe which keys those dicts have.

---

### 6. Two kinds of lookup: `[]` and `.`

- `object["key"]` — look up an **entry in a mapping** (a dict). The key is an expression, usually `str` or `int`.
- `object.attribute` — look up an **attribute** on the object (a field or method stored on it), e.g. `logs.append`.

A dict stores key–value pairs inside itself. You reach them with `[]`. Dict methods (e.g. `.keys()`) are attributes, so they use a dot.

```python
log = {"user_id": 1, "action": "login"}
log["action"]   # "login" — key
log["user_id"]  # 1
```

Missing key: `log["missing"]` raises `KeyError`.

Write (insert or overwrite):

```python
ages = {}
ages["Ada"] = 3
ages["Ada"] = 4   # same key: 4 remains, 3 is gone
```

A `dict` key is unique. A second assignment under the same key **replaces** the value. That is why a dict comprehension only *looks* like it could sum — it keeps the last value.

---

### 7. Lists

```python
xs = [10, 20, 30]
xs[0]          # 10 — zero-based index
xs.append(40)  # now [10, 20, 30, 40]
len(xs)        # 4
```

A list keeps order. An index out of range raises `IndexError`.

---

### 8. `if`

```python
if log["action"] == "login":
    ...
elif log["action"] == "logout":
    ...
else:
    ...
```

The condition is an expression Python reduces to true/false. Parentheses around it are optional (this is not C/JS).

Today you only need `==` and maybe `and` / `or` / `not`.

---

### 9. The `for` loop

Python `for` is **not** `for (i = 0; i < n; i++)`. It walks the **elements** of a collection.

```python
for n in [10, 20, 30]:
    print(n)
```

Prints `10`, then `20`, then `30`. Each round, the loop name (`n`) is bound to the **next element**, not an index.

Over a list of dicts:

```python
for log in logs:
    print(log["action"], log["duration"])
```

`log` is the whole dict for that round. Fields come from `log["..."]`.

Building a new list with a loop (accumulator):

```python
squares = []
for n in [1, 2, 3, 4]:
    if n % 2 == 0:
        squares.append(n * n)
# squares == [4, 16]
```

`%` is remainder. `n % 2 == 0` means “even”.

This is the mental model for a list comprehension: walk the collection, maybe skip a row, append an expression to the result.

---

### 10. Functions

```python
def double(n: int) -> int:
    return n * 2

x = double(21)  # 42
```

- `def` + name + parameter list in `()`.
- `return expression` leaves the function and hands the value to the caller. With no `return`, the function returns `None`.
- A parameter (`n`) is a local name, bound to the argument (`21`) for the duration of the call.
- Call: `name(arg1, arg2)`.

A function that computes something usually **returns** it; leave `print` in `main()`.

```python
def main() -> None:
    xs = [1, 2, 3]
    print(double(xs[0]))
```

`-> None` means this function returns nothing useful (the effect is `print` or a mutation).

---

### 11. `import`

Pull names from another module at the top of the file:

```python
from collections import defaultdict
```

`collections` is in the standard library. `defaultdict` is a class from that module. After the import you use the name `defaultdict` in this file.

---

### 12. `print`

`print(x)` writes a readable picture of the value and ends the line. Several arguments are separated by spaces: `print(a, b)`.

Lists and dicts print in literal form, e.g. `[120, 110]` or `{1: 150, 2: 110}`. Use that to check the exercises.

---

### 13. List comprehension

An **expression** that builds a new list. Semantics match a loop plus `.append`, in one line.

```python
[expression for item in collection if condition]
```

Evaluation order:

1. Take the next `item` from `collection`.
2. If there is `if condition` and it is false — skip.
3. Evaluate `expression` (it may use `item`).
4. Append the result to the new list.
5. Repeat until the collection is exhausted.

`for` and `if` inside `[...]` belong to this syntax. They are not a separate `for` statement.

```python
[n * 2 for n in [1, 2, 3, 4] if n % 2 == 0]
# 1. n=1 odd → skip
# 2. n=2 → 4
# 3. n=3 skip
# 4. n=4 → 8
# result: [4, 8]
```

The equivalent loop is in §9. In exercises 3a/3b you write a comprehension, not `.map()` / `.filter()` (those are other languages / another idiom; here you learn Python’s syntax).

---

### 14. Dict comprehension

The same idea, but the result is a `dict`. Key on the left, value on the right:

```python
{key: value for item in collection if condition}
```

```python
{n: n * n for n in [1, 2, 3]}
# {1: 1, 2: 4, 3: 9}
```

If the same key comes out a second time, the **later** pair remains — exactly like `d[k] = v` in a loop. A dict comprehension does **not** add values under a key. For a sum you need an accumulator (next section).

```python
{c: 1 for c in ["a", "b", "a"]}
# {"a": 1, "b": 1}  — the second "a" overwrote the first
```

---

### 15. `defaultdict` and `+=`

A plain `dict`: reading a missing key → `KeyError`. To count, you would check every time whether the key already exists.

`defaultdict(factory)` on the **first** read of a missing key calls `factory()` and inserts the result.

`int` as factory: `int()` returns `0`. So `defaultdict(int)` — a missing key behaves like `0`.

```python
from collections import defaultdict

counts = defaultdict(int)
counts["a"] += 1
counts["a"] += 1
counts["b"] += 5
# counts["a"] == 2, counts["b"] == 5
```

`counts["a"] += 1` means: read the current value (or `0`), add `1`, write it back.

`defaultdict` is a subclass of `dict`. `print` looks similar. The difference: reading a missing key **inserts** `0` instead of raising `KeyError`. That is why a function result is often returned as a plain dict:

```python
plain = dict(counts)  # copy of key→value pairs, type dict
```

`dict(counts)` does not change `counts`; it builds a new, ordinary `dict`.

Summing “by key” is a `for` *statement* plus `+=`. A comprehension does not replace that loop.

---

### 16. Exercises — event logs

Data (one list in `main()`, three functions, `print` each):

```python
logs = [
    {"user_id": 1, "action": "login", "duration": 120},
    {"user_id": 2, "action": "login", "duration": 110},
    {"user_id": 1, "action": "logout", "duration": 90},
    {"user_id": 1, "action": "login", "duration": 30},
]
```

Each element is a dict with keys `"user_id"` (`int`), `"action"` (`str`), `"duration"` (`int`).

**3a.** `login_durations(logs: list[dict]) -> list[int]`

List comprehension: `"duration"` values from rows whose `"action"` is `"login"`.

Expected: `[120, 110, 30]`.

**3b.** `last_login_duration(logs: list[dict]) -> dict[int, int]`

Dict comprehension: `user_id → duration` of the **last** login (list order = overwrite order).

Expected: `{1: 30, 2: 110}`.

**3c.** `total_login_duration(logs: list[dict]) -> dict[int, int]`

`defaultdict(int)` and a `for` loop. Add `"duration"` only where `"action"` is `"login"`. Return `dict(...)` or the `defaultdict` itself.

Expected: `{1: 150, 2: 110}`.

Check: `uv run python-week1` from the `python-week1` directory.

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
