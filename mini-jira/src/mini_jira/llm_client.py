from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

async def stream_response(prompt: str):
    response = await client.chat.completions.create(
        model="qwen/qwen3.6-35b-a3b",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    return response


async def get_response(prompt: str):
    response = await client.chat.completions.create(
        model="qwen/qwen3.6-35b-a3b",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    return response