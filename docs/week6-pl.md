# Tydzień 6: Systemy Rozproszone, Asynchroniczne AI & Production Operations

W ostatnim tygodniu włączysz stworzone moduły AI do dojrzałej architektury systemowej z kolejkami, streamingiem SSE oraz pełnym monitoringiem. Dalej pracujesz w katalogu `mini-jira` z Tygodnia 2.

---

## Dzień 36: Async AI Processing z ARQ

### 1. Wprowadzenie i Koncepty

Lokalne modele LLM są wolne i zasobożerne (generowanie odpowiedzi może trwać od kilku do kilkudziesięciu sekund). Takie zapytania nie powinny blokować handlera HTTP — łatwo przekraczają timeout klienta.

* Architektura oparta na zdarzeniach: HTTP POST wrzuca zadanie do ARQ → worker wykonuje je na lokalnym LLM → wynik ląduje w bazie. Klient dostaje od razu `task_id` i odczytuje wynik, gdy worker skończy.

### 2. Zadania na dzisiaj

1. Worker ARQ z tygodnia 3 wykonuje pętlę agenta z dnia 30.
2. `POST /agent/tasks`, body `{"session_id": str, "message": str}`, odpowiedź od razu `{"task_id": str}` ze statusem 202. Wiersz ląduje w nowej tabeli `agent_jobs` (`id`, `session_id`, `message`, `status`, `answer`). Status na starcie: `pending`.
3. `GET /agent/tasks/{task_id}` zwraca `{"status": "pending" | "done" | "failed", "answer": str | null}`. Dla wiadomości „ile otwartych zadań high ma projekt Backend” po chwili `status` to `done`, a `answer` mówi o dwóch.

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
2. `GET /agent/stream` z query `session_id` i `message`, odpowiedź przez `EventSourceResponse`. To ta sama pętla agenta, wołana w tym żądaniu. Zdarzenia:

   * `token` — kolejny kawałek tekstu odpowiedzi
   * `tool_called` — `{"name": "<nazwa funkcji>"}` w momencie wywołania narzędzia, na przykład `find_project`
   * `done` — koniec

   Dla wiadomości o projekcie Backend w strumieniu ma pojawić się `tool_called`, zanim przyjdą tokeny końcowej liczby.

---

## Dzień 38: Tracing i Observability dla AI (OpenTelemetry + Langfuse / Phoenix)

### 1. Wprowadzenie i Koncepty

W tradycyjnym backendzie śledzisz zapytania SQL. W aplikacjach AI musisz śledzić **dokładny prompt, zużyte tokeny, czas odpowiedzi LLM, wywołane narzędzia i pobrany kontekst RAG**.

* **Langfuse / Arize Phoenix:** Lokalne (self-hosted) lub chmurowe narzędzia do APM dla aplikacji AI oparte na OpenTelemetry.

### 2. Zadania na dzisiaj

1. Uruchom Phoenixa: `docker run -p 6006:6006 arizephoenix/phoenix`. Panel: http://localhost:6006.
2. Oprzyrządowanie klienta OpenAI z dnia 22: każde `chat.completions.create` i `embeddings.create` jest spanem. Wywołanie narzędzia agenta to span potomny z nazwą funkcji. Instructor i graf z dnia 32 używają tego samego klienta, więc wpadają w te spany.
3. Jedno `POST /qa` o priorytet i jedno polecenie agenta o projekcie Backend. W panelu widać prompt, nazwę narzędzia i fragment z `help.txt`.

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

1. Złóż to, co już jest w `mini-jira`, w jedną ścieżkę. Tabele zostają te z wcześniejszych dni: `projects`, `tasks`, `agent_messages`, `agent_jobs`.

   * `POST /qa` z pytaniem „Jakie wartości ma priority?” zwraca low, medium, high i cytat z `help.txt`.
   * `POST /agent/tasks` z wiadomością o otwartych high w projekcie Backend zwraca `task_id`, a `GET` po chwili podaje dwa.
   * `GET /agent/stream` dla tej samej wiadomości wysyła `tool_called`, potem tokeny.
   * W Phoenixie oba wywołania mają trace: prompt oraz narzędzie albo fragment RAG.



---

## Dzień 41: Multi-stage Docker Build dla aplikacji AI/Python

### 1. Wprowadzenie i Koncepty

Tworzenie obrazów kontenerowych dla aplikacji AI wymaga dbałości o rozmiar i bezpieczeństwo (brak zbędnych bibliotek kompilacyjnych na produkcji).

### 2. Zadania na dzisiaj

1. `Dockerfile` wieloetapowy, z `uv`. W końcowym obrazie zostają zależności produkcyjne. Proces: `uvicorn mini_jira.main:app`.
2. `docker-compose.yml`: serwis `api` (ten obraz), Redis, worker ARQ (ten sam obraz, inna komenda) i Phoenix. Wolumeny na `app.db` i `.lancedb`. Po `docker compose up` `POST /qa` o priorytet zwraca odpowiedź z cytatem.

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
