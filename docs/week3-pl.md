# Tydzień 3: Observability, Architektura Aplikacji i Procesy Tła

W tym tygodniu skupiamy się na rozwiązaniach używanych w skali produkcyjnej: komunikacji międzysystemowej, asynchronicznym przetwarzaniu zadań w tle (kolejki), strukturyzowanym logowaniu oraz czystej architekturze warstwowej w Pythonie.

---

## Dzień 15: Struktura projektu i Czysta Architektura (Service Layer & Repository Pattern)

### 1. Wprowadzenie i Koncepty

Mieszanie logiki bazodanowej (SQLAlchemy) bezpośrednio w endpointach FastAPI utrudnia testowanie i utrzymanie kodu. Zamiast tego stosuje się wzorce **Repository** (odizolowanie dostępu do danych) oraz **Service Layer** (odizolowanie logiki biznesowej).

* **Repository Pattern:** Klasa opakowująca zapytania ORM. Zamiast pisać `select(UserModel)` w endpoincie, wywołujesz `user_repo.get_by_id(user_id)`.
* **Service Layer:** Przechowuje reguły biznesowe, steruje transakcjami bazy danych (`commit`/`rollback`) oraz wywołuje zewnętrzne serwisy.

#### Przykład:

```python
from typing import Protocol
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import UserModel

# Protokół (interfejs ala TS)
class UserRepositoryProtocol(Protocol):
    async def get_by_email(self, email: str) -> UserModel | None: ...

# Konkretna implementacja ORM
class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

# Service Layer
class UserService:
    def __init__(self, repo: UserRepositoryProtocol):
        self.repo = repo

    async def register_user(self, email: str) -> UserModel:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError("User already exists")
        # logika tworzenia użytkownika...

```

### 2. Zadania na dzisiaj

1. Zrefaktoryzuj aplikację powstałą w Tygodniu 2 (Mini-Jira):
* Stwórz klasę `ProjectRepository` oraz `TaskRepository` w osobnych plikach.
* Stwórz klasy `ProjectService` oraz `TaskService`, w których umieścisz całą logikę biznesową.


2. Odchudź endpointy w `FastAPI` tak, aby odpowiadały wyłącznie za deserializację requestu, przekazanie danych do serwisu i zwrócenie response'a.

---

## Dzień 16: Zaawansowane logowanie i śledzenie (Structlog)

### 1. Wprowadzenie i Koncepty

Standardowy moduł `logging` w Pythonie tworzy jednolinijkowe teksty, które trudno parsuje się w systemach takich jak Datadog, Kibana czy Grafana Loki. Standardem produkcyjnym jest **Structlog** – biblioteka generująca logi w formacie JSON z kontekstem (np. `request_id`, `user_id`).

* **Contextvars:** Moduł Pythona pozwalający na przechowywanie zmiennych wątku/kontekstu asynchronicznego (odpowiednik `AsyncLocalStorage` w Node.js). Używany do przekazywania `correlation_id` przez całe żądanie.

#### Przykład:

```python
import structlog

# Konfiguracja bazowa Structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars, # Scalanie kontekstu asynchronicznego
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()      # Format JSON dla produkcji
    ]
)

logger = structlog.get_logger()

# Użycie
async def process_order(order_id: str):
    # Dopisanie kontekstu do bieżącego kontekstu wykonania
    structlog.contextvars.bind_contextvars(order_id=order_id)
    
    logger.info("order_processing_started", amount=150.00)
    # Log wynikowy: {"event": "order_processing_started", "amount": 150.0, "order_id": "123", "level": "info", "timestamp": "..."}

```

### 2. Zadania na dzisiaj

1. Zainstaluj `structlog`: `uv add structlog`.
2. Skonfiguruj `structlog` w swoim projekcie tak, aby logował w formacie JSON.
3. Stwórz middleware w FastAPI, który generuje unikalny `X-Request-ID` (UUID) dla każdego żądania, przypisuje go do `structlog.contextvars` i dołącza do nagłówka odpowiedzi.
4. Zastąp wszystkie zwykłe wywołania `print` lub `logging` w serwisach wywołaniami `logger.info()` / `logger.error()`.

---

## Dzień 17: Celery & Redis – Kolejki zadań w tle (Task Queues)

### 1. Wprowadzenie i Koncepty

Niektóre operacje (wysyłka e-maili, generowanie raportów PDF, przetwarzanie obrazów) trwają zbyt długo, by wykonywać je synchronicznie w żądaniu HTTP. W ekosystemie Pythona standardowym narzędziem do delegowania zadań w tle jest **Celery** z brokerem **Redis** lub **RabbitMQ**.

* **Broker:** Przechowuje kolejkowane zadania (np. Redis).
* **Worker:** Osobny proces Pythona, który pobiera zadania z brokera i je wykonuje.
* **Celery Task:** Zwykła funkcja udekorowana przez `@app.task`, wywoływana za pomocą `.delay()`.

#### Przykład:

```python
# tasks.py
from celery import Celery

celery_app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery_app.task
def send_welcome_email(email: str) -> None:
    # Ciężka operacja I/O / SMTP
    print(f"Sending email to {email}...")

# main.py (FastAPI Endpoint)
@app.post("/register")
def register(email: str):
    # Wywołanie asynchroniczne - funkcja WRACA NATYCHMIAST, zadanie ląduje w Redisie
    send_welcome_email.delay(email)
    return {"message": "Registration successful, email queued"}

```

### 2. Zadania na dzisiaj

1. Dodaj Celery i Redis: `uv add celery redis`.
2. Stwórz plik `worker.py` i skonfiguruj instancję Celery.
3. Napisz zadanie Celery `generate_project_report(project_id: int)`, które symuluje długa pracę (np. `time.sleep(5)`) i zapisuje wynik w pliku lub konsoli.
4. Wywołaj to zadanie w endpoincie FastAPI `POST /projects/{id}/report` przy użyciu `.delay()`. Upewnij się, że odpowiedź z HTTP wraca od razu (status 202 Accepted).

---

## Dzień 18: ARQ – Modern Async Task Queue (Alternatywa dla Celery)

### 1. Wprowadzenie i Koncepty

Celery wywodzi się z czasów Pythona 2 i jest w pełni synchroniczne wewnątrz workerów (używa wątków/procesów). **ARQ** to nowoczesna, w pełni asynchroniczna (`asyncio`) biblioteka do kolejkowania zadań oparta na Redisie, idealnie pasująca do FastAPI.

* Lekka, bardzo szybka, w pełni wspiera `async/await`.
* Natywna integracja z typowaniem Pythona.

#### Przykład:

```python
# worker.py
from arq import create_pool
from arq.connections import RedisSettings

async def download_file(ctx: dict, url: str) -> int:
    # ctx zawiera m.in. połaczenie do bazy lub sesję HTTP podpiętą w startupie
    print(f"Downloading {url}")
    return 200

class WorkerSettings:
    functions = [download_file]
    redis_settings = RedisSettings(host="localhost", port=6379)

# W FastAPI
async def trigger_download(request: Request, url: str):
    redis = request.app.state.arq_redis
    await redis.enqueue_job("download_file", url)
    return {"status": "queued"}

```

### 2. Zadania na dzisiaj

1. Zainstaluj ARQ: `uv add arq`.
2. Stwórz prosty worker ARQ wykonujący asynchroniczne zadanie I/O (np. zapytanie do zewnętrznego API via `httpx`).
3. Zintegruj pulę połączeń ARQ z aplikacją FastAPI (używając zdarzeń `lifespan` w FastAPI do otwarcia/zamknięcia połączenia z Redisem).
4. Porównaj składnię i prostotę ARQ z Celery z poprzedniego dnia.

---

## Dzień 19: Caching z Redisem i Dekoratory

### 1. Wprowadzenie i Koncepty

Aby uniknąć ciągłego odpytywania bazy danych o te same, rzadko zmieniające się dane, stosuje się warstwę cache (Redis). W Pythonie często tworzy się **własne dekoratory** do przezroczystego keszowania wyników funkcji.

* **Wykorzystanie `@wraps` z `functools`:** Wymagane przy pisaniu dekoratorów w Pythonie, aby zachować nazwy funkcji, docstringi i typowanie.

#### Przykład:

```python
import json
from functools import wraps
from redis.asyncio import Redis

redis_client = Redis(host="localhost", port=6379)

def cache_json(ttl_seconds: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generowanie klucza na podstawie argumentów
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached_data = await redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            # Wywołanie oryginalnej funkcji
            result = await func(*args, **kwargs)
            
            await redis_client.setex(cache_key, ttl_seconds, json.dumps(result))
            return result
        return wrapper
    return decorator

```

### 2. Zadania na dzisiaj

1. Zaimplementuj powyższy dekorator keszujący `cache_json` dla asynchronicznych funkcji.
2. Nałóż go na metodę `get_project_by_id` w swoim `ProjectService`.
3. Dodaj mechanizm unieważniania cache'u (Cache Invalidation): przy edycji lub usunięciu projektu (`UPDATE`/`DELETE`), skasuj odpowiedni klucz z Redisa.

---

## Dzień 20: Profilowanie i wydajność (cProfile, memory_profiler, Py-Spy)

### 1. Wprowadzenie i Koncepty

Przed wdrożeniem produkcyjnym musisz umieć zidentyfikować wąskie gardła (obciążenie CPU, wycieki pamięci, nieoptymalne pętle).

* **`cProfile`:** Wbudowany w Pythona profiler deterministyczny (mierzy czas wykonania każdej funkcji).
* **`py-spy`:** Profiler próbkowujący (sampling profiler) działający poza procesem Pythona. Bezpieczny do uruchamiania na produkcji, generuje wykresy typu **Flamegraph**.

#### Przykład uruchomienia Py-Spy z CLI:

```bash
# Wygenerowanie wykresu Flamegraph z działającego procesu Pythona
uv run py-spy record -o profile.svg --pid <PID_PROCESU_PYTHON>

# Profilowanie skryptu z poziomu CLI
uv run py-spy top -- uv run main.py

```

### 2. Zadania na dzisiaj

1. Zainstaluj `py-spy`: `uv add --dev py-spy`.
2. Stwórz skrypt `benchmark.py`, który wykonuje niewydajną operację (np. przetwarzanie dużej listy w pętli `for` z wielokrotnym łączeniem stringów zamiast użycia `join`).
3. Przeprowadź profilowanie skryptu za pomocą `py-spy` i wygeneruj plik `flamegraph.svg`. Otwórz go w przeglądarce i zidentyfikuj najwolniejszą funkcję.
4. Zoptymalizuj kod i porównaj czasy przed i po zmianach.

---

## Dzień 21: Projekty produkcyjne i przygotowanie do Code Review

### 1. Wprowadzenie i Koncepty

Ostatnim krokiem jest związanie architektury, logowania, zadań w tle i testów w jeden spójny system produkcyjny gotowy do przeglądu kodu.

### 2. Zadania na dzisiaj (Synteza)

Połącz wszystkie elementy zbudowane w tym tygodniu w jeden spójny microservice:

1. Skonfiguruj `docker-compose.yml`, który podnosi:
* Aplikację FastAPI
* Bazę danych PostgreSQL
* Instancję Redis
* Worker ARQ / Celery


2. Upewnij się, że start aplikacji automatycznie wykonuje migracje Alembic (`alembic upgrade head`).
3. Przeprowadź pełną weryfikację jakościową:
```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest --maxfail=1

```
