# Tydzień 5: Agentic Architecture & Tool Calling (Architektury Agentowe)

W tym tygodniu przekształcisz lokalny model z "rozmówcy" w **autonomicznego agenta**, który potrafi samodzielnie korzystać z Twojego kodu: odpytywać bazy danych, wywoływać API, uruchamiać skrypty i podejmować decyzje w pętli. Dalej pracujesz w katalogu `mini-jira` z Tygodnia 2.

---

## Dzień 29: Native Tool Calling (Function Calling) z lokalnym LLM

### 1. Wprowadzenie i Koncepty

Nowoczesne modele LLM potrafią zwrócić specjalny obiekt JSON mówiący: *"Nie mam odpowiedzi w mojej wiedzy, ale proszę uruchom dla mnie funkcję `get_weather(city='Warsaw')` i daj mi jej wynik"*.

* **Tool Definition:** Schemat funkcji wygenerowany automatycznie na podstawie type hintów i docstringów w Pythonie.

```python
# Definicja narzędzia w kodzie Python
def get_user_balance(user_id: int) -> int:
    """Pobiera aktualne saldo konta użytkownika z bazy danych, w groszach."""
    # ... zapytanie do bazy ...
    return 15_050  # 150,50 zł

# Przekazanie narzędzia do OpenAI API
tools = [{
    "type": "function",
    "function": {
        "name": "get_user_balance",
        "description": "Pobiera aktualne saldo konta użytkownika z bazy danych, w groszach.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
            },
            "required": ["user_id"],
        },
    },
}]

```

### 2. Zadania na dzisiaj

1. W `mini_jira/agent.py` dwie funkcje na istniejącej bazie `app.db` (modele `ProjectModel` i `TaskModel`):

   * `list_projects() -> list[str]` — nazwy projektów.
   * `create_task(project_name: str, title: str, priority: Literal["low", "medium", "high"]) -> int` — dopisuje zadanie do projektu i zwraca jego `id`.
2. Pętla na jednym zdaniu: „Dodaj do projektu Backend zadanie «Napraw login» z priorytetem high”. Jeśli projektu nie ma, skrypt zakłada go przed pętlą. Wyślij zdanie i schemat obu funkcji do lokalnego modelu, wykonaj `tool_calls` w Pythonie, odeślij wynik narzędzia i wypisz końcową odpowiedź asystenta. W bazie ma zostać zadanie o tym tytule i priorytecie.



---

## Dzień 30: Budowa pętli agentowej od zera (ReAct Pattern)

### 1. Wprowadzenie i Koncepty

Wzorzec **ReAct (Reason + Act)** to algorytm, w którym agent działa w pętli `while`:

1. **Thought:** Agent analizuje problem i planuje krok.
2. **Action:** Agent decyduje się na wywołanie narzędzia.
3. **Observation:** Agent otrzymuje wynik wykonania narzędzia.
4. Powtarza proces, aż osiągnie wynik (**Final Answer**).

### 2. Zadania na dzisiaj

1. W tym samym `agent.py` pętla `while`, bez LangGraph i innych frameworków.
2. Przed uruchomieniem skrypt wstawia projekt „Backend” z trzema zadaniami, jeśli ich nie ma: dwa otwarte z priorytetem high („Napraw login”, „Padł deploy”) i jedno ukończone low („Opis README”). Agent dostaje jedno polecenie: „Znajdź projekt Backend, policz otwarte zadania i podaj, ile z nich ma priorytet high”. Do odpowiedzi dochodzi trzema funkcjami:

   * `find_project(name: str) -> int`
   * `list_open_tasks(project_id: int) -> list[str]` — tytuły, gdzie `is_completed` jest false
   * `count_by_priority(project_id: int) -> dict[str, int]` — liczby dla low, medium i high wśród otwartych

   Sens odpowiedzi: dwa otwarte, oba high.
3. Po 5 iteracjach pętla się kończy i zwraca komunikat, że limit kroków został osiągnięty.

---

## Dzień 31: Pamięć Agenta (historia w bazie SQL)

### 1. Wprowadzenie i Koncepty

Agent bez pamięci traci kontekst przy każdym żądaniu HTTP. Historię rozmowy trzymasz w SQLite (`app.db` z Tygodnia 2), przez SQLAlchemy 2.0. Redis zostaje przy kolejkach ARQ, nie przy wiadomościach.

* Wiersze sesji (`session_id`, role `system`, `user`, `assistant`, `tool`) leżą w tabeli.
* Do promptu ładujesz okno: najnowsze wiadomości albo skrót starszych, gdy całość przekroczy N tokenów.

### 2. Zadania na dzisiaj

1. Migracja Alembic: tabela `agent_messages` z kolumnami `id`, `session_id` (str), `role` (`system`, `user`, `assistant`, `tool`), `content`, `created_at`. Agent z dnia 30 zapisuje tam każdą turę i przy starcie wczytuje wiersze danego `session_id`. Dwa uruchomienia z tym samym `session_id`. Pierwsze: polecenie z dnia 30. Drugie, już bez nazwy projektu: „A ile z nich było high?”. Drugie dochodzi do „dwa” z historii w `app.db`.
2. Okno: gdy treść historii przekroczy około 2000 znaków (cztery fragmenty po ~500 znaków z dnia 25), najstarsze tury idą do lokalnego modelu po skrót. Skrót zapisujesz w tej samej tabeli jako wiersz `role=system`, treść od „Skrót:”. Do następnego promptu wchodzi skrót i tury, które zostały.

---

## Dzień 32: LangGraph (Framework Agentowy)

### 1. Wprowadzenie i Koncepty

Pisanie skomplikowanych grafów decyzyjnych od zera bywa uciążliwe. **LangGraph** to aktualnie wiodący w Pythonie framework do budowy wielo-agentowych systemów w postaci cyklicznych grafów skierowanych (State Graphs).

* **State:** Jednolity stan (zwykle `TypedDict` albo model Pydantic) przechodzący przez wszystkie węzły grafu.
* **Nodes:** Funkcje Pythonowe (lub wywołania LLM) przetwarzające stan.
* **Edges:** Warunkowe przejścia na podstawie decyzji modelu.

### 2. Zadania na dzisiaj

1. Zainstaluj LangGraph: `uv add langgraph`.
2. Graf o dwóch węzłach na stanie z polami `plan: str` i `answer: str`. Węzeł `plan` pyta lokalny model, którą funkcję z dnia 30 wywołać jako pierwszą dla polecenia „Znajdź projekt Backend i podaj liczbę otwartych zadań high”. Węzeł `execute` odpala tę funkcję na `app.db` i wpisuje `answer`.
3. Ten sam `base_url` co w dniu 22. Uruchom graf i wypisz `answer`. Sens odpowiedzi: dwa.

---

## Dzień 33: Multi-Agent Collaboration (Współpraca Agentyczna)

### 1. Wprowadzenie i Koncepty

Zamiast tworzyć jednego "wszechwiedzącego" agenta, stosuje się wyspecjalizowanych agentów w małych rolach:

* **Agent Researcher:** Przeszukuje dokumenty/bazę danych.
* **Agent Writer:** Formułuje czytelną odpowiedź.
* **Agent Critic / Reviewer:** Sprawdza jakość i poprawność odpowiedzi przed wysłaniem do użytkownika.

### 2. Zadania na dzisiaj

1. Dwa wywołania lokalnego modelu, jeszcze bez uruchamiania kodu. Programista dostaje specyfikację: funkcja `open_high_tasks(tasks: list[dict]) -> list[str]` zwraca tytuły, gdzie `priority` to `high` i `is_completed` to false. Tester czyta kod i oddaje listę uwag: zły warunek, brakujące pole albo zmiana wejścia.
2. Druga tura: programista dostaje te uwagi i zwraca poprawiony kod. Zostaw obie wersje w zmiennych i wypisz uwagi testera. Uruchomienie kodu jest w dniu 34.

---

## Dzień 34: Sandboxing i Bezpieczeństwo Wykonywania Kodu

### 1. Wprowadzenie i Koncepty

Dawanie agentowi możliwości uruchamiania dowolnego kodu Python na Twoim lokalnym komputerze/serwerze jest ogromnym ryzykiem (Prompt Injection / `os.system("rm -rf /")`).

* **Executors:** Uruchamianie kodu wygenerowanego przez LLM wyłącznie w odizolowanych kontenerach Docker lub mikro-VM (pakiet `docker` na PyPI, dawniej `docker-py`, albo runtime WASM).

### 2. Zadania na dzisiaj

1. Zainstaluj bibliotekę Docker dla Pythona: `uv add docker`.
2. Runner bierze kod od modelu i startuje tymczasowy kontener `python:3.12-slim` bez sieci, z limitem 10 sekund. Po biegu kontener jest usuwany. Do kodu runner dokleja wywołanie `open_high_tasks` na trzech słownikach: otwarte high „Napraw login”, ukończone high „Stary bug”, otwarte low „Opis”. Zwraca `stdout` i `stderr`.
3. Tester z dnia 33 woła ten runner. Uwaga ma cytować `stdout` albo `stderr`. Do zobaczenia: funkcja, która zwraca też ukończone high — w `stdout` jest „Stary bug”, tester to zgłasza.

---

## Dzień 35: Podsumowanie Tygodnia 5

Sprawdź agenta na danych projektu Backend z dnia 30:

1. Polecenie o otwartych zadaniach high kończy się liczbą dwa, a w `app.db` widać ślad wywołań narzędzi.
2. Drugie pytanie w tej samej sesji („A ile z nich było high?”) korzysta z `agent_messages`.
3. Tester odpala `open_high_tasks` w kontenerze i uwaga powołuje się na `stdout`.

---
