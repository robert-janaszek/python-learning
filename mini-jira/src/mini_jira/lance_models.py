import asyncio
from dataclasses import dataclass
import dataclasses
from typing import Any, cast
import lancedb

from mini_jira.knowledge import sentences
from mini_jira.llm_client import get_embedding

db = lancedb.connect("./.lancedb")

@dataclass
class NotesModel:
    vector: list[float]
    text: str


async def load_notes():
    data: list[NotesModel] = []
    for sentence in sentences:
        embedding = await get_embedding(sentence)
        data.append(NotesModel(text=sentence, vector=embedding))
    
    table = db.create_table( # pyright: ignore[reportUnknownMemberType]
        "notes",
        data=[dataclasses.asdict(d) for d in data],
    )

    print(f"Successfully loaded {len(data)} embeddings")

    # sanity test
    query = "what values can a task priority take"
    query_embedding = await get_embedding(query)
    
    results = cast(
        list[dict[str, Any]],
        table.search(query_embedding).limit(1).to_list(),  # pyright: ignore[reportUnknownMemberType]
    )
    print(results[0]["text"])


if __name__ == "__main__":
    asyncio.run(load_notes())