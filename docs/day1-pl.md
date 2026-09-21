## Dzień 1: Tooling i czysta składnia (`uv`, `Ruff`, comprehensions)

**Cel:** Konfiguracja środowiska w 2 minuty i opanowanie idiomu operacji na kolekcjach.

1. **Konfiguracja środowiska:**

- Zainstaluj `uv` (jeśli jeszcze nie masz): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Inicjalizacja projektu: `uv init python-week1 && cd python-week1`
- Dodaj Ruff: `uv add --dev ruff`
- Uruchom linter i formatter: `uv run ruff check .` oraz `uv run ruff format .`
- Uruchom kod: `uv run python-week1` (z katalogu `python-week1`). To woła `python_week1:main` z `pyproject.toml`. `uv run` używa lokalnego `.venv`, nie musisz go aktywować ręcznie.
- `uv run python -m python_week1` nic nie wykona, dopóki w pakiecie nie ma `__main__.py`, a `main()` nie jest wołane przy imporcie.

1. **Zadanie kodowe — logi zdarzeń:**

Dane to lista **słowników**, nie obiektów. Pole czytasz kluczem: `log["action"]`, **nie** `log.action`.

W `main()` trzymaj jedną listę i wołaj z niej trzy funkcje (`print` każdej). Nie używaj `.map()` / `.filter()`.

```
logs = [
    {"user_id": 1, "action": "login", "duration": 120},
    {"user_id": 2, "action": "login", "duration": 110},
    {"user_id": 1, "action": "logout", "duration": 90},
    {"user_id": 1, "action": "login", "duration": 30},
]
```

`for` wewnątrz `[...]` albo `{...}` to składnia comprehension — tak ma być. Klasycznej pętli:

```python
result = []
for x in items:
    ...
```

użyj **tylko** w zadaniu 2c.

**2a. List comprehension — filtr + mapa**

Składnia: `[wyrażenie for element in kolekcja if warunek]`.

Mini-przykład: `[n * 2 for n in [1, 2, 3, 4] if n % 2 == 0]` → `[4, 8]`.

Napisz `login_durations(logs: list[dict]) -> list[int]`: lista `duration` tylko dla `"login"`.

Oczekiwany wynik: `[120, 110, 30]`.

**2b. Dict comprehension — ostatnia wartość wygrywa**

Składnia: `{klucz: wartość for element in kolekcja if warunek}`.

Mini-przykład: `{n: n * n for n in [1, 2, 3]}` → `{1: 1, 2: 4, 3: 9}`.

Napisz `last_login_duration(logs: list[dict]) -> dict[int, int]`: `user_id → duration` **ostatniego** loginu. Przy powtórzonym kluczu dict **nadpisuje** poprzednią wartość — o to tu chodzi. Comprehensionem **nie** sumujesz.

Oczekiwany wynik: `{1: 30, 2: 110}`.

**2c.** `defaultdict` **— suma po kluczu**

Sumowanie to nie zadanie na comprehension. Napisz `total_login_duration(logs: list[dict]) -> dict[int, int]` z `collections.defaultdict(int)` i pętlą `for`:

- `totals = defaultdict(int)` — brakujący klucz to `0`
- dla każdego loginu: `totals[user_id] += duration`

Możesz najpierw wziąć wynik z 2a albo filtrować w pętli. Zwróć `dict(totals)` albo sam `defaultdict`.

Oczekiwany wynik: `{1: 150, 2: 110}`.

---



## Dzień 2: Dunder Methods, OOP i Context Manager

**Cel:** Zrozumienie, jak obiekty w Pythonie wchodzą w interakcję ze składnią języka.

1. **Zadanie kodowe – Magiczne metody:**

- Stwórz klasę `RateLimiter`, która przyjmuje `max_requests: int` oraz `window_seconds: int`.
- Zaimplementuj metodę `__call__(self, user_id: str) -> bool`, aby instancja klasy była wywoływalna jak funkcja (`limiter("user_123")`).
- Zaimplementuj `__repr__`, aby wywołanie `print(limiter)` dawało czytelny string debugowy: `RateLimiter(max_requests=10, window=60)`.

1. **Zadanie kodowe – Custom Context Manager:**

- Napisz klasę `Timer` używającą protokołu Context Managera (`__enter__` i `__exit__`).
- Użycie: `with Timer("DB Query"): ...` ma automatycznie zmierzyć czas wykonania bloku kodu i wydrukować go po wyjściu z bloku.

---



## Dzień 3: Typing i Pydantic v2 (Pythonowy "Zod")

**Cel:** Modele danych na granicy I/O z pełną walidacją i statycznym typowaniem.

1. **Przygotowanie:**

- Dodaj Pydantic i Pyright/Mypy: `uv add pydantic` oraz `uv add --dev pyright`

1. **Zadanie kodowe:**

- Stwórz model Pydantic `UserPayload`:
- `id`: `UUID`
- `email`: `EmailStr`
- `roles`: `list[Literal["admin", "user", "guest"]]`
- `created_at`: `datetime` (z automatyczną domyślną wartością strefy UTC)
- Dodaj `@field_validator` dla pola `roles`, który zgłosi błąd, jeśli lista jest pusta.
- Dodaj `@model_validator(mode="after")` wymuszający, że jeśli `email` kończy się na `@company.com`, użytkownik musi posiadać rolę `"admin"`.
- Przetestuj deserializację niepoprawnego JSON-a i obsłuż `ValidationError`.

---



## Dzień 4: Asynchroniczność w `asyncio`

**Cel:** Zrozumienie jawnej pętli zdarzeń i unikanie blokowania event loopa.

1. **Zadanie kodowe – Async Fetcher & Rate Limiting:**

- Napisz asynchroniczną funkcję `fetch_metrics(service_id: int) -> dict`, która symuluje zapytanie HTTP (`await asyncio.sleep(0.5)`).
- Wywołaj współbieżnie pobieranie danych dla 20 serwisów (`service_id` od 1 do 20) przy użyciu `asyncio.gather`.
- Nałóż limit maksymalnie 3 równoległych zapytań naraz, używając `asyncio.Semaphore`.
- **Pułapka do przetestowania:** Dodaj do jednej z funkcji synchroniczne `time.sleep(2)` i zobacz, jak blokuje cały event loop. Napraw to, przenosząc blokujące wywołanie do osobnego wątku za pomocą `asyncio.to_thread`.

---



## Dzień 5: TDD z `pytest` i Fixtures

**Cel:** Pisanie idiomaticznych testów z wykorzystaniem fixture'ów i parametryzacji.

1. **Przygotowanie:**

- Dodaj pytest: `uv add --dev pytest pytest-asyncio`

1. **Zadanie kodowe:**

- Zbuduj prosty klasowy serwis `UserService` z pamięcią podręczną (słownik).
- Napisz zestaw testów w `pytest`:
- Użyj `@pytest.fixture` do przygotowania czystej instancji `UserService` przed każdym testem.
- Użyj `@pytest.mark.parametrize` do przetestowania walidacji adresów e-mail na 5 różnych prawidłowych i nieprawidłowych ciągach znaków w jednym teście.
- Użyj `pytest.raises(ValueError)` do weryfikacji rzucanych wyjątków.

---



## Dzień 6: Mini-CLI w oparciu o wszystko, co powiązałeś

**Cel:** Połączenie narzędzi w spójny skrypt.

1. **Zadanie:**

- Stwórz narzędzie CLI, które przyjmuje ścieżkę do pliku JSON z listą użytkowników, waliduje każdy wpis przez Pydantic, asynchronicznie "przetwarza" ich (simulated I/O) i zapisuje zagregowane statystyki do nowego pliku.
- Całość powinna być w pełni otypowana, sformatowana przez `ruff` i mieć przechodzące testy w `pytest`.

---



## Dzień 7: Code Review i Pyright Strict Mode

**Cel:** Weryfikacja jakości kodu według standardów produkcyjnych.

1. Włącz w `pyproject.toml` ścisłą kontrolę typów dla Pyright (`typeCheckingMode = "strict"`) lub Mypy (`strict = true`).
2. Przejrzyj kod z Dnia 6 i wyeliminuj wszystkie ostrzeżenia typowania (brakujące `None`, typy `Any`, niezgodności z `Optional`).
3. Uruchom pełny ciąg kontroli:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest

```

