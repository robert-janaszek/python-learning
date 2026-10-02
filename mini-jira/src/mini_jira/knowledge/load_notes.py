import asyncio
import dataclasses
from typing import Any, cast
import lancedb

from mini_jira.knowledge.notes import notes
from mini_jira.lance_models import NotesModel
from mini_jira.llm_client import get_embedding

db = lancedb.connect("./.lancedb")

async def load_notes():
    table_name = "notes"
    existing = db.list_tables().tables or []
    if table_name in existing:
        table = db.open_table(table_name)  # pyright: ignore[reportUnknownMemberType]
        print(f"Table {table_name} already exists ({table.count_rows()} rows). Skipping load.")
        return

    data: list[NotesModel] = []
    for note in notes:
        embedding = await get_embedding(note)
        data.append(NotesModel(text=note, vector=embedding))
    
    table = db.create_table( # pyright: ignore[reportUnknownMemberType]
        table_name,
        data=[dataclasses.asdict(d) for d in data],
    )

    print(f"Successfully loaded {len(data)} embeddings")

    # sanity test
    query = "what groups related tasks"
    query_embedding = await get_embedding(query)
    
    results = cast(
        list[dict[str, Any]],
        table.search(query_embedding).limit(1).to_list(),  # pyright: ignore[reportUnknownMemberType]
    )
    print(results[0]["text"])


if __name__ == "__main__":
    asyncio.run(load_notes())
