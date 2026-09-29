Python became the default language for AI work because of a mature ecosystem (`pydantic`, `httpx`, `asyncio`), first-class support in agent frameworks, and straightforward integration with ML and C++ runtimes.

Here is the plan for **Weeks 4, 5, and 6**, tied to the backend stack you already have. You will call a **local model through an OpenAI-compatible REST API**: Ollama at `http://localhost:11434/v1`, or LM Studio at `http://localhost:1234/v1`.

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

Parsing JSON from an LLM by hand breaks easily. **Instructor** (or native structured outputs) wraps the OpenAI client and forces the local model to return validated Pydantic models.

* **Automatic retry:** If the LLM emits invalid JSON or breaks a Pydantic rule, Instructor sends the validation error back to the model and asks for a fix.

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
2. Write a parser for system logs or unstructured emails: take raw text and make the local model return a validated Pydantic model (for example ticket priority, an extracted email, and a list of tags).
3. Add a `@field_validator` to the Pydantic model and watch Instructor push the LLM to repair the answer when validation fails.

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

1. Install an embedded vector database: `uv add lancedb`.
2. Embed a few sentences (local OpenAI `/v1/embeddings`, or `sentence-transformers`).
3. Store the vectors with metadata in LanceDB and run a semantic search (searching for "programming" should find the text about Python).

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

1. Write a script that loads a text file (for example internal project docs), splits it into chunks of about 128 tokens, and stores them in the vector database from Day 24. Without a tokenizer, cut on ~500 characters — roughly the same 128 tokens (about 4 characters per token).
2. Add a FastAPI `POST /qa` endpoint that embeds the user's question, runs semantic search, and returns a local-LLM answer grounded in the retrieved quotes.

---

## Day 26: Reranking (Selecting Better Context)

### 1. Introduction and Concepts

Vector search returns chunks that are semantically close, and those are not always the ones that best answer the question (unique proper names, device IDs). A **reranker** takes the question and a handful of candidates from the database, sorts them from most to least relevant, and only the best chunks go to the LLM.

* **Reranker:** A small, fast local model (for example a cross-encoder). Its input is the question plus about 20 chunks from the database.

### 2. Tasks for today

1. Extend your local RAG search with a reranker.
2. Compare how relevant the local LLM's answers are before and after reranking.

---

## Day 27: Evaluating and Testing LLM Systems (Deepeval)

### 1. Introduction and Concepts

Ordinary tests use `assert a == b`. An LLM answer is different every run. AI apps are tested with **LLM-as-a-judge**: another model scores the answer.

* **RAG metrics:**
  * *Faithfulness* — the answer uses only the supplied context.
  * *Answer relevance* — the answer addresses the question.

### 2. Tasks for today

1. Install an eval framework: `uv add deepeval`.
2. Write `pytest` tests that run your RAG pipeline and use the local LLM to check that the answers are not hallucinated.

---

## Day 28: Week 4 Review

Wire the LLM clients, Pydantic models, vector database, and tests into one fully offline module inside your backend project.

---
