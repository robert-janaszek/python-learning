# Tydzień 5: Agentic Architecture & Tool Calling (Architektury Agentowe)

W tym tygodniu przekształcisz lokalny model z "rozmówcy" w **autonomicznego agenta**, który potrafi samodzielnie korzystać z Twojego kodu: odpytywać bazy danych, wywoływać API, uruchamiać skrypty i podejmować decyzje w pętli.

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

1. Zdefiniuj dwie funkcje Pythonowe w kodzie (np. `add_task_to_jira` oraz `search_db`).
2. Stwórz pętlę wywołań:
* Wyślij zapytanie do lokalnego LLM wraz ze schematem narzędzi.
* Odczytaj `tool_calls` z odpowiedzi modelu.
* Wykonaj odpowiadającą funkcję w kodzie Python.
* Wyślij wynik wykonania funkcji z powrotem do LLM, aby wygenerował ostateczną odpowiedź dla użytkownika.



---

## Dzień 30: Budowa pętli agentowej od zera (ReAct Pattern)

### 1. Wprowadzenie i Koncepty

Wzorzec **ReAct (Reason + Act)** to algorytm, w którym agent działa w pętli `while`:

1. **Thought:** Agent analizuje problem i planuje krok.
2. **Action:** Agent decyduje się na wywołanie narzędzia.
3. **Observation:** Agent otrzymuje wynik wykonania narzędzia.
4. Powtarza proces, aż osiągnie wynik (**Final Answer**).

### 2. Zadania na dzisiaj

1. Napisz własną pętlę `while` w Pythonie bez zewnętrznych frameworków agentowych.
2. Stwórz agenta, który dostaje skomplikowane zadanie (np. "Znajdź projekt X, policz ile ma zadań i wygeneruj podsumowanie") i rozwiązuje je, wykonując po kolei 3 różne funkcje Pythonowe w pętli.
3. Dodaj zabezpieczenie (Max Iterations Limit = 5), aby agent z powodu błędnego wnioskowania lokalnego modelu nie wpadł w nieskończoną pętlę.

---

## Dzień 31: Pamięć Agenta (historia w bazie SQL)

### 1. Wprowadzenie i Koncepty

Agent bez pamięci traci kontekst przy każdym żądaniu HTTP. Historię rozmowy trzymasz w SQLite (`app.db` z Tygodnia 2), przez SQLAlchemy 2.0. Redis zostaje przy kolejkach ARQ, nie przy wiadomościach.

* Wiersze sesji (`session_id`, role `system`, `user`, `assistant`, `tool`) leżą w tabeli.
* Do promptu ładujesz okno: najnowsze wiadomości albo skrót starszych, gdy całość przekroczy N tokenów.

### 2. Zadania na dzisiaj

1. Zapisuj i odczytuj historię wiadomości agenta dla `session_id` w `app.db`.
2. Zaimplementuj okno pamięci (Memory Truncation) – gdy historia przekroczy N tokenów (ta sama jednostka co chunki RAG z dnia 25), podsumuj najstarsze tury lokalnym LLM i zapisz skrót w tej samej tabeli.

---

## Dzień 32: LangGraph (Framework Agentowy)

### 1. Wprowadzenie i Koncepty

Pisanie skomplikowanych grafów decyzyjnych od zera bywa uciążliwe. **LangGraph** to aktualnie wiodący w Pythonie framework do budowy wielo-agentowych systemów w postaci cyklicznych grafów skierowanych (State Graphs).

* **State:** Jednolity stan (zwykle `TypedDict` albo model Pydantic) przechodzący przez wszystkie węzły grafu.
* **Nodes:** Funkcje Pythonowe (lub wywołania LLM) przetwarzające stan.
* **Edges:** Warunkowe przejścia na podstawie decyzji modelu.

### 2. Zadania na dzisiaj

1. Zainstaluj LangGraph: `uv add langgraph`.
2. Zbuduj prosty graf złożony z 2 węzłów: Węzeł 1 (Agent Planujący), Węzeł 2 (Agent Wykonujący).
3. Podłącz graf pod lokalne API OpenAI.

---

## Dzień 33: Multi-Agent Collaboration (Współpraca Agentyczna)

### 1. Wprowadzenie i Koncepty

Zamiast tworzyć jednego "wszechwiedzącego" agenta, stosuje się wyspecjalizowanych agentów w małych rolach:

* **Agent Researcher:** Przeszukuje dokumenty/bazę danych.
* **Agent Writer:** Formułuje czytelną odpowiedź.
* **Agent Critic / Reviewer:** Sprawdza jakość i poprawność odpowiedzi przed wysłaniem do użytkownika.

### 2. Zadania na dzisiaj

1. Stwórz pipeline: Agent Programista pisze kod Python na podstawie zadania, Agent Tester ten kod czyta i zwraca uwagi (błąd, brakujący przypadek). Tester jeszcze nie uruchamia kodu — odpalanie jest w dniu 34.
2. Pozwól agentom na 2 wymiany: programista poprawia kod na podstawie uwag testera.

---

## Dzień 34: Sandboxing i Bezpieczeństwo Wykonywania Kodu

### 1. Wprowadzenie i Koncepty

Dawanie agentowi możliwości uruchamiania dowolnego kodu Python na Twoim lokalnym komputerze/serwerze jest ogromnym ryzykiem (Prompt Injection / `os.system("rm -rf /")`).

* **Executors:** Uruchamianie kodu wygenerowanego przez LLM wyłącznie w odizolowanych kontenerach Docker lub mikro-VM (pakiet `docker` na PyPI, dawniej `docker-py`, albo runtime WASM).

### 2. Zadania na dzisiaj

1. Zainstaluj bibliotekę Docker dla Pythona: `uv add docker`.
2. Napisz bezpieczny runner w Pythonie, który przyjmuje kod od LLM, uruchamia go w tymczasowym, pozbawionym sieci kontenerze Docker (`python:3.12-slim`), przechwytuje `stdout`/`stderr` i zwraca wynik do agenta.
3. Podłącz ten runner jako narzędzie Agenta Testera z dnia 33. Uwagi testera mają wynikać z `stdout`/`stderr`, nie tylko z czytania kodu.

---

## Dzień 35: Podsumowanie Tygodnia 5

Masz w pełni funkcjonalnego, bezpiecznego agenta, który potrafi używać narzędzi, ma pamięć i działa na lokalnym modelu.

---
