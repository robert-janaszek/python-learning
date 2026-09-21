## Dzień 1: Tooling i czysta składnia (`uv`, `Ruff`, comprehensions)

**Cel:** Konfiguracja środowiska w 2 minuty i opanowanie idiomu operacji na kolekcjach.

1. **Konfiguracja środowiska:**
* Zainstaluj `uv` (jeśli jeszcze nie masz): `curl -LsSf https://astral.sh/uv/install.sh | sh`
* Inicjalizacja projektu: `uv init python-week1 && cd python-week1`
* Dodaj Ruff: `uv add --dev ruff`
* Uruchom linter i formatter: `uv run ruff check .` oraz `uv run ruff format .`


2. **Zadanie kodowe:**
* Masz listę słowników reprezentujących logi zdarzeń: `[{"user_id": 1, "action": "login", "duration": 120}, ...]`.
* Napisz funkcję, która za pomocą **List/Dict Comprehension** (bez pętli `for` i bez `.map()`/`.filter()`):
* Przefiltruje tylko zdarzenia typu `"login"`.
* Zwróci słownik `{user_id: total_duration}` (uwzględniając przypadek, gdy użytkownik ma wiele logów – spróbuj użyć `collections.defaultdict`).





---

## Dzień 2: Dunder Methods, OOP i Context Manager

**Cel:** Zrozumienie, jak obiekty w Pythonie wchodzą w interakcję ze składnią języka.

1. **Zadanie kodowe – Magiczne metody:**
* Stwórz klasę `RateLimiter`, która przyjmuje `max_requests: int` oraz `window_seconds: int`.
* Zaimplementuj metodę `__call__(self, user_id: str) -> bool`, aby instancja klasy była wywoływalna jak funkcja (`limiter("user_123")`).
* Zaimplementuj `__repr__`, aby wywołanie `print(limiter)` dawało czytelny string debugowy: `RateLimiter(max_requests=10, window=60)`.


2. **Zadanie kodowe – Custom Context Manager:**
* Napisz klasę `Timer` używającą protokołu Context Managera (`__enter__` i `__exit__`).
* Użycie: `with Timer("DB Query"): ...` ma automatycznie zmierzyć czas wykonania bloku kodu i wydrukować go po wyjściu z bloku.



---

## Dzień 3: Typing i Pydantic v2 (Pythonowy "Zod")

**Cel:** Modele danych na granicy I/O z pełną walidacją i statycznym typowaniem.

1. **Przygotowanie:**
* Dodaj Pydantic i Pyright/Mypy: `uv add pydantic` oraz `uv add --dev pyright`


2. **Zadanie kodowe:**
* Stwórz model Pydantic `UserPayload`:
* `id`: `UUID`
* `email`: `EmailStr`
* `roles`: `list[Literal["admin", "user", "guest"]]`
* `created_at`: `datetime` (z automatyczną domyślną wartością strefy UTC)


* Dodaj `@field_validator` dla pola `roles`, który zgłosi błąd, jeśli lista jest pusta.
* Dodaj `@model_validator(mode="after")` wymuszający, że jeśli `email` kończy się na `@company.com`, użytkownik musi posiadać rolę `"admin"`.
* Przetestuj deserializację niepoprawnego JSON-a i obsłuż `ValidationError`.



---

## Dzień 4: Asynchroniczność w `asyncio`

**Cel:** Zrozumienie jawnej pętli zdarzeń i unikanie blokowania event loopa.

1. **Zadanie kodowe – Async Fetcher & Rate Limiting:**
* Napisz asynchroniczną funkcję `fetch_metrics(service_id: int) -> dict`, która symuluje zapytanie HTTP (`await asyncio.sleep(0.5)`).
* Wywołaj współbieżnie pobieranie danych dla 20 serwisów (`service_id` od 1 do 20) przy użyciu `asyncio.gather`.
* Nałóż limit maksymalnie 3 równoległych zapytań naraz, używając `asyncio.Semaphore`.
* **Pułapka do przetestowania:** Dodaj do jednej z funkcji synchroniczne `time.sleep(2)` i zobacz, jak blokuje cały event loop. Napraw to, przenosząc blokujące wywołanie do osobnego wątku za pomocą `asyncio.to_thread`.



---

## Dzień 5: TDD z `pytest` i Fixtures

**Cel:** Pisanie idiomaticznych testów z wykorzystaniem fixture'ów i parametryzacji.

1. **Przygotowanie:**
* Dodaj pytest: `uv add --dev pytest pytest-asyncio`


2. **Zadanie kodowe:**
* Zbuduj prosty klasowy serwis `UserService` z pamięcią podręczną (słownik).
* Napisz zestaw testów w `pytest`:
* Użyj `@pytest.fixture` do przygotowania czystej instancji `UserService` przed każdym testem.
* Użyj `@pytest.mark.parametrize` do przetestowania walidacji adresów e-mail na 5 różnych prawidłowych i nieprawidłowych ciągach znaków w jednym teście.
* Użyj `pytest.raises(ValueError)` do weryfikacji rzucanych wyjątków.





---

## Dzień 6: Mini-CLI w oparciu o wszystko, co powiązałeś

**Cel:** Połączenie narzędzi w spójny skrypt.

1. **Zadanie:**
* Stwórz narzędzie CLI, które przyjmuje ścieżkę do pliku JSON z listą użytkowników, waliduje każdy wpis przez Pydantic, asynchronicznie "przetwarza" ich (simulated I/O) i zapisuje zagregowane statystyki do nowego pliku.
* Całość powinna być w pełni otypowana, sformatowana przez `ruff` i mieć przechodzące testy w `pytest`.



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