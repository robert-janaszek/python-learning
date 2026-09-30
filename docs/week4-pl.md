Python stał się absolutnym standardem w świecie AI ze względu na dojrzały ekosystem (`pydantic`, `httpx`, `asyncio`), natywne wsparcie w frameworkach agentowych oraz możliwość bezszwowej integracji ze środowiskami ML/C++.

Oto plan na **Tygodnie 4, 5 i 6**, powiązany z Twoim dotychczasowym backendowym stackiem. Dalej pracujesz w katalogu `mini-jira` z Tygodnia 2. Zakładamy pracę z **lokalnym modelem przez REST API zgodne z OpenAI**: Ollama pod `http://localhost:11434/v1` albo LM Studio pod `http://localhost:1234/v1`.

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

Ręczne parsowanie JSON-a zwróconego przez LLM jest podatne na błędy. **Instructor** opakowuje klienta OpenAI z Dnia 22 i zwraca zwalidowany model Pydantic.

Przykład używa `Mode.JSON`: serwer ma oddać poprawny JSON, a schemat i walidacja zostają po stronie Instructora. Ten tryb działa na Ollamie i w LM Studio. Natywne structured outputs, gdzie serwer trzyma się JSON Schema już w trakcie generowania, są lepsze tam, gdzie endpoint je honoruje. Tutaj ich nie zakładamy.

* **Retry:** łapie złą wartość przy poprawnym JSON-ie, na przykład regułę z `@field_validator`. Instructor odsyła błąd walidacji do modelu i prosi o poprawkę.

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
2. W module `ticket_parser.py` napisz funkcję `parse_ticket(text: str) -> TicketDraft`. Danymi wejściowymi są dwa albo trzy maile, które wpisujesz jako stałe `str` w tym samym pliku. Bez skrzynki, plików i zewnętrznego API. Każdy mail to luźny tekst: kto pisze, czego dotyczy sprawa, czasem priorytet słowami („pilne”, „może poczekać”).

   Model `TicketDraft`:

   * `title: str` — krótki tytuł zgłoszenia
   * `sender_email: str` — adres wyciągnięty z tekstu
   * `priority: Literal["low", "medium", "high"]`
   * `tags: list[str]` — kilka krótkich etykiet, na przykład temat sprawy

   Uruchom funkcję na każdym mailu i wypisz zwrócony model. Jeden mail napisz wyraźnie, drugi chaotycznie, bez adresu w jednej linijce, żeby było widać, co model wyciąga z kontekstu.
3. Na polu `sender_email` dodaj `@field_validator`: wartość ma zawierać `@` i kropkę w części za `@`. Uruchom `parse_ticket` na mailu bez adresu, z `max_retries=3`. Przy pierwszej próbie widać błąd walidacji odesłany do modelu, potem poprawioną odpowiedź albo wyczerpanie prób.

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

1. Zainstaluj bazę: `uv add lancedb`.
2. W `mini_jira/knowledge.py` wpisz sześć zdań jako stałe. Pięć opisuje mini-jira, jedno jest z innej dziedziny, żeby wyszukiwanie miało mylący trop:

   * Projekt grupuje zadania.
   * Zadanie ma tytuł i należy do jednego projektu.
   * Priorytet zadania to dokładnie low, medium albo high.
   * Ukończone zadanie ma is_completed równe true.
   * Czat zwraca tokeny strumieniem.
   * Kawa parzy się w 90 stopniach.

   Każde zdanie zamień na wektor klientem z dnia 22, endpoint `/v1/embeddings`. Nazwę modelu embeddingów trzymaj w `llm_client.py`.
3. Zapisz wiersze w LanceDB, katalog `./.lancedb`, tabela `notes`, kolumny `text` i `vector`. Zapytanie „jakie wartości ma priorytet zadania” ma zwrócić zdanie o low, medium i high jako pierwszy wynik. Wypisz ten tekst.

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

1. Dopisz plik `mini-jira/knowledge/help.txt`: co najmniej osiem krótkich akapitów o projektach i zadaniach. W środku mają paść dwa zdania: „Priorytet zadania to dokładnie low, medium albo high.” oraz „Ukończone zadanie ma is_completed równe true i nie jest już otwarte.” Pozostałe akapity też są o zadaniach, ale tej reguły nie powtarzają. Skrypt `python -m mini_jira.index_help` czyta plik, tnie po około 500 znakach (zgrubnie 128 tokenów, około 4 znaki na token) i zapisuje fragmenty w tabeli `help_chunks` (kolumny `text`, `vector`) w `./.lancedb` z dnia 24.
2. Endpoint `POST /qa`. Body: `{"question": str}`. Odpowiedź: `{"answer": str, "quotes": list[str]}`, a `quotes` to teksty trzech najbliższych fragmentów. Pytanie „Jakie wartości ma priority?” ma w `answer` wymienić low, medium i high, a w `quotes` fragment z `help.txt`, który to mówi.

---

## Dzień 26: Reranking (Dobór lepszego kontekstu)

### 1. Wprowadzenie i Koncepty

Wyszukiwanie wektorowe zwraca fragmenty podobne znaczeniowo, ale nie zawsze te, które najlepiej odpowiadają na pytanie (np. przy unikalnych nazwach własnych albo ID urządzeń). **Reranker** dostaje pytanie i kilkanaście kandydatów z bazy, układa je od najbardziej do najmniej trafnego, i do LLM idą tylko najlepsze.

* **Reranker:** Mały, szybki model lokalny (np. `cross-encoder`). Na wejściu ma pytanie oraz ok. 20 fragmentów z bazy.

### 2. Zadania na dzisiaj

1. Do `POST /qa` dołóż reranker. `uv add sentence-transformers`. Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`. Najpierw weź 8 fragmentów z LanceDB, potem reranker układa je od najbardziej do najmniej trafnego i do promptu idą pierwsze 3.
2. Porównanie na jednym pytaniu: „Czy ukończone zadanie zostaje na liście otwartych?”. Wypisz kolejność ośmiu fragmentów przed rerankingiem i po nim, potem dwie odpowiedzi modelu: z trzech pierwszych fragmentów wektorowych i z trzech pierwszych po rerankingu.

---

## Dzień 27: Ewaluacja i Testowanie Systemów LLM (Deepeval)

### 1. Wprowadzenie i Koncepty

W tradycyjnym kodzie używasz `assert a == b`. W aplikacjach opartych na LLM odpowiedź za każdym razem wygląda inaczej. Do testowania aplikacji AI stosuje się podejście **LLM-as-a-Judge** (inny model ocenia jakość odpowiedzi).

* **Metryki RAG:**
  * *Faithfulness* — odpowiedź opiera się wyłącznie na dostarczonym kontekście.
  * *Answer Relevance* — odpowiedź odpowiada na zadane pytanie.



### 2. Zadania na dzisiaj

1. Zainstaluj framework do ewaluacji: `uv add deepeval`.
2. W `src/mini_jira/tests/test_qa.py` dwa testy wołają ten sam pipeline co `POST /qa` (funkcję, nie serwer HTTP). Sędzia to lokalny model z dnia 22, ten sam `base_url`, bez klucza chmurowego. Metryki: Faithfulness i Answer Relevancy, próg 0.7.

   * „Jakie wartości ma priority?” — odpowiedź ma trzymać się fragmentu o low, medium i high.
   * „Jaki jest numer telefonu supportu?” — tego zdania nie ma w `help.txt`. Odpowiedź ma powiedzieć, że w materiałach tego nie ma.

---

## Dzień 28: Przegląd Tygodnia 4 i Podsumowanie

Sprawdź, że moduł w `mini-jira` działa offline, na lokalnym modelu:

1. `POST /qa` z pytaniem o priorytet zwraca low, medium i high oraz cytat z `help.txt`.
2. `parse_ticket` z dnia 23 nadal zwraca `TicketDraft` dla maila wpisanego w pliku.
3. `uv run pytest src/mini_jira/tests/test_qa.py` przechodzi przy włączonym Ollama albo LM Studio.

---
