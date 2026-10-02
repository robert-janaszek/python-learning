
import asyncio
import dataclasses
from pathlib import Path
from typing import Any, cast

import lancedb
from mini_jira.lance_models import HelpChunksModel
from mini_jira.llm_client import get_embedding

db = lancedb.connect("./.lancedb")

async def load_help():
    table_name = HelpChunksModel.__tablename__
    existing = db.list_tables().tables or []
    if table_name in existing:
        table = db.open_table(table_name)  # pyright: ignore[reportUnknownMemberType]
        print(f"Table {table_name} already exists ({table.count_rows()} rows). Skipping load.")
        return

    help_text = (Path(__file__).parent / "help.txt").read_text()

    chunk_size = 500
    overlap = 50
    stride = chunk_size - overlap

    chunks = [help_text[i:i + chunk_size] for i in range(0, len(help_text), stride)]

    data: list[HelpChunksModel] = []
    for chunk in chunks:
        embedding = await get_embedding(chunk)
        data.append(HelpChunksModel(text=chunk, vector=embedding))
    
    table = db.create_table( # pyright: ignore[reportUnknownMemberType]
        HelpChunksModel.__tablename__,
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
    asyncio.run(load_help())
