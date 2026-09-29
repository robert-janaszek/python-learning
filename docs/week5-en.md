# Week 5: Agentic Architecture and Tool Calling

This week you turn the local model from a chatbot into an **autonomous agent** that can use your code: query databases, call APIs, run scripts, and decide what to do next inside a loop. Keep working in the `mini-jira` directory from Week 2.

---

## Day 29: Native Tool Calling (Function Calling) with a Local LLM

### 1. Introduction and Concepts

Modern LLMs can return a JSON object that means: *"I cannot answer this from my own knowledge — please run `get_weather(city='Warsaw')` and give me the result."*

* **Tool definition:** A function schema built from Python type hints and docstrings.

```python
# Tool implemented in Python
def get_user_balance(user_id: int) -> int:
    """Load the user's current account balance from the database, in minor units (cents)."""
    # ... database query ...
    return 15_050  # 150.50 in major units

# Pass the tool to the OpenAI API
tools = [{
    "type": "function",
    "function": {
        "name": "get_user_balance",
        "description": "Load the user's current account balance from the database, in minor units (cents).",
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

### 2. Tasks for today

1. Define two Python functions (for example `add_task_to_jira` and `search_db`).
2. Build the call loop:
* Send the user request to the local LLM together with the tool schemas.
* Read `tool_calls` from the model response.
* Run the matching Python function.
* Send the function result back to the LLM so it can write the final answer for the user.



---

## Day 30: An Agent Loop from Scratch (ReAct Pattern)

### 1. Introduction and Concepts

**ReAct (Reason + Act)** is a loop. The agent repeats `while` it still has work to do:

1. **Thought:** The agent looks at the problem and plans the next step.
2. **Action:** The agent chooses a tool to call.
3. **Observation:** The agent receives the tool result.
4. It repeats until it can give a **final answer**.

### 2. Tasks for today

1. Write your own `while` loop in Python, with no agent framework.
2. Build an agent that receives a multi-step task (for example "Find project X, count its tasks, and write a summary") and solves it by calling three different Python functions in sequence.
3. Add a guard (max iterations = 5) so a bad local-model decision cannot spin forever.

---

## Day 31: Agent Memory (History in the SQL Database)

### 1. Introduction and Concepts

An agent with no memory forgets the conversation on every HTTP request. Store the transcript in SQLite (`app.db` from Week 2), through SQLAlchemy 2.0. Redis stays with the ARQ queue, not with messages.

* Session rows (`session_id`, roles `system`, `user`, `assistant`, `tool`) live in a table.
* The prompt only gets a window: the newest messages, or a summary of older ones once the whole history passes N tokens.

### 2. Tasks for today

1. Save and load the agent's messages for a `session_id` in `app.db`.
2. Add a memory window (memory truncation): when the history passes N tokens (the same unit as the RAG chunks from Day 25), summarize the oldest turns with the local LLM and store that summary in the same table.

---

## Day 32: LangGraph (Agent Framework)

### 1. Introduction and Concepts

Hand-rolled decision graphs get painful. **LangGraph** is the current Python default for multi-agent systems built as cyclic directed graphs (state graphs).

* **State:** One shared state object (usually a `TypedDict` or a Pydantic model) passed through every node.
* **Nodes:** Python functions (or LLM calls) that update that state.
* **Edges:** Conditional transitions chosen from the model's decision.

### 2. Tasks for today

1. Install LangGraph: `uv add langgraph`.
2. Build a two-node graph: node 1 is a planning agent, node 2 is an executing agent.
3. Point the graph at your local OpenAI-compatible API.

---

## Day 33: Multi-Agent Collaboration

### 1. Introduction and Concepts

Instead of one agent that does everything, use small specialized roles:

* **Researcher:** Searches documents or the database.
* **Writer:** Turns the findings into a readable answer.
* **Critic / reviewer:** Checks the answer before it goes to the user.

### 2. Tasks for today

1. Build a pipeline: a programmer agent writes Python for the task, and a tester agent reads that code and returns comments (a bug, a missing case). The tester does not run the code yet — execution is Day 34.
2. Let the agents exchange two rounds: the programmer fixes the code from the tester's comments.

---

## Day 34: Sandboxing and Safe Code Execution

### 1. Introduction and Concepts

Letting an agent run arbitrary Python on your machine is a serious risk (prompt injection, `os.system("rm -rf /")`).

* **Executors:** Run LLM-generated code only inside an isolated Docker container or a micro-VM (the PyPI package `docker`, formerly `docker-py`, or a WASM runtime).

### 2. Tasks for today

1. Install the Docker library: `uv add docker`.
2. Write a Python runner that takes code from the LLM, starts a temporary network-less container (`python:3.12-slim`), captures `stdout` / `stderr`, and returns the result to the agent.
3. Attach this runner as a tool of the tester agent from Day 33. The tester's comments should come from `stdout` / `stderr`, not only from reading the source.

---

## Day 35: Week 5 Review

You now have a working, sandboxed agent that can call tools, keep memory, and run on a local model.

---
