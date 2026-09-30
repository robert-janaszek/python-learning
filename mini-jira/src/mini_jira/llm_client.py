import instructor
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

structured_client = instructor.from_openai(
    client,
    mode=instructor.Mode.JSON_SCHEMA
)

async def stream_response(prompt: str):
    response = await client.chat.completions.create(
        model="qwen/qwen3.6-35b-a3b",
        messages=[{"role": "user", "content": prompt}],
        extra_body={"reasoning": "off"},
        stream=True,
    )

    return response


async def get_response(prompt: str):
    response = await client.chat.completions.create(
        model="qwen/qwen3.6-35b-a3b",
        messages=[{"role": "user", "content": prompt}],
        extra_body={"reasoning": "off"},
        stream=False,
    )
    return response