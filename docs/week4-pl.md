Python stał się absolutnym standardem w świecie AI ze względu na dojrzały ekosystem (`pydantic`, `httpx`, `asyncio`), natywne wsparcie w frameworkach agentowych oraz możliwość bezszwowej integracji ze środowiskami ML/C++.

Oto plan na **Tygodnie 4, 5 i 6**, powiązany z Twoim dotychczasowym backendowym stackiem. Zakładamy pracę z **lokalnym modelem przez REST API zgodne z OpenAI**: Ollama pod `http://localhost:11434/v1` albo LM Studio pod `http://localhost:1234/v1`.

Przejdziemy od podstawowych integracji LLM, przez zaawansowaną walidację struktur i RAG, po budowę autonomicznego agenta.

---

# Tydzień 4: Integracja z LLM, Structured Outputs i RAG (Retrieval-Augmented Generation)

W tym tygodniu nauczysz się, jak zintegrować lokalny model LLM z backendem tak, aby nie zwracał losowego tekstu, lecz **gwarantowane, poprawne pod względem typów struktury danych** oraz jak karmić model własną wiedzą.

---

## Dzień 22: Klient OpenAI API, Async Client i Streaming (Lokalny Model)

### 1. Wprowadzenie i Koncepty

Mimo że używasz lokalnego modelu, oficjalny pakiet `openai` jest branżowym standardem interfejsu API. Za pomocą `base_url` oraz `api_key` (dowolny niepusty ciąg, np. `"ollama"` — lokalny serwer go nie sprawdza) kierujesz zapytania bezpośrednio do swojego lokalnego serwera.

* **`AsyncOpenAI`:** Asynchroniczny klient wykorzystujący `httpx` pod spodem.
* **Streaming (`stream=True`):** Odbieranie tokenów po kolei w miarę ich generowania (Server-Sent Events) z wykorzystaniem `async for`.

```python
from openai import AsyncOpenAI

# Klient skonfigurowany pod lokalny serwer API
client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",  # lub Twój lokalny port (np. LM Studio / Ollama)
    api_key="ollama"                        # Klucz nie jest weryfikowany lokalnie
)

async def stream_response(prompt: str):
    response = await client.chat.completions.create(
        model="llama3", # nazwa Twojego lokalnego modelu
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    async for chunk in response:
        content = chunk.choices[0].delta.content or ""
        print(content, end="", flush=True)

```

### 2. Zadania na dzisiaj

1. Zainstaluj SDK: `uv add openai`.
2. Uruchom lokalny serwer LLM i upewnij się, że eksponuje endpoint OpenAI-compatible.
3. Stwórz moduł `llm_client.py`, który dostarcza asynchroniczną funkcję do generowania odpowiedzi bez streamingu, oraz endpoint w FastAPI wykorzystujący `StreamingResponse` do przesyłania tokenów na żywo do klienta HTTP.

---

## Dzień 23: Structured Outputs & Instructor (Pydantic + LLM)

### 1. Wprowadzenie i Koncepty

Ręczne parsowanie JSON-a zwróconego przez LLM jest podatne na błędy. Biblioteka **Instructor** (albo natywne Structured Outputs) opakowuje klienta OpenAI i wymusza na lokalnym modelu zwracanie danych jako zwalidowanych modeli Pydantic.

* **Automatyczne Retry:** Jeśli LLM wygeneruje niepoprawny JSON lub złamie regułę walidacji Pydantic, Instructor automatycznie wyśle błąd walidacji z powrotem do LLM z prośbą o poprawkę.

```python
import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

# Opakowanie klienta OpenAI przez Instructor
client = instructor.from_openai(
    AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama"),
    mode=instructor.Mode.JSON
)

class UserExtraction(BaseModel):
    name: str
    age: int
    skills: list[str] = Field(description="Lista umiejętności technicznych")

async def extract_data(text: str) -> UserExtraction:
    # LLM zwraca od razu zweryfikowaną instancję Pydantic.
    return await client.chat.completions.create(
        model="llama3",
        response_model=UserExtraction,
        messages=[{"role": "user", "content": text}],
        max_retries=3
    )

```

### 2. Zadania na dzisiaj

1. Zainstaluj `instructor`: `uv add instructor`.
2. Napisz parser logów systemowych lub nieustrukturyzowanych e-maili: przyjmij tekst wejściowy i zmuś lokalny model do zwrócenia zwalidowanego modelu Pydantic (np. priorytet zgłoszenia, wyciągnięty e-mail, lista powiązanych tagów).
3. Dodaj `@field_validator` do modelu Pydantic i przetestuj, jak Instructor zmusza LLM do poprawy odpowiedzi przy błędzie.

---

## Dzień 24: Bazy Wektorowe i Embeddings (LanceDB / Qdrant)

### 1. Wprowadzenie i Koncepty

Aby przeszukiwać tekst semantycznie (po znaczeniu, a nie po słowach kluczowych), przekształcamy tekst na wektory liczbowe (Embeddings) i zapisujemy je w bazie wektorowej.

* **Model embeddingów:** Działa lokalnie (np. `sentence-transformers` albo lokalny endpoint `/v1/embeddings`).
* **LanceDB / Qdrant:** Bazy pod wyszukiwanie najbliższych sąsiadów (podobieństwo cosinusowe / odległość euklidesowa). LanceDB działa w trybie embedded (jak SQLite) i tego używasz w zadaniach. Qdrant to alternatywa w postaci osobnego serwera.

```python
import lancedb

# Połączenie z lokalną bazą plikową (jak SQLite)
db = lancedb.connect("./.lancedb")

# Tabela z gotowymi wektorami (embedding liczysz wcześniej, nie tutaj)
table = db.create_table(
    "documents",
    data=[
        {"id": 1, "vector": [0.1, 0.2, 0.3], "text": "Python wspiera asynchroniczność"},
        {"id": 2, "vector": [0.9, 0.1, 0.0], "text": "Kawa parzy się w 90 stopniach"},
    ],
)

# Wyszukiwanie najbliższych wektorów
results = table.search([0.1, 0.2, 0.3]).limit(1).to_list()

```

### 2. Zadania na dzisiaj

1. Zainstaluj bezobsługową bazę wektorową: `uv add lancedb`.
2. Wygeneruj wektory dla kilku zdań (używając lokalnego API OpenAI `/v1/embeddings` lub biblioteki `sentence-transformers`).
3. Zapisz wektory wraz z meta-danymi do bazy LanceDB i przeprowadź wyszukiwanie semantyczne (np. szukając "programowanie" znajdź tekst o "Pythonie").

---

## Dzień 25: Budowa Naive RAG (Retrieval-Augmented Generation)

### 1. Wprowadzenie i Koncepty

RAG polega na dostarczeniu lokalnemu modelowi LLM kontekstu wyszukanego z Twojej prywatnej bazy wiedzy, zapobiegając halucynacjom.

**Przepływ RAG:**

1. User zadaje pytanie.
2. Zmieniasz pytanie na wektor (embedding).
3. Szukasz top N najbardziej pasujących fragmentów dokumentów w bazie wektorowej.
4. Budujesz Prompt: `"Na podstawie poniższego kontekstu: {kontekst} Odpowiedz na pytanie: {pytanie}"`.
5. Przekazujesz prompt do lokalnego LLM.

### 2. Zadania na dzisiaj

1. Stwórz skrypt, który wczytuje plik tekstowy (np. dokumentację wewnętrzną projektu), tnie go na fragmenty po ok. 128 tokenach i zapisuje je w bazie wektorowej z Dnia 24. Bez tokenizera tnij po ~500 znakach — to zgrubnie te same 128 tokenów (ok. 4 znaki na token).
2. Stwórz endpoint w FastAPI `POST /qa`, który na podstawie pytania użytkownika robi wyszukiwanie semantyczne i zwraca odpowiedź z lokalnego LLM podpartą znalezionymi cytatami z dokumentu.

---

## Dzień 26: Reranking (Dobór lepszego kontekstu)

### 1. Wprowadzenie i Koncepty

Wyszukiwanie wektorowe zwraca fragmenty podobne znaczeniowo, ale nie zawsze te, które najlepiej odpowiadają na pytanie (np. przy unikalnych nazwach własnych albo ID urządzeń). **Reranker** dostaje pytanie i kilkanaście kandydatów z bazy, układa je od najbardziej do najmniej trafnego, i do LLM idą tylko najlepsze.

* **Reranker:** Mały, szybki model lokalny (np. `cross-encoder`). Na wejściu ma pytanie oraz ok. 20 fragmentów z bazy.

### 2. Zadania na dzisiaj

1. Rozbuduj wyszukiwanie w swoim lokalnym RAG o reranker.
2. Porównaj trafność odpowiedzi lokalnego LLM przed rerankingiem i po nim.

---

## Dzień 27: Ewaluacja i Testowanie Systemów LLM (Deepeval)

### 1. Wprowadzenie i Koncepty

W tradycyjnym kodzie używasz `assert a == b`. W aplikacjach opartych na LLM odpowiedź za każdym razem wygląda inaczej. Do testowania aplikacji AI stosuje się podejście **LLM-as-a-Judge** (inny model ocenia jakość odpowiedzi).

* **Metryki RAG:**
  * *Faithfulness* — odpowiedź opiera się wyłącznie na dostarczonym kontekście.
  * *Answer Relevance* — odpowiedź odpowiada na zadane pytanie.



### 2. Zadania na dzisiaj

1. Zainstaluj framework do ewaluacji: `uv add deepeval`.
2. Napisz testy w `pytest`, które uruchamiają Twój pipeline RAG i używają lokalnego LLM do sprawdzenia, czy wygenerowane odpowiedzi nie zawierają halucynacji.

---

## Dzień 28: Przegląd Tygodnia 4 i Podsumowanie

Połącz klientów LLM, Pydantic, bazę wektorową oraz testy w jeden działający w pełni offline moduł w Twoim projekcie backendowym.

---
