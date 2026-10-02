import lancedb

db = lancedb.connect("./.lancedb")
print(f'Tables: {db.list_tables().tables}')

notes_table = db.open_table("notes")
print(f"notes table ({notes_table.count_rows()} rows)")
help_table = db.open_table("help_chunks")
print(f"help_chunks table ({help_table.count_rows()} rows)")

# print(help_table.schema)
# print(help_table.to_arrow().select(["text"]))