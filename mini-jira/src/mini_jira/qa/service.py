from typing import Any, cast

import lancedb
from mini_jira.lance_models import HelpChunksModel
from mini_jira.llm_client import client, get_embedding
from mini_jira.schemas import QaResponse

db = lancedb.connect("./.lancedb")

async def answer_question(question: str) -> QaResponse:
    question_embedding = await get_embedding(question)
    chunks_table = db.open_table(HelpChunksModel.__tablename__)
    embedding_search = cast(
        list[dict[str, Any]],
        chunks_table.search(question_embedding).limit(3).to_list(),  # pyright: ignore[reportUnknownMemberType]
    )

    chunks_found: list[str] = [chunk["text"] for chunk in embedding_search]
    punctuated_chunks = ["\n* " + chunk for chunk in chunks_found]
    chunks_concat = "".join(punctuated_chunks)

    response = await client.chat.completions.create(
        model="qwen/qwen3.6-35b-a3b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer the question using only the context in the next message. "
                    "The context is excerpts from the mini-jira help. "
                    "If the context does not contain the answer, say that the materials do not contain it. "
                    "Do not add facts from outside the context."
                ),
            },
            {"role": "user", "content": "# Context:\n" + chunks_concat},
            {"role": "user", "content": question},
        ],
    )

    content = response.choices[0].message.content or ""

    return QaResponse(answer=content, quotes=chunks_found)
