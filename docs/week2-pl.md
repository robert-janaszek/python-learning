# Tydzień 2: Async Architecture, Web API (FastAPI) i Dostęp do Baz Danych (SQLAlchemy 2.0)

W tym tygodniu przechodzimy od czystego języka do budowania produkcyjnych serwisów backendowych. Zamiast szukać informacji po dokumentacjach, poniżej znajdziesz kompletne wprowadzenie teoretyczne wraz z kodem dla każdego kluczowego konceptu.

---

## 1. Wprowadzenie i Koncepty

### A. FastAPI i Architektura ASGI

W świecie JS/TS odpowiednikiem FastAPI jest NestJS lub Express, ale FastAPI bazuje na standardzie **ASGI** (Asynchronous Server Gateway Interface) – odpowiedniku WSGI dla kodu asynchronicznego.

* **Pydantic jako warstwa I/O:** FastAPI automatycznie waliduje requesty i response'y używając modeli Pydantic. Generuje też gotową dokumentację OpenAPI (`/docs`).
* **Dependency Injection (DI):** Posiada wbudowany kontener wstrzykiwania zależności (`Depends`), służący do zarządzania sesjami bazy danych, autoryzacją czy konfiguracją.

```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

app = FastAPI()

# Model I/O (DTO)
class UserCreate(BaseModel):
    email: EmailStr
    age: int

# Zależność (Dependency Injection)
def get_db_session():
    db = {"connected": True}
    try:
        yield db
    finally:
        # Cleanup (odpowiednik połączenia z bazą)
        db["connected"] = False

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: dict = Depends(get_db_session)):
    if payload.age < 18:
        raise HTTPException(status_code=400, detail="User must be adult")
    return {"status": "created", "email": payload.email}

```

---

### B. SQLAlchemy 2.0 (Modern Async ORM)

W Pythonie SQLAlchemy jest standardem rynkowym (jak Prisma czy TypeORM w TS). Version 2.0 wprowadziła w pełni asynchroniczny interfejs i jawne typowanie.

* **`DeclarativeBase`:** Klasa bazowa dla encji (odpowiednik `@Entity()` w TypeORM).
* **`Mapped` i `mapped_column`:** Nowoczesny zapis typów pól wspierany przez static type checkery.
* **`AsyncSession`:** Asynchroniczna sesja do wykonywania zapytań przy użyciu jawnego `select()`.

```python
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# 1. Klasa bazowa
class Base(AsyncAttrs, DeclarativeBase):
    pass

# 2. Model encji
class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)

# 3. Setup połączenia (SQLite in-memory dla przykładu)
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# 4. Przykładowe zapytanie (Syntax 2.0)
async def get_user_by_email(session: AsyncSession, email: str) -> UserModel | None:
    stmt = select(UserModel).where(UserModel.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

```

---

### C. Migracje Bazodanowe z Alembic

Alembic to narzędzie towarzyszące SQLAlchemy (odpowiednik `prisma migrate` lub `typeorm migration`).

* Przechowuje stan bazy w tabeli `alembic_version`.
* Potrafi automatycznie wykrywać zmiany w strukturze klas `DeclarativeBase` i generować skrypty migracyjne (`autogenerate`).

---

### D. Integration Testing w `pytest` z `httpx`

Do testowania asynchronicznych punktów końcowych FastAPI używamy `AsyncClient` z biblioteki `httpx` połączonego z fixture'ami `pytest`.

```python
import pytest
from httpx import AsyncClient, ASGITransport
from my_app import app  # Przykładowy import aplikacji FastAPI

@pytest.fixture
async def async_client():
    # ASGITransport pozwala testować aplikację w pamięci bez stawiania serwera HTTP
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    response = await async_client.post("/users", json={"email": "dev@test.com", "age": 25})
    assert response.status_code == 201
    assert response.json()["email"] == "dev@test.com"

```

---

## 2. Plan Zadań na Tydzień 2

Celem tego tygodnia jest zbudowanie w pełni przetestowanego REST API do zarządzania projektami i zadaniami (Mini-Jira) z asynchroniczną bazą danych.

### Dzień 8: Konfiguracja projektu i DTO z Pydantic v2

* **Zadanie:**
1. Zainicjalizuj projekt: `uv init python-week2 && cd python-week2`
2. Dodaj Pyright: `uv add --dev pyright` i w `pyproject.toml` włącz tryb strict:

```toml
[tool.pyright]
typeCheckingMode = "strict"
```

3. Zainstaluj w projekcie potrzebne pakiety za pomocą `uv`:
`uv add fastapi uvicorn sqlalchemy aiosqlite alembic httpx pytest-asyncio`
4. Zdefiniuj strukturę plików projektu:
```text
src/
  ├── database.py
  ├── models.py
  ├── schemas.py
  ├── main.py
tests/
  └── test_api.py

```


5. W `schemas.py` stwórz modele Pydantic dla encji `Project` oraz `Task`:
* `ProjectCreate` (`name: str`, `description: str | None`)
* `ProjectResponse` (`id: int`, `name: str`, `created_at: datetime`)
* `TaskCreate` (`title: str`, `priority: Literal["low", "medium", "high"]`)
* `TaskResponse` (`id: int`, `title: str`, `is_completed: bool`, `project_id: int`)





---

### Dzień 9: Modele ORM i warstwa bazy danych (SQLAlchemy 2.0)

* **Zadanie:**
1. W `models.py` utwórz modele SQLAlchemy dla tabel `projects` i `tasks`.
2. Zaimplementuj relację One-to-Many między `ProjectModel` a `TaskModel` używając `relationship()` oraz `ForeignKey`.
3. W `database.py` przygotuj asynchroniczny `engine`, `async_sessionmaker` oraz funkcję zależną `get_db()`, która używa generatora asynchronicznego (`yield`) do przekazywania sesji i zamykania jej po obsłudze żądania.



---

### Dzień 10: Inicjalizacja Migracji (Alembic)

* **Zadanie:**
1. Zinicjalizuj Alembic w projekcie: `uv run alembic init -t async alembic`
2. Skonfiguruj `alembic/env.py`, podłączając `target_metadata = Base.metadata` z Twoich modeli.
3. Wygeneruj pierwszą automatyczną migrację:
`uv run alembic revision --autogenerate -m "Initial tables"`
4. Uruchom migrację: `uv run alembic upgrade head`.



---

### Dzień 11: Endpoints API w FastAPI

* **Zadanie:**
W `main.py` stwórz następujące punkty końcowe:
* `POST /projects/` – Tworzenie nowego projektu.
* `GET /projects/` – Pobieranie listy projektów wraz z liczbą przypisanych zadań.
* `POST /projects/{project_id}/tasks/` – Tworzenie zadania przypisanego do danego projektu (zwróć `HTTP 404`, jeśli projekt nie istnieje).
* `PATCH /tasks/{task_id}/complete` – Oznaczenie zadania jako zakończonego.



---

### Dzień 12: Testy Integracyjne (pytest + AsyncClient)

* **Zadanie:**
1. Skonfiguruj `conftest.py` w katalogu `tests/`. Stwórz fixture dla asynchronicznej sesji bazodanowej działającej na bazie SQLite w pamięci (`sqlite+aiosqlite:///:memory:`).
2. Nadpisz zależność `get_db` w FastAPI w czasie testów przy użyciu `app.dependency_overrides`.
3. Napisz pełne testy integracyjne dla:
* Tworzenia projektu i weryfikacji statusu 201.
* Próby dodania zadania do nieistniejącego projektu (sprawdzenie statusu 404).
* Odczytu listy projektów.





---

### Dzień 13: Handling błędów, Middleware i Strukturacja Logów

* **Zadanie:**
1. Stwórz własny wyjątek w Pythonie `DomainException` i zarejestruj dla niego `exception_handler` w FastAPI, aby zwracał ujednoliconą strukturę błędu JSON (`{"error": "message", "code": "CUSTOM_CODE"}`).
2. Dodaj proste middleware mierzące czas wykonania każdego requestu HTTP i dodające nagłówek `X-Process-Time` do odpowiedzi.



---

### Dzień 14: Dockerization i przegląd architektury

* **Zadanie:**
1. Przygotuj optymalny, wieloetapowy plik `Dockerfile` dla aplikacji z wykorzystaniem `uv`:
* Stage 1 (Builder): Przygotowanie środowiska i instalacja zależności.
* Stage 2 (Runner): Kopiowanie tylko gotowego środowiska venv i kodu aplikacji, uruchomienie jako nie-root user.


2. Uruchom kontener i przetestuj ręcznie dokumentację pod adresem `http://localhost:8000/docs`.