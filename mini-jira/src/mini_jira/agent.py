import asyncio
from collections.abc import Mapping
import json
from typing import Any, Awaitable, Callable

from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam, ChatCompletionToolUnionParam

from mini_jira.database import AsyncSessionLocal
from mini_jira.dependencies import get_project_repository, get_project_service, get_task_repository, get_task_service
from mini_jira.llm_client import client
from mini_jira.project.tools import make_list_projects
from mini_jira.task.tools import make_create_task

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
    return json.dumps(await tool(**arguments))

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

async def run_agentic_loop():
    async with AsyncSessionLocal() as session:
        project_repository = get_project_repository(session)
        task_repository = get_task_repository(session)
        project_service = get_project_service(project_repository, session)
        task_service = get_task_service(task_repository, project_repository, session)
        list_projects, list_projects_tool = make_list_projects(project_service)
        create_task, create_task_tool = make_create_task(task_service, project_service)

        tools_by_name: Mapping[str, Tool] = {
            "list_projects": list_projects,
            "create_task": create_task,
        }

        message_queued = True
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "user",
                "content": "Create task `fix login` in Backend project with critical priority"
            }
        ]

        while message_queued:
            message_queued = False
            response_message = await call_llm_agent(
                messages,
                [list_projects_tool, create_task_tool]
            )

            if response_message.tool_calls:
                message_queued = True
                tool_messages = await handle_tool_call(response_message, tools_by_name)
                messages.extend(tool_messages)
                
            if response_message.content:
                print(response_message.content)


if __name__ == "__main__":
    asyncio.run(run_agentic_loop())
