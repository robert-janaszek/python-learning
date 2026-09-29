from mini_jira.llm_client import stream_response


class ChatService:
    async def chat(self, prompt: str):
        response = await stream_response(prompt)
        async for chunk in response:
            content = chunk.choices[0].delta.content or ""
            if content:
                yield content

