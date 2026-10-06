from collections.abc import Mapping
import json
from typing import Any, Awaitable, Callable, cast

from fastapi import status
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam, ChatCompletionToolUnionParam

from mini_jira.agent_messages.service import AgentMessagesService
from mini_jira.exception import DomainException
from mini_jira.llm_client import client
from mini_jira.project.service import ProjectService
from mini_jira.project.tools import make_find_project, make_list_projects
from mini_jira.task.service import TaskService
from mini_jira.task.tools import make_count_by_priority, make_create_task, make_list_tasks

type Tool = Callable[..., Awaitable[Any]]

async def call_llm_agent(
    messages: list[ChatCompletionMessageParam],
    tools: list[ChatCompletionToolUnionParam]
) -> ChatCompletionMessage:
    response = await client.chat.completions.create(
        model="qwen/qwen3.6-35b-a3b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant for mini-jira. "
                    "Use the provided tools to read and change projects and tasks. "
                    "Answer from the tool results. "
                    "If a tool does not return the data, say so."
                ),
            },
            *messages,
        ],
        tools=tools
    )

    return response.choices[0].message

async def run_tool(name: str, arguments: Any, tools_by_name: Mapping[str, Tool]) -> str:
    tool = tools_by_name.get(name)
    if tool is None:
        return json.dumps({"error": f"unknown tool {name}"})

    result = await tool(**arguments)
    if isinstance(result, str):
        return result
    return json.dumps(result)

async def handle_tool_call(
    response_message: ChatCompletionMessage,
    tools_by_name: Mapping[str, Tool]
) -> list[ChatCompletionMessageParam]:
    messages: list[ChatCompletionMessageParam] = []

    if not response_message.tool_calls:
        return messages
    
    messages.append({
        "role": "assistant",
        "tool_calls": [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in response_message.tool_calls
            if tool_call.type == "function"
        ],
    })
    for tool_call in response_message.tool_calls:
        if tool_call.type != "function":
            continue
        
        name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        result = await run_tool(name, arguments, tools_by_name)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })
    
    return messages

async def run_agentic_loop(
    session_id: str,
    project_service: ProjectService,
    task_service: TaskService,
    agent_message_service: AgentMessagesService,
) -> str:
    list_projects, list_projects_tool = make_list_projects(project_service)
    find_project, find_project_tool = make_find_project(project_service)
    create_task, create_task_tool = make_create_task(task_service, project_service)
    list_tasks, list_tasks_tool = make_list_tasks(task_service, project_service)
    count_by_priority, count_by_priority_tool = make_count_by_priority(task_service, project_service)

    tools_by_name: Mapping[str, Tool] = {
        "list_projects": list_projects,
        "create_task": create_task,
        "list_tasks": list_tasks,
        "count_by_priority": count_by_priority,
        "find_project": find_project,
    }
   
    agent_messages = await agent_message_service.get_messages(session_id)
    messages: list[ChatCompletionMessageParam] = [
        cast(
            ChatCompletionMessageParam,
            { "content": message.content, "role": message.role },
        )
        for message in agent_messages
    ]

    message_queued = True
    iterations = 0

    while message_queued:
        iterations += 1
        if iterations > 5:
                raise DomainException(
                    message="The assistant exceeded the step limit",
                    code="ASSISTANT_STEP_LIMIT_EXCEEDED",
                    status_code=status.HTTP_502_BAD_GATEWAY,
                )
        message_queued = False
        response_message = await call_llm_agent(
            messages,
            [
                list_projects_tool,
                create_task_tool,
                list_tasks_tool,
                count_by_priority_tool,
                find_project_tool
            ]
        )

        if response_message.tool_calls:
            message_queued = True
            tool_messages = await handle_tool_call(response_message, tools_by_name)
            messages.extend(tool_messages)

        if not response_message.tool_calls and response_message.content and response_message.content.strip():
            return response_message.content.strip()

    raise DomainException(
        message="The assistant returned no answer",
        code="ASSISTANT_EMPTY_RESPONSE",
        status_code=status.HTTP_502_BAD_GATEWAY,
    )
