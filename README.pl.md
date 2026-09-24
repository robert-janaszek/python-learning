# python-learning

[English](README.md)

Prywatny kurs Pythona dla osób, które już programują w TypeScript. Repo prowadzi tydzień po tygodniu: każdego dnia czytasz krótkie notatki o idiomatycznym wzorcu, a potem sam wykonujesz zadania. Notatki są po polsku i po angielsku.

## Jak zacząć

W repozytorium leży gotowy kod rozwiązań. Zanim ruszysz z zadaniami, schowaj go — zmień nazwę pliku albo rozszerzenie, na przykład:

```text
rate_limiter.py  →  rate_limiter.py.solution
```

Python przestaje ten plik importować, więc piszesz własną wersję od zera. Stary plik zostaje obok jako ściąga: otwierasz go dopiero wtedy, gdy utkniesz.

Dotyczy to modułów w `python-week1/src/python_week1/` (implementacja i testy). Zostaw `pyproject.toml`, `uv.lock` i pliki danych (`users.json`).

Potem idź dzień po dniu. Teoria jest na początku dnia, zadania na końcu.

- Tydzień 1: [docs/week1-pl.md](docs/week1-pl.md) · [docs/week1-en.md](docs/week1-en.md)
- Tydzień 2: [docs/week2-pl.md](docs/week2-pl.md) · [docs/week2-en.md](docs/week2-en.md)

## Wymagania

- Python 3.14 (`python-week1/.python-version`)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

Z katalogu `python-week1`:

```bash
uv sync
uv run python-week1
```

`uv run` używa lokalnego `.venv`. Osobna aktywacja środowiska nie jest potrzebna.

## Jak pracować

1. Przeczytaj notatki jednego dnia.
2. Zrób zadania z końca tego dnia we własnych plikach.
3. Uruchom kod i sprawdzenia podane w notatkach.
4. Do plików `*.solution` zajrzyj dopiero, gdy utkniesz.

Tam, gdzie pomaga porównanie ze światem TypeScript, notatki je podają. Celem jest wzorzec używany w Pythonie, a nie tłumaczenie składni jeden do jednego.

## Tydzień 1 — język i narzędzia

Projekt: `python-week1/`.

| Dzień | Temat |
| --- | --- |
| 1 | Tooling i semantyka: `uv`, Ruff, `dict`, `for`, comprehensions |
| 2 | Dunder methods, OOP, context manager |
| 3 | Typing i Pydantic v2 |
| 4 | Asynchroniczność w `asyncio` |
| 5 | TDD z `pytest` i fixtures |
| 6 | Mini-CLI spinające poprzednie dni |
| 7 | Code review i Pyright w trybie strict |

Pełna kontrola z katalogu `python-week1` (dzień 7):

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

## Tydzień 2 — API, baza, testy

Budujesz REST API (mini-Jira): FastAPI, SQLAlchemy 2.0, Alembic, testy integracyjne i Docker. Projekt stawiasz w dniu 8, według notatek.

| Dzień | Temat |
| --- | --- |
| 8 | Konfiguracja projektu i DTO w Pydantic v2 |
| 9 | Modele ORM i warstwa bazy (SQLAlchemy 2.0) |
| 10 | Migracje (Alembic) |
| 11 | Endpointy FastAPI |
| 12 | Testy integracyjne (`pytest` + `AsyncClient`) |
| 13 | Błędy, middleware, logi |
| 14 | Docker i przegląd architektury |
