from typing import Any, cast
import numpy as np

import lancedb
from mini_jira.lance_models import HelpChunksModel
from mini_jira.llm_client import client, get_embedding
from sentence_transformers import CrossEncoder

from mini_jira.qa.schemas import QaResponse


db = lancedb.connect("./.lancedb")

def sort_by_cross_encoder(question: str, chunks: list[str]) -> list[str]:
    model = CrossEncoder(
        'cross-encoder/ms-marco-MiniLM-L6-v2',
        local_files_only=True,
    )

    scores = model.predict([(question, chunk) for chunk in chunks])  # pyright: ignore[reportUnknownMemberType]

    chunks_scored: list[tuple[str, np.float32]] = []

    for i in range(len(scores)):
        chunks_scored.append((chunks[i], scores[i]))
    
    chunks_scored.sort(reverse=True, key=lambda pair: pair[1])

    # for rank, (text, score) in enumerate(chunks_scored, start=1):
    #     print(f"{rank}. {float(score):.3f}\n{text}\n")

    return [text for text, _score in chunks_scored]


async def answer_question(question: str) -> QaResponse:
    question_embedding = await get_embedding(question)
    chunks_table = db.open_table(HelpChunksModel.__tablename__)
    embedding_search = cast(
        list[dict[str, Any]],
        chunks_table.search(question_embedding).limit(8).to_list(),  # pyright: ignore[reportUnknownMemberType]
    )
    chunks_found: list[str] = [chunk["text"] for chunk in embedding_search]
    sorted_chunks = sort_by_cross_encoder(question, chunks_found)
    top_chunks = sorted_chunks[:3]

    punctuated_chunks = ["\n* " + chunk for chunk in top_chunks]
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

    return QaResponse(answer=content, quotes=top_chunks)
