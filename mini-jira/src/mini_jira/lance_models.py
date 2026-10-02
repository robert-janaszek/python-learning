from dataclasses import dataclass

@dataclass
class NotesModel:
    vector: list[float]
    text: str


@dataclass
class HelpChunksModel:
    __tablename__ = "help_chunks"
    vector: list[float]
    text: str
