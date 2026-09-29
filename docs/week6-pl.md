# Tydzień 6: Systemy Rozproszone, Asynchroniczne AI & Production Operations

W ostatnim tygodniu włączysz stworzone moduły AI do dojrzałej architektury systemowej z kolejkami, streamingiem SSE oraz pełnym monitoringiem.

---

## Dzień 36: Async AI Processing z ARQ

### 1. Wprowadzenie i Koncepty

Lokalne modele LLM są wolne i zasobożerne (generowanie odpowiedzi może trwać od kilku do kilkudziesięciu sekund). Takie zapytania nie powinny blokować handlera HTTP — łatwo przekraczają timeout klienta.

* Architektura oparta na zdarzeniach: HTTP POST wrzuca zadanie do ARQ → worker wykonuje je na lokalnym LLM → wynik ląduje w bazie. Klient dostaje od razu `task_id` i odczytuje wynik, gdy worker skończy.

### 2. Zadania na dzisiaj

1. Zintegruj stworzonego agenta z workerem ARQ (z Tygodnia 3).
2. Utwórz endpoint `POST /agent/tasks`, który przyjmuje trudne zadanie, natychmiast zwraca `task_id`, a agent wykonuje pracę w tle na lokalnym LLM.

---

## Dzień 37: SSE (Server-Sent Events) dla interfejsów AI

### 1. Wprowadzenie i Koncepty

Użytkownik nie chce czekać 20 sekund na pusty ekran. Chce widzieć myśli agenta i generowane tokeny w czasie rzeczywistym.

* **SSE (Server-Sent Events):** Jednokierunkowy protokół, którym w tym kursie streamujesz odpowiedź LLM do przeglądarki.
* **`StreamingResponse`:** wbudowana odpowiedź FastAPI/Starlette. W przykładzie generator zwraca ramki SSE (`data: ...\n\n`) z `media_type="text/event-stream"`.
* **`EventSourceResponse` (`sse-starlette`):** osobna biblioteka, nie część FastAPI. Wygodna, gdy chcesz nazwane zdarzenia (`event: tool_called`).

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def llm_token_generator():
    tokens = ["Cześć", "!", " Jestem", " Twoim", " agentem", " AI."]
    for token in tokens:
        await asyncio.sleep(0.2)
        yield f"data: {token}\n\n"

@app.get("/stream")
async def stream_ai_reply():
    return StreamingResponse(llm_token_generator(), media_type="text/event-stream")

```

### 2. Zadania na dzisiaj

1. Zainstaluj wsparcie dla SSE: `uv add sse-starlette`.
2. Stwórz endpoint w FastAPI (`EventSourceResponse` z `sse-starlette`), który przesyła w czasie rzeczywistym zarówno tokeny z lokalnego LLM, jak i statusy wywoływanych narzędzi (np. zdarzenie `tool_called` i dane `{"name": "search_db"}`).

---

## Dzień 38: Tracing i Observability dla AI (OpenTelemetry + Langfuse / Phoenix)

### 1. Wprowadzenie i Koncepty

W tradycyjnym backendzie śledzisz zapytania SQL. W aplikacjach AI musisz śledzić **dokładny prompt, zużyte tokeny, czas odpowiedzi LLM, wywołane narzędzia i pobrany kontekst RAG**.

* **Langfuse / Arize Phoenix:** Lokalne (self-hosted) lub chmurowe narzędzia do APM dla aplikacji AI oparte na OpenTelemetry.

### 2. Zadania na dzisiaj

1. Uruchom w Dockerze lokalną instancję Phoenixa lub Langfuse (`docker run -p 6006:6006 arizephoenix/phoenix`).
2. Podłącz OpenTelemetry w Pythonie pod klienta OpenAI / Instructor / LangGraph.
3. Wykonaj kilka zapytań do agenta i przejrzyj pełne drzewo wywołań (Trace Tree) w lokalnym panelu kontrolnym.

---

## Dzień 39: Parametry wywołania modelu z Pythona

### 1. Wprowadzenie i Koncepty

Serwer zostaje ten sam co w dniu 22 (Ollama albo LM Studio). Dziś sterujesz odpowiedzią z kodu, parametrami `chat.completions.create`.

* **`temperature`:** jak bardzo model może odejść od najbardziej prawdopodobnego tokenu. `0` trzyma się jednego toru, wyższa wartość rozrzuca odpowiedzi.
* **`top_p`:** zostawia tylko tokeny z górnej części rozkładu prawdopodobieństwa.
* **`max_tokens`:** limit tokenów w odpowiedzi.

```python
response = await client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
    top_p=0.9,
    max_tokens=512,
)
```

### 2. Zadania na dzisiaj

1. Wywołaj ten sam prompt trzy razy, z `temperature` równą `0`, `0.7` i `1.2`, i porównaj odpowiedzi.
2. Ustaw `max_tokens` tak, żeby odpowiedź urwała się w połowie zdania, potem podnieś limit i zobacz pełną odpowiedź.

---

## Dzień 40: System Design – End-to-End Enterprise AI Service

### 1. Wprowadzenie i Koncepty

Zaprojektowanie i połączenie wszystkich zdobytych umiejętności w jeden kompletny, skalowalny system rozproszony.

### 2. Zadania na dzisiaj

1. Zaprojektuj i zaimplementuj końcowy system backendowy w Pythonie:
* **FastAPI** jako bramka API z walidacją Pydantic v2.
* **SSE** do streamingu odpowiedzi do klienta.
* **ARQ + Redis** do asynchronicznych zadań AI w tle.
* **SQLite (`app.db`) + SQLAlchemy 2.0** do użytkowników i historii rozmów. Ta sama baza co w Tygodniu 2.
* **LanceDB** jako wbudowana baza wektorowa do RAG.
* **Lokalny LLM** z interfejsem OpenAI do napędzania Agenta i RAG-a.
* **Structlog + OpenTelemetry** dla monitoringu całego systemu.



---

## Dzień 41: Multi-stage Docker Build dla aplikacji AI/Python

### 1. Wprowadzenie i Koncepty

Tworzenie obrazów kontenerowych dla aplikacji AI wymaga dbałości o rozmiar i bezpieczeństwo (brak zbędnych bibliotek kompilacyjnych na produkcji).

### 2. Zadania na dzisiaj

1. Zbuduj wieloetapowy `Dockerfile` z użyciem `uv`, który instaluje tylko zależności produkcyjne.
2. Zbuduj plik `docker-compose.yml`, który jednym poleceniem (`docker compose up`) stawia API, Redis, workera i tracing. SQLite (`app.db`) i LanceDB to pliki aplikacji, nie osobne kontenery.

---

## Dzień 42: Podsumowanie i Code Review całej ścieżki

### 1. Zadanie

Uruchom pełny zestaw kontroli na kodzie z 6 tygodni. Każde polecenie ma zakończyć się kodem 0: zero zgłoszeń Ruffa, zero błędów typów, zero niezdanych testów.

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest

```

Gratulacje! Przeszedłeś pełną ścieżkę: od zrozumienia idiomu języka Python, przez asynchroniczny backend (FastAPI/SQLAlchemy), aż po budowę zaawansowanych, bezpiecznych systemów agentowych i RAG z wykorzystaniem lokalnych modeli AI na poziomie produkcyjnym.
