# Week 5: Agentic Architecture and Tool Calling

This week you turn the local model from a chatbot into an **autonomous agent** that can use your code: query databases, call APIs, run scripts, and decide what to do next inside a loop. Keep working in the `mini-jira` directory from Week 2.

---

## Day 29: Native Tool Calling (Function Calling) with a Local LLM

### 1. Introduction and Concepts

Modern LLMs can return a JSON object that means: *"I cannot answer this from my own knowledge — please run `get_weather(city='Warsaw')` and give me the result."*

* **Tool definition:** A separate JSON schema. The model sees only that schema: the name, the description, and the parameters. The Python function stays in your code. The `name` field links the two.

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

response = await client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": "What is the balance of user 7?"}],
    tools=tools,
)

import json

tool_call = response.choices[0].message.tool_calls[0]
name = tool_call.function.name
arguments = json.loads(tool_call.function.arguments)

if name == "get_user_balance":
    result = get_user_balance(**arguments)

```

The client receives the list of schemas in the `tools` argument. It does not receive the function. When the model wants a tool, the response contains `tool_calls` instead of ordinary text. You choose the function by `name`, read the arguments from the JSON, call the function yourself, and on the next turn send the result back as a message with `role="tool"`.

### 2. Tasks for today

1. Write two functions in `mini_jira/agent.py` that use the existing `app.db` (`ProjectModel` and `TaskModel`):

   * `list_projects() -> list[dict]` — `id` and `name` of each project. The name is not unique, so `name` alone does not identify a row.
   * `create_task(project_id: int, title: str, priority: Literal["low", "medium", "high"]) -> str` — adds a task to the project with that `id`. It returns a sentence: the task was created with the given `id`, or a description of the error, such as no project with that `id` or a priority outside `low`, `medium`, and `high`. The task `id` alone does not say whether the write succeeded.
2. One sentence drives the loop: "Add a task «Fix login» with priority critical to the Backend project." The model turns the name "Backend" into an `id` through `list_projects`, and `create_task` receives that `project_id`. `critical` is deliberately outside `low`, `medium`, and `high`. The model has to handle that ambiguity: ask, refuse, or pick an allowed value. Send the sentence and both function schemas to the local model, run the `tool_calls` in Python, send the tool result back, and print the assistant's final answer. If a task is created, the database must contain the title from the instruction and a priority from the allowed set.



---

## Day 30: An Agent Loop from Scratch (ReAct Pattern)

### 1. Introduction and Concepts

**ReAct (Reason + Act)** is a loop. The agent repeats `while` it still has work to do:

1. **Thought:** The agent looks at the problem and plans the next step.
2. **Action:** The agent chooses a tool to call.
3. **Observation:** The agent receives the tool result.
4. It repeats until it can give a **final answer**.

### 2. Tasks for today

1. In the same `agent.py`, a `while` loop, with no LangGraph or other framework.
2. Before the run, the script inserts a project named "Backend" with three tasks when they are missing: two open tasks with priority high ("Fix login", "Deploy failed") and one completed low task ("README blurb"). The agent gets one instruction: "Find the Backend project, count its open tasks, and say how many of them have priority high." It reaches the answer through three functions:

   * `find_project(name: str) -> int | str` — returns the `id` when exactly one project has that name. When none match, or more than one does, it returns an error description.
   * `list_tasks(project_id: int, status: Literal["open", "completed", "all"] = "all") -> str` — a JSON string with title, priority, and `is_completed`. The `status` argument selects open, completed, or all tasks. When the project is missing, it returns an error description. The model receives that string, not a list of objects.
   * `count_by_priority(project_id: int, status: Literal["open", "completed", "all"] = "all") -> dict[str, int]` — counts of low, medium, and high among tasks with the given `status`.

   For this instruction both calls use `status="open"`. The answer means: two open tasks, both high.
3. After 5 iterations the loop stops and returns a message that the step limit was reached.

---

## Day 31: Agent Memory (History in the SQL Database)

### 1. Introduction and Concepts

An agent with no memory forgets the conversation on every HTTP request. Store the transcript in SQLite (`app.db` from Week 2), through SQLAlchemy 2.0. Redis stays with the ARQ queue, not with messages.

* Session rows (`session_id`, roles `system`, `user`, `assistant`, `tool`) live in a table.
* The prompt only gets a window: the newest messages, or a summary of older ones once the whole history passes N tokens.

### 2. Tasks for today

1. An Alembic migration adds table `agent_messages` with columns `id`, `session_id` (str), `role` (`system`, `user`, `assistant`, `tool`), `content`, and `created_at`. The Day 30 agent writes every turn there and loads the rows for that `session_id` on startup. Two runs share one `session_id`. The first is the Day 30 instruction. The second drops the project name: "And how many of them were high?". The second reaches "two" from the history in `app.db`.
2. Window: once the history text passes about 2000 characters (four of the ~500-character chunks from Day 25), the oldest turns go to the local model for a summary. Store the summary in the same table as a `role=system` row whose content starts with "Summary:". The next prompt receives the summary and the turns that remain.

---

## Day 32: LangGraph (Agent Framework)

### 1. Introduction and Concepts

Hand-rolled decision graphs get painful. **LangGraph** is the current Python default for multi-agent systems built as cyclic directed graphs (state graphs).

* **State:** One shared state object (usually a `TypedDict` or a Pydantic model) passed through every node.
* **Nodes:** Python functions (or LLM calls) that update that state.
* **Edges:** Conditional transitions chosen from the model's decision.

### 2. Tasks for today

1. Install LangGraph: `uv add langgraph`.
2. A two-node graph whose state has `plan: str` and `answer: str`. Node `plan` asks the local model which Day 30 function to call first for "Find the Backend project and report the number of open high-priority tasks." Node `execute` runs that function on `app.db` and writes `answer`.
3. The same `base_url` as Day 22. Run the graph and print `answer`. The answer means two.

---

## Day 33: Multi-Agent Collaboration

### 1. Introduction and Concepts

Instead of one agent that does everything, use small specialized roles:

* **Researcher:** Searches documents or the database.
* **Writer:** Turns the findings into a readable answer.
* **Critic / reviewer:** Checks the answer before it goes to the user.

### 2. Tasks for today

1. Two calls to the local model, with no code execution yet. The programmer receives a spec: `open_high_tasks(tasks: list[dict]) -> list[str]` returns titles where `priority` is `high` and `is_completed` is false. The tester reads the code and returns comments: a wrong condition, a missing field, or a change to the input.
2. Second turn: the programmer receives those comments and returns fixed code. Keep both versions in variables and print the tester's comments. Running the code is Day 34.

---

## Day 34: Sandboxing and Safe Code Execution

### 1. Introduction and Concepts

Letting an agent run arbitrary Python on your machine is a serious risk (prompt injection, `os.system("rm -rf /")`).

* **Executors:** Run LLM-generated code only inside an isolated Docker container or a micro-VM (the PyPI package `docker`, formerly `docker-py`, or a WASM runtime).

### 2. Tasks for today

1. Install the Docker library: `uv add docker`.
2. The runner takes the model's code and starts a temporary `python:3.12-slim` container with no network and a 10-second limit. The container is removed after the run. The runner appends a call to `open_high_tasks` on three dicts: open high "Fix login", completed high "Old bug", open low "Blurb". It returns `stdout` and `stderr`.
3. The Day 33 tester calls this runner. A comment must quote `stdout` or `stderr`. The case to see: a function that also returns completed high tasks — `stdout` contains "Old bug", and the tester reports that.

---

## Day 35: Week 5 Review

Check the agent against the Backend project data from Day 30:

1. The instruction about open high-priority tasks ends with the number two, and `app.db` shows a trace of the tool calls.
2. A second question in the same session ("And how many of them were high?") uses `agent_messages`.
3. The tester runs `open_high_tasks` in a container, and the comment cites `stdout`.

---
