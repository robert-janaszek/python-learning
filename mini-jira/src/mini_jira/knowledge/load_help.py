
import asyncio
import dataclasses
from pathlib import Path
from typing import Any, cast

import lancedb
from mini_jira.lance_models import HelpChunksModel
from mini_jira.llm_client import get_embedding

db = lancedb.connect("./.lancedb")

def find_chunk_break_position(string: str, last: bool = False) -> int:
    search = string.rfind if last else string.find

    for char in ("\n", ".", " "):
        position = search(char)
        if position != -1:
            return position

    return -1

def chunk_text(text: str) -> list[str]:
    chunk_size = 500
    break_search_length = 210

    chunks: list[str] = []

    start = 0

    while start < len(text):
        if start + chunk_size >= len(text):
            chunks.append(text[start:])
            break

        nominal = start + chunk_size
        window = text[nominal:nominal + break_search_length]
        rel = find_chunk_break_position(window)

        if rel >= 0:
            cut = nominal + rel
            chunk_end = cut + 1
        else:
            cut = nominal
            chunk_end = cut

        chunks.append(text[start:chunk_end])

        if cut >= len(text) - 1:
            break

        rel = find_chunk_break_position(text[start:cut], last=True)
        next_start = start + rel + 1 if rel >= 0 else cut + 1

        if next_start <= start:
            next_start = cut + 1

        start = next_start

    return chunks

async def load_help():
    table_name = HelpChunksModel.__tablename__
    existing = db.list_tables().tables or []
    if table_name in existing:
        table = db.open_table(table_name)  # pyright: ignore[reportUnknownMemberType]
        print(f"Table {table_name} already exists ({table.count_rows()} rows). Skipping load.")
        return

    help_text = (Path(__file__).parent / "help.txt").read_text()

    chunks = chunk_text(help_text)

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
