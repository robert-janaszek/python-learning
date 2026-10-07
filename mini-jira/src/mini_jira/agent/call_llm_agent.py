from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam, ChatCompletionToolUnionParam
from mini_jira.llm_client import client


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

async def call_compaction_agent(
    messages: list[ChatCompletionMessageParam]
):
    response = await client.chat.completions.create(
        model="qwen/qwen3.6-35b-a3b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You summarize older mini-jira conversation turns. "
                    "The messages are history, not a new request. "
                    "Do not call tools and do not answer the user. "
                    "Keep project names, task counts, priorities, and decisions. "
                    "Leave out greetings and repeated details. "
                    "Reply with only the summary, starting with \"Summary:\"."
                ),
            },
            *messages,
        ],
    )

    return response.choices[0].message
