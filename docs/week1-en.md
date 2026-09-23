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

### Introduction to decorators

In Python a function is an object. You can pass it into another function the same way you pass a number or a string.

A decorator is a function that takes a function and returns a function. Usually it returns a new function: that one calls the original and adds its own behavior. The `@` spelling is shorthand. Python takes the function from the `def` on the next line and passes it through the decorator immediately.

```python
def twice(fn):
    def wrapped(n: int) -> int:
        return fn(n) * 2

    return wrapped


@twice
def add_one(n: int) -> int:
    return n + 1


add_one(3)  # 8
```

`@twice` sits on the line above `def`. After the definition, the name `add_one` already refers to the result of `twice(...)`, which is `wrapped`. Calling `add_one(3)` enters `wrapped`: it calls the original (`3 + 1`) and multiplies the result by 2.

The same thing without `@`:

```python
def add_one(n: int) -> int:
    return n + 1


add_one = twice(add_one)
```

`@` runs once, at definition time, while the module is loading. Later calls go through the wrapped function.

A decorator can be a factory. It takes arguments itself and returns the real decorator. The parentheses are then part of the spelling: you call the factory first, and whatever it returns wraps the function.

```python
def tag(label: str):
    def decorator(fn):
        fn.label = label
        return fn

    return decorator


@tag("points")
def check(value: int) -> int:
    return value


check.label  # "points"
```

`@tag("points")` means `check = tag("points")(check)`.

Several decorators stack, one above another. Python applies them from the bottom: the one closest to `def` wraps first.

```python
@outer
@inner
def f():
    ...
```

is `f = outer(inner(f))`.

`@field_validator(...)` and `@model_validator(...)` in the exercise below are decorators written in Pydantic. You configure them in the parentheses, and they wrap the method in the `def` underneath — the same mechanism as `twice` and `tag`.

### Introduction to validation in Pydantic

A model is a class that inherits from `BaseModel`. Fields stay annotations. Validation is a method under a decorator. Pydantic calls it when you build an object from data.

Each of these decorators gets its own `def`. `@field_validator` and `@model_validator` run at different times and receive different arguments.

**One field.** `@field_validator("name")` wraps a method that receives that field’s value. In v2 it is a `@classmethod`: the first argument is the class (`cls`), the second is the value. Return the value that should stay on the field. Reject a bad value with `raise ValueError("...")`.

```python
from pydantic import BaseModel, field_validator


class Score(BaseModel):
    points: int

    @field_validator("points")
    @classmethod
    def non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("points must be >= 0")
        return value
```

`Score(points=-1)` is never created: Pydantic turns the `ValueError` into a `ValidationError`. `Score(points=3)` succeeds because the method returned `3`.

**Several fields at once.** `@model_validator(mode="after")` wraps an instance method. Pydantic calls it once the fields are already set. You read them through `self` and return `self`. A rule that combines fields also raises `ValueError`.

```python
from typing import Self

from pydantic import BaseModel, model_validator


class Pair(BaseModel):
    left: int
    right: int

    @model_validator(mode="after")
    def left_not_above_right(self) -> Self:
        if self.left > self.right:
            raise ValueError("left must be <= right")
        return self
```

You choose the method names (`non_negative`, `left_not_above_right`). What matters is the decorator, the arguments, and whether you return a value or raise `ValueError`. You write the `UserPayload` rules separately, on this same shape.

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

### Introduction to `asyncio`

An ordinary function holds the thread until `return`. The rest of the program waits. `async def` defines a **coroutine**: a function that can pause on `await` and hand control to the event loop. The loop runs other coroutines in that time, then comes back.

`async def` by itself starts nothing. `asyncio.run` starts a coroutine — once, at the top of the program. Inside a coroutine you call the next one with `await`.

```python
import asyncio


async def boil(item: str) -> str:
    await asyncio.sleep(0.1)
    return item


async def cook() -> None:
    ready = await boil("water")
    print(ready)


asyncio.run(cook())
```

`asyncio.sleep` gives the loop back for the given time. `time.sleep` holds the thread: the loop stays still until the sleep finishes, and no other coroutine moves in that time.

`asyncio.gather` starts several coroutines and waits until all of them finish. The result is a list in the same order as the arguments.

```python
async def cook() -> None:
    ready = await asyncio.gather(boil("water"), boil("pasta"), boil("sauce"))
    print(ready)  # ["water", "pasta", "sauce"]
```

`asyncio.Semaphore(n)` holds a count of entries. `async with` takes one entry for the duration of the block and gives it back on exit. `gather` can start many coroutines, and the semaphore keeps at most `n` of them inside the block at once.

```python
async def cook() -> None:
    burners = asyncio.Semaphore(2)

    async def one(item: str) -> str:
        async with burners:
            return await boil(item)

    ready = await asyncio.gather(*(one(item) for item in ["water", "pasta", "sauce"]))
    print(ready)
```

Create the semaphore inside the coroutine that `asyncio.run` starts. An object created while the module is imported can end up bound to a different loop.

When you have to call a function that holds the thread (`time.sleep`, ordinary I/O with no `await`), move it off the loop. `asyncio.to_thread` runs it in a thread and returns an awaitable: the loop runs the rest in the meantime.

```python
import time


def slow_label(item: str) -> str:
    time.sleep(1)
    return item.upper()


async def cook() -> None:
    label = await asyncio.to_thread(slow_label, "water")
    print(label)
```

The function’s arguments follow it: `to_thread(slow_label, "water")` means `slow_label("water")` in the thread.

1. **Coding exercise — async fetcher & rate limiting:**
   * Write an async function `fetch_metrics(service_id: int) -> dict` that simulates an HTTP request (`await asyncio.sleep(0.5)`).
   * Fetch data concurrently for 20 services (`service_id` from 1 to 20) using `asyncio.gather`.
   * Cap concurrency at 3 in-flight requests with `asyncio.Semaphore`.
   * **Trap to test:** Add a synchronous `time.sleep(2)` in one of the functions and watch it block the whole event loop. Fix it by moving the blocking call to another thread with `asyncio.to_thread`.

---

## Day 5: TDD with `pytest` and fixtures

**Goal:** Write idiomatic tests using fixtures and parametrization.

### Introduction to `pytest`

A test is a function named `test_...` in a file named `test_*.py`. `pytest` collects them on its own. Run it from the `python-week1` directory: `uv run pytest`. An assertion is a plain `assert`. A false result fails the test and shows the values on both sides of the comparison.

A fixture prepares an object before the test. `@pytest.fixture` sits above a `def`, the same way as the decorators from Day 3. The test receives the fixture’s result through an argument of the same name. By default the fixture runs again before every test that asks for it.

```python
import pytest


class Stack:
    def __init__(self) -> None:
        self.items: list[int] = []

    def push(self, n: int) -> None:
        if n < 0:
            raise ValueError("negative")
        self.items.append(n)


@pytest.fixture
def stack() -> Stack:
    return Stack()


def test_push(stack: Stack) -> None:
    stack.push(1)
    assert stack.items == [1]
```

`@pytest.mark.parametrize` runs the same test once per list element. The name in the string has to match the function argument.

```python
@pytest.mark.parametrize("n", [-1, -5])
def test_rejects_negative(stack: Stack, n: int) -> None:
    with pytest.raises(ValueError):
        stack.push(n)
```

`pytest.raises` is a context manager: an exception inside the `with` block passes the test. No exception, or a different type, fails it.

An async test is an `async def`. `pytest` alone will not run it. After `pytest-asyncio`, mark it with `@pytest.mark.asyncio` and use `await` inside, as in Day 4.

```python
import asyncio

import pytest


@pytest.mark.asyncio
async def test_pause() -> None:
    await asyncio.sleep(0)
    assert True
```

1. **Setup:**
   * Add pytest: `uv add --dev pytest pytest-asyncio`

2. **Coding exercise:**

`UserService` remembers users in a dictionary on the instance. The key is the email. A second lookup of the same address returns the stored entry. A fixture that builds a clean `UserService` starts every test with an empty dictionary: a registration in one test does not leave a user behind for the next one.

   * Build a `UserService` class:
     * In `__init__`, create an empty dictionary `self._users: dict[str, dict[str, str]]`.
     * `validate_email(self, email: str) -> None` — an address is valid when it contains exactly one `@` and both sides of it are non-empty. A valid address returns without error. Anything else raises `ValueError`. Write the check yourself: `EmailStr` from Day 3 raises `ValidationError`, and this exercise wants `ValueError`.
     * `register(self, email: str) -> dict[str, str]` — call `validate_email` first. If the email is already in the dictionary, return that same entry and do not overwrite it. Otherwise store `{"email": email}` and return it.
     * `get_user(self, email: str) -> dict[str, str]` — return the entry from the dictionary. A missing key raises `KeyError`.
   * Write tests in a `test_*.py` file:
     * `@pytest.fixture` returns a new `UserService` before every test that asks for it.
     * One test with `@pytest.mark.parametrize` checks five strings. Include both valid and invalid addresses. A valid one passes through `validate_email`. An invalid one is caught with `pytest.raises(ValueError)`.
     * Calling `register` twice with the same email returns the same dictionary (`is`). `_users` then holds one entry. A different email is a separate entry.
     * `get_user` after `register` returns the stored entry. `get_user` for an unknown address is caught with `pytest.raises(KeyError)`.

---

## Day 6: Mini-CLI from everything you wired together

**Goal:** Combine the tools into one coherent script.

### Introduction to the CLI, files, and JSON

`uv run python-week1` calls `main()`. Extra words after the command land in `sys.argv`. `argparse` reads them and reports an error when a required argument is missing.

```python
import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    text = Path(args.path).read_text(encoding="utf-8")
    print(text)
```

Invocation: `uv run python-week1 notes.txt`. `Path.read_text` returns the whole file as a `str`. `Path.write_text` replaces the file with the given text.

`json.loads` turns JSON text into Python objects. A JSON array becomes a `list`, a JSON object becomes a `dict`. `json.dumps` goes the other way: from a Python object to text.

```python
import json
from pathlib import Path

raw = Path("nums.json").read_text(encoding="utf-8")
rows = json.loads(raw)  # e.g. [{"n": 1}, {"n": 2}]
Path("summary.json").write_text(
    json.dumps({"count": len(rows)}),
    encoding="utf-8",
)
```

A single JSON object that should match a Pydantic model goes in as text to `model_validate_json`. A list of such objects: `json.loads` first, then `model_validate` on each dictionary. A bad entry raises `ValidationError`, as in Day 3.

`main()` is an ordinary function. You start Day 4 coroutines from it with `asyncio.run(...)`. Every new `def` has argument annotations and a return type — Day 7 turns on a mode that requires them.

1. **Exercise:**
   * Create a CLI that takes a path to a JSON file with a list of users, validates each entry with Pydantic, “processes” them asynchronously (simulated I/O), and writes aggregated stats to a new file.
   * Everything should be fully typed, formatted by `ruff`, and covered by passing `pytest` tests.

---

## Day 7: Code review and Pyright strict mode

**Goal:** Verify code quality against production standards.

### Introduction to strict mode

Pyright in strict mode reads annotations and rejects places where the type could be anything. In `python-week1/pyproject.toml`:

```toml
[tool.pyright]
typeCheckingMode = "strict"
```

Or, if you use Mypy:

```toml
[tool.mypy]
strict = true
```

A function that sometimes finds nothing returns `str | None`. A bare `-> str` fails strict mode, because `None` is not a `str`. Before you use a `str | None` value as a string, you check for `None`.

```python
def first(items: list[str]) -> str | None:
    if not items:
        return None
    return items[0]


def shout(name: str | None) -> str:
    if name is None:
        return ""
    return name.upper()
```

`Any` turns checking off at that spot. Strict mode still lets you write it, and the exercise tells you to remove those spots: the argument, the result, and the attribute get a concrete type.

The four commands from the `python-week1` directory check different things. `ruff check` looks for style mistakes and obvious bugs. `ruff format --check` compares the file layout with the formatter and changes nothing. `pyright` checks types. `pytest` runs the tests.

1. Enable strict type checking in `pyproject.toml` for Pyright (`typeCheckingMode = "strict"`) or Mypy (`strict = true`).
2. Review the Day 6 code and eliminate all typing warnings (missing `None`, `Any` types, `Optional` mismatches).
3. Run the full check pipeline:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```
