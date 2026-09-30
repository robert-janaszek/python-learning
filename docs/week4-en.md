Python became the default language for AI work because of a mature ecosystem (`pydantic`, `httpx`, `asyncio`), first-class support in agent frameworks, and straightforward integration with ML and C++ runtimes.

Here is the plan for **Weeks 4, 5, and 6**, tied to the backend stack you already have. Keep working in the `mini-jira` directory from Week 2. You will call a **local model through an OpenAI-compatible REST API**: Ollama at `http://localhost:11434/v1`, or LM Studio at `http://localhost:1234/v1`.

You go from basic LLM integration, through structured validation and RAG, to an autonomous agent.

---

# Week 4: LLM Integration, Structured Outputs, and RAG (Retrieval-Augmented Generation)

This week you connect a local LLM to your backend so it returns **typed, validated data structures** instead of free-form text, and you feed the model your own knowledge.

---

## Day 22: OpenAI API Client, Async Client, and Streaming (Local Model)

### 1. Introduction and Concepts

Even with a local model, the official `openai` package is the usual API client. `base_url` and `api_key` (any non-empty string, for example `"ollama"` — a local server does not check it) send requests to that server.

* **`AsyncOpenAI`:** An async client built on `httpx`.
* **Streaming (`stream=True`):** Tokens arrive one by one as they are generated (Server-Sent Events), consumed with `async for`.

```python
from openai import AsyncOpenAI

# Client pointed at a local API server
client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",  # or your local port (LM Studio / Ollama)
    api_key="ollama"                        # not checked by a local server
)

async def stream_response(prompt: str):
    response = await client.chat.completions.create(
        model="llama3",  # the name of your local model
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    async for chunk in response:
        content = chunk.choices[0].delta.content or ""
        print(content, end="", flush=True)

```

### 2. Tasks for today

1. Install the SDK: `uv add openai`.
2. Start a local LLM server and confirm it exposes an OpenAI-compatible endpoint.
3. Create an `llm_client.py` module with an async function for a non-streaming reply, and a FastAPI endpoint that uses `StreamingResponse` to push tokens live to the HTTP client.

---

## Day 23: Structured Outputs and Instructor (Pydantic + LLM)

### 1. Introduction and Concepts

Parsing JSON from an LLM by hand breaks easily. **Instructor** wraps the OpenAI client from Day 22 and returns a validated Pydantic model.

The example uses `Mode.JSON`: the server is asked for valid JSON, and the schema plus validation stay on Instructor's side. This mode works on Ollama and in LM Studio. Native structured outputs, where the server follows a JSON Schema while generating, are better wherever the endpoint honors them. This day does not assume that.

* **Retry:** catches a bad value inside valid JSON, for example a `@field_validator` rule. Instructor sends the validation error back to the model and asks for a fix.

```python
import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

# Wrap the OpenAI client with Instructor
client = instructor.from_openai(
    AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama"),
    mode=instructor.Mode.JSON
)

class UserExtraction(BaseModel):
    name: str
    age: int
    skills: list[str] = Field(description="List of technical skills")

async def extract_data(text: str) -> UserExtraction:
    # The call returns an already validated Pydantic instance.
    return await client.chat.completions.create(
        model="llama3",
        response_model=UserExtraction,
        messages=[{"role": "user", "content": text}],
        max_retries=3
    )

```

### 2. Tasks for today

1. Install Instructor: `uv add instructor`.
2. In `ticket_parser.py`, write `parse_ticket(text: str) -> TicketDraft`. The inputs are two or three emails you store as `str` constants in the same file. No inbox, no files, and no external API. Each email is loose text: who is writing, what the issue is, and sometimes a priority in words ("urgent", "this can wait").

   `TicketDraft` has:

   * `title: str` — a short ticket title
   * `sender_email: str` — the address taken from the text
   * `priority: Literal["low", "medium", "high"]`
   * `tags: list[str]` — a few short labels, for example the topic of the issue

   Run the function on each email and print the model it returns. Write one email clearly and another messily, without the address on its own line, so you can see what the model pulls from context.
3. Add a `@field_validator` on `sender_email`: the value must contain `@` and a dot in the part after `@`. Run `parse_ticket` on the email that has no address, with `max_retries=3`. The first attempt shows a validation error sent back to the model, then a repaired answer or the retries running out.

---

## Day 24: Vector Databases and Embeddings (LanceDB / Qdrant)

### 1. Introduction and Concepts

Semantic search matches meaning, not keywords. You turn text into numeric vectors (embeddings) and store them in a vector database.

* **Embedding model:** Runs locally (for example `sentence-transformers`, or a local `/v1/embeddings` endpoint).
* **LanceDB / Qdrant:** Stores vectors for nearest-neighbour search (cosine similarity / Euclidean distance). LanceDB runs embedded, like SQLite, and that is what the tasks use. Qdrant is the alternative that runs as its own server.

```python
import lancedb

# Local file database (like SQLite)
db = lancedb.connect("./.lancedb")

# Table of precomputed vectors (you embed the text before this step)
table = db.create_table(
    "documents",
    data=[
        {"id": 1, "vector": [0.1, 0.2, 0.3], "text": "Python supports async I/O"},
        {"id": 2, "vector": [0.9, 0.1, 0.0], "text": "Coffee is brewed at 90 degrees"},
    ],
)

# Nearest-vector search
results = table.search([0.1, 0.2, 0.3]).limit(1).to_list()

```

### 2. Tasks for today

1. Install the database: `uv add lancedb`.
2. In `mini_jira/knowledge.py`, store six sentences as constants. Five describe mini-jira, and one is from another domain so search has a misleading neighbor:

   * A project groups tasks.
   * A task has a title and belongs to one project.
   * A task priority is exactly low, medium, or high.
   * A completed task has is_completed set to true.
   * Chat returns tokens as a stream.
   * Coffee is brewed at 90 degrees.

   Embed each sentence with the Day 22 client, endpoint `/v1/embeddings`. Keep the embedding model name in `llm_client.py`.
3. Store the rows in LanceDB, directory `./.lancedb`, table `notes`, columns `text` and `vector`. The query "what values can a task priority take" must return the sentence about low, medium, and high as the first hit. Print that text.

---

## Day 25: Building Naive RAG (Retrieval-Augmented Generation)

### 1. Introduction and Concepts

RAG gives the local LLM context retrieved from your private knowledge base, which cuts down hallucinations.

**RAG flow:**

1. The user asks a question.
2. You embed the question.
3. You fetch the top N closest document chunks from the vector database.
4. You build a prompt: `"Using the context below: {context} Answer the question: {question}"`.
5. You send that prompt to the local LLM.

### 2. Tasks for today

1. Add `mini-jira/knowledge/help.txt`: at least eight short paragraphs about projects and tasks. Two sentences must appear in it: "A task priority is exactly low, medium, or high." and "A completed task has is_completed set to true and is no longer open." The other paragraphs are also about tasks, and they do not repeat that rule. The script `python -m mini_jira.index_help` reads the file, cuts it at about 500 characters (roughly 128 tokens, about 4 characters per token), and stores the chunks in table `help_chunks` (columns `text`, `vector`) in the `./.lancedb` directory from Day 24.
2. Endpoint `POST /qa`. Body: `{"question": str}`. Response: `{"answer": str, "quotes": list[str]}`, where `quotes` are the texts of the three nearest chunks. The question "What values can priority take?" must list low, medium, and high in `answer`, and `quotes` must include the `help.txt` chunk that says so.

---

## Day 26: Reranking (Selecting Better Context)

### 1. Introduction and Concepts

Vector search returns chunks that are semantically close, and those are not always the ones that best answer the question (unique proper names, device IDs). A **reranker** takes the question and a handful of candidates from the database, sorts them from most to least relevant, and only the best chunks go to the LLM.

* **Reranker:** A small, fast local model (for example a cross-encoder). Its input is the question plus about 20 chunks from the database.

### 2. Tasks for today

1. Add a reranker to `POST /qa`. `uv add sentence-transformers`. Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`. Fetch 8 chunks from LanceDB first, then the reranker orders them from most to least relevant, and the prompt receives the first 3.
2. Compare on one question: "Does a completed task stay on the open list?". Print the order of the eight chunks before reranking and after it, then the two model answers: from the first three vector hits, and from the first three after reranking.

---

## Day 27: Evaluating and Testing LLM Systems (Deepeval)

### 1. Introduction and Concepts

Ordinary tests use `assert a == b`. An LLM answer is different every run. AI apps are tested with **LLM-as-a-judge**: another model scores the answer.

* **RAG metrics:**
  * *Faithfulness* — the answer uses only the supplied context.
  * *Answer relevance* — the answer addresses the question.

### 2. Tasks for today

1. Install an eval framework: `uv add deepeval`.
2. In `src/mini_jira/tests/test_qa.py`, two tests call the same pipeline as `POST /qa` (the function, not the HTTP server). The judge is the Day 22 local model, the same `base_url`, with no cloud API key. Metrics: Faithfulness and Answer Relevancy, threshold 0.7.

   * "What values can priority take?" — the answer must stay with the chunk about low, medium, and high.
   * "What is the support phone number?" — that sentence is not in `help.txt`. The answer must say the materials do not contain it.

---

## Day 28: Week 4 Review

Check that the `mini-jira` module works offline, on the local model:

1. `POST /qa` asked about priority returns low, medium, and high, plus a quote from `help.txt`.
2. `parse_ticket` from Day 23 still returns a `TicketDraft` for an email stored in the file.
3. `uv run pytest src/mini_jira/tests/test_qa.py` passes with Ollama or LM Studio running.

---
