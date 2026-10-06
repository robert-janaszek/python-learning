import json
from typing import Any, Awaitable, Callable, Mapping

from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam

type Tool = Callable[..., Awaitable[Any]]

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
